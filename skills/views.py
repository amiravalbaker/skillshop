from django.http import HttpResponse 
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
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
    })


@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
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
                return redirect("home")
    else:
        form = ListingForm()

    return render(request, "skills/create_listing.html", {"form": form})


def search(request):
    listings = Listing.objects.select_related("skill", "provider", "provider__user", "location").filter(is_active=True).annotate(avg_rating=Avg("reviews__rating"), review_count=Count("reviews"))
    
    skill_q = request.GET.get("skill", "").strip()
    location_q = request.GET.get("location", "").strip()

    # miles (default 15)
    radius_miles = request.GET.get("radius", "15").strip()

    # Optional browser coords
    lat = request.GET.get("lat")
    lon = request.GET.get("lon")

    if skill_q:
        listings = listings.filter(skill__name__icontains=skill_q)
    
    # Determine user coords
    user_coords = None
    location_error = None

    # Determine whether the user attempted location filtering at all
    attempted_location_filter = bool(location_q) or (lat and lon)

    # Prefer browser coordinates if present
    if lat and lon:
        try:
            user_coords = (float(lat), float(lon))
        except ValueError:
            user_coords = None
            location_error = "Could not read your browser location. Please type your postcode/town."
    
    
     # Otherwise geocode typed location (avoid "Current location ..." text)
    if user_coords is None and location_q:
        if location_q.lower().startswith("current location"):
            location_error = "Your browser location was unavailable. Please type your postcode/town."
        else:
            geo = Nominatim(user_agent="skillshop").geocode(location_q)
            if geo:
                user_coords = (geo.latitude, geo.longitude)
            else:
                location_error = "Could not find that location. Try a full postcode or town/city name."
    
     # Parse radius in miles
    try:
        r_miles = float(radius_miles) if radius_miles else 15.0
    except ValueError:
        r_miles = 15.0
    
    # If the user attempted location filtering but we couldn't get coords => show NO results
    if attempted_location_filter and user_coords is None:

    # Filter by distance (uses listing.location coords)
        return render(request, "skills/search.html", {
            "results": [],
            "skill_q": skill_q,
            "location_q": location_q,
            "radius_miles": radius_miles,
            "location_error": location_error or "Please enter a valid location.",
        })

    # Build results
    results = []
    if user_coords:
        for listing in listings:
            if not listing.location:
                continue
            listing_coords = (listing.location.latitude, listing.location.longitude)
            d_miles = geodesic(user_coords, listing_coords).miles
            if d_miles <= r_miles:
                results.append((listing, d_miles))
        results.sort(key=lambda x: x[1])
    else:
        # No location filter used => show all listings with no distance
        results = [(l, None) for l in listings]

    return render(request, "skills/search.html", {
        "results": results,
        "skill_q": skill_q,
        "location_q": location_q,
        "radius_miles": radius_miles,
        "location_error": location_error,
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
    reviews = listing.reviews.select_related("reviewer", "reviewer__user")
    
    avg_rating = rating_stats["avg"] or 0 
    avg_rating_int = int(avg_rating)

    review_form = None
    user_review = None
    can_review = False
    if request.user.is_authenticated:
        reviewer = request.user.profile
        # Don't allow provider to review their own listing
        if reviewer != listing.provider:
            # ✅ allow review only if user has an existing conversation with provider
            has_messaged = listing.conversations.filter(participants=reviewer,messages__isnull=False).exists()
            if has_messaged:
                can_review = True

        if can_review:
            user_review = Review.objects.filter(
                listing=listing,
                reviewer=reviewer
            ).first()

            if request.method == "POST":
                review_form = ReviewForm(request.POST, instance=user_review)
                if review_form.is_valid():
                    obj = review_form.save(commit=False)
                    obj.listing = listing
                    obj.reviewer = reviewer
                    obj.save()
                    return redirect("listing_detail", listing_id=listing.id)
            else:
                review_formform = ReviewForm(instance=user_review)

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
            msg.sender = request.user.profile
            msg.save()
            return redirect("conversation_detail", conversation_id=conv.id)
    else:
        form = MessageForm()

    other = conv.other_participant(me)

    return render(request, "skills/conversation_detail.html", {
        "conversation": conv,
        "messages": messages_qs,  # oldest first
        "form": form,
        "other": other,
    })