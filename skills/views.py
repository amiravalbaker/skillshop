from django.shortcuts import render, redirect
from django.http import HttpResponse 
from .forms import ProfileForm, SignUpForm, ListingForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from geopy.geocoders import Nominatim
from .models import  Listing, Location

# Create your views here.
def index(request): return HttpResponse("Hello, World!")

def home(request):
    listings = Listing.objects.select_related("skill", "provider", "provider__user").filter(is_active=True)
    return render(request, "skills/home.html", {"listings": listings})

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
    profile = request.user.profile
    return render(request, "skills/profile.html", {
        "profile": request.user.profile
    })

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
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
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            location_text = form.cleaned_data["location_text"]
            geolocator = Nominatim(user_agent="skillshop")
            geo = geolocator.geocode(location_text)

            if not geo:
                form.add_error("location_text", "Could not find that location. Try a postcode or full town/city name.")
            else:
                loc_obj, _ = Location.objects.get_or_create(
                    name=location_text.strip(),
                    defaults={"latitude": geo.latitude, "longitude": geo.longitude}
            )
            listing.location = loc_obj
            listing.provider = profile
            listing.save()
            return redirect("home")
    else:
        form = ListingForm()

    return render(request, "skills/create_listing.html", {"form": form})