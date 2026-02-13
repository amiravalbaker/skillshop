from django.shortcuts import render, redirect
from django.http import HttpResponse 
from .forms import SignUpForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request): return HttpResponse("Hello, World!")

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
def home(request):
    return render(request, "skills/home.html")

