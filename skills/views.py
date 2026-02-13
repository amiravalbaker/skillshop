from django.shortcuts import render, redirect
from django.http import HttpResponse 
from .forms import ProfileForm, SignUpForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request): return HttpResponse("Hello, World!")

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
