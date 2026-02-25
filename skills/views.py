from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from geopy.geocoders import Nominatim
from geopy.distance import geodesic 
from .models import  Profile, Listing, Location, Skill, Review, Conversation, Message
from .forms import ProfileForm, SignUpForm, ListingForm, ReviewForm, MessageForm

# Create your views here.

def home(request):
    return render(request, "skills/home.html")
   

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = SignUpForm()

    return render(request, "skills/signup.html", {"form": form})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    # Fetch listings using the related_name you defined
    my_listings = profile.listings.all().select_related("skill", "location")
    conversations = Conversation.objects.filter(participants=profile).select_related("listing", "listing__skill").prefetch_related("participants", "messages").order_by("-updated_at")
    
 # Build a light “inbox” list with last message (avoids template query surprises)
    inbox = []
    for c in conversations:
        other = c.other_participant(profile)
        last_msg = c.messages.order_by("-created_at").first()
        inbox.append((c, other, last_msg))
      
    return render(request, "skills/profile.html", {
        "profile": profile,
        "inbox": inbox,
        "listings": my_listings,
    })


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "skills/edit_profile.html", {
        "form": form
    })


@login_required
def create_listing(request):
    profile = request.user.profile

    # Only providers can create listings
    if not profile.is_provider:
        # Either raise PermissionDenied OR redirect to profile edit
        return redirect("edit_profile")

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)

            location_text = form.cleaned_data["location_text"].strip()
            geo= Nominatim(user_agent="skillshop").geocode(location_text)

            if not geo:
                form.add_error("location_text", "Could not find that location. Try a postcode or full town/city name.")
            else:
                loc_obj, _ = Location.objects.get_or_create(
                    name=location_text,
                    defaults={"latitude": geo.latitude, "longitude": geo.longitude}
                )
                listing.location = loc_obj
                listing.provider = profile
                listing.save()
                messages.success(request, f"Success! Your listing '{listing.skill.name}' has been published.")
                return redirect("home")
    else:
        form = ListingForm()

    return render(request, "skills/create_listing.html", {"form": form})


def search(request):

    listings = Listing.objects.select_related("skill", "provider", "provider__user", "location").filter(is_active=True).annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
    form = ListingForm(request.GET, search_mode=True)  # Pass search_mode=True to the form to adjust its behavior
    #skill_q = request.GET.get("skill", "").strip()
    skill_q = request.GET.get("skill_choice") or request.GET.get("skill")

    location_q = request.GET.get("location", "").strip()

    # miles (default 15)
    radius_miles = request.GET.get("radius", "15").strip()

    # Optional browser coords
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if skill_q:
        listings = listings.filter(skill_id=skill_q)
    
    try: r_miles = float(radius_miles) 
    except ValueError: r_miles = 15.0
    
    # Determine user coords
    user_coords = None
    location_error = None

    # Determine whether the user attempted location filtering at all
    #attempted_location_filter = bool(location_q) or (lat and lon)

    # Browser coordinates if present
    if lat and lon:
        try:
            user_coords = (float(lat), float(lon))
        except ValueError:
            location_error = "Could not read your browser location."
    
     # OFallback: geocode typed location
    if not user_coords and location_q:
        geolocator = Nominatim(user_agent="skillshop")
        geo = geolocator.geocode(location_q)
        if geo:
            user_coords = (geo.latitude, geo.longitude)
        else:
            location_error = "Could not find that location. Try a full postcode or town/city name."
    
    results=[]
    if user_coords:
        for listing in listings:
            if not listing.location:
                continue
            listing_coords = (listing.location.latitude, listing.location.longitude)
            d_miles = geodesic(user_coords, listing_coords).miles
            if d_miles <= r_miles:
                listing.avg_rating_int = int(listing.avg_rating or 0)
                results.append((listing, d_miles))
        results.sort(key=lambda x: x[1])
    else:
        # No location filtering, just show all results with avg_rating_int annotated for star display
        for listing in listings:
            listing.avg_rating_int = int(listing.avg_rating or 0)
            results.append((listing, None))  # No distance

    # Filter by distance (uses listing.location coords)
    return render(request, "skills/search.html", {
        "results": results,
        "skill_q": skill_q,
        "location_q": location_q,
        "radius_miles": radius_miles,
        "location_error": location_error,
        "form": form,
    })

@login_required
def edit_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    # Owner-only permission
    if listing.provider != request.user.profile:
        raise PermissionDenied

    # Pre-fill location_text from existing Location
    initial = {}
    if listing.location:
        initial["location_text"] = listing.location.name

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            updated = form.save(commit=False)
            messages.success(request, f'Your listing "{listing.skill.name}" has been updated!')
            return redirect('profile') 
        
            # Geocode and set location (same as create)
            location_text = form.cleaned_data.get("location_text", "").strip()
            geo = Nominatim(user_agent="skillshop").geocode(location_text)

            if not geo:
                form.add_error("location_text", "Could not find that location. Try a postcode or full town/city name.")
            else:
                loc_obj, _ = Location.objects.get_or_create(
                    name=location_text,
                    defaults={"latitude": geo.latitude, "longitude": geo.longitude},
                )
                updated.location = loc_obj
                updated.provider = listing.provider
                updated.save()
                return redirect("home")
    else:
        form = ListingForm(instance=listing, initial=initial)

    return render(request, "skills/edit_listing.html", {
        "form": form,
        "listing": listing,
    })

def listing_detail(request, listing_id):
    listing = get_object_or_404(
        Listing.objects.select_related("skill", "provider", "provider__user", "location"),
        id=listing_id,
        is_active=True
    )

# Aggregate rating stats for this listing
    rating_stats = listing.reviews.aggregate(avg=Avg("rating"), count=Count("id"))
    reviews = listing.reviews.select_related("reviewer", "reviewer__user").order_by("-created_at")
    
    avg_rating = rating_stats["avg"] or 0 
    avg_rating_int = int(avg_rating)

# Initialize Permission Variables
    review_form = None
    user_review = None
    can_review = False
    if request.user.is_authenticated:
        reviewer = request.user.profile
        # Don't allow provider to review their own listing
        if reviewer != listing.provider:
            # Allow review only if user has an existing conversation with provider
            has_replied = listing.conversations.filter(participants=reviewer).filter(messages__sender=listing.provider).exists()
            if has_replied:
                can_review = True
                # Check if they have already left a review
                user_review = Review.objects.filter(listing=listing, reviewer=reviewer).first()

#Handle form processing
        if can_review:

            if request.method == "POST":
                # If user_review exists, this updates it; otherwise, it creates a new one
                review_form = ReviewForm(request.POST, instance=user_review)
                if review_form.is_valid():
                    obj = review_form.save(commit=False)
                    obj.listing = listing
                    obj.reviewer = reviewer
                    obj.save()

                    msg = "Your review has been updated." if user_review else "Your review has been submitted."
                    messages.success(request, msg)
                    return redirect(f"{reverse('listing_detail', args=[listing.id])}#review-section")
            else:
                review_form = ReviewForm(instance=user_review)

    return render(request, "skills/listing_detail.html",{
        "listing": listing,
        "photos": listing.get_photos(),
        "reviews": reviews,
        "rating_stats": rating_stats,
        "avg_rating_int": avg_rating_int,
        "review_form": review_form,
        "user_review": user_review,   
        "can_review": can_review,                                                
    })

@login_required
def delete_review(request, review_id):
    # We use reviewer=request.user.profile as a security check
    review = get_object_or_404(Review, id=review_id, reviewer=request.user.profile)
    listing_id = review.listing.id
    review.delete()
    messages.success(request, "Review deleted successfully.")
    # Redirect back to the listing detail and scroll to the review header
    return redirect(f"{reverse('listing_detail', args=[listing_id])}#review-section")

@login_required
def start_conversation(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, is_active=True)

    me = request.user.profile
    other = listing.provider

    # Don't allow providers to start conversations on their own listings
    if other == me:
        raise PermissionDenied

    # Check if a conversation already exists between this user and the provider about this listing
    existing = listing.conversations.filter(participants=me).filter(participants=other).first()
    if existing:
        return redirect("conversation_detail", conversation_id=existing.id)

    # Create new conversation
    conv = listing.conversations.create()
    conv.participants.add(me)
    conv.participants.add(other)
    conv.save()

    return redirect("conversation_detail", conversation_id=conv.id)

@login_required
def conversation_detail(request, conversation_id):
    conv  = get_object_or_404(
        Conversation.objects.prefetch_related("participants", "messages__sender"),
        id=conversation_id
    )
    me= request.user.profile

    if me not in conv.participants.all():
        raise PermissionDenied

    messages_qs = conv.messages.select_related("sender", "sender__user").order_by("created_at")
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = conv
            msg.sender = me
            msg.save()
            return redirect("conversation_detail", conversation_id=conv.id)
    else:
        form = MessageForm()

    other = conv.other_participant(me)

    # Logic for the dynamic back link
    user_is_provider = False
    if conv.listing and conv.listing.provider == me:
        user_is_provider = True

    return render(request, "skills/conversation_detail.html", {
        "conversation": conv,
        "messages": messages_qs,  # oldest first
        "form": form,
        "other": other,
        "user_is_provider": user_is_provider, # Added this
    })
#delete listing view - provider only
@login_required
def delete_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, user=request.user)
    
    if request.method == 'POST':
        listing.delete()
        # You can add a 'success' message here later
        return redirect('profile')
    
    # If someone tries to access via a link (GET), send them back
    return redirect('profile')

@login_required
def delete_profile(request):
    user = request.user
    # Optional: Perform any specific cleanup here
    user.delete()
    messages.success(request, "Your account and all associated data have been deleted.")
    return redirect('home')