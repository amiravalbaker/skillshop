from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)   
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    is_provider =models.BooleanField(default=False)
    profile_image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return self.user.username

    def display_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.user.username     

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name
    
class Location(models.Model):
    name = models.CharField(max_length=120)   # e.g. "London", "SW1A 1AA"
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = ("latitude", "longitude", "name")

    def __str__(self):
        return self.name

class Listing(models.Model):
    provider = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="listings")
    skill = models.ForeignKey(Skill, on_delete=models.PROTECT, related_name="listings")
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)
    photo = CloudinaryField("image", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.skill.name} ({self.provider.user.username})"
    
