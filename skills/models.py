from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cloudinary.models import CloudinaryField
from django.core.validators import MinValueValidator, MaxValueValidator

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
    # Up to 3 photos for each listing
    photo_1 = CloudinaryField("First image", blank=True, null=True)
    photo_2 = CloudinaryField("Second image", blank=True, null=True)
    photo_3 = CloudinaryField("Third image", blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.skill.name} ({self.provider.user.username})"

    def get_photos(self):
        """Returns a list of populated photo fields."""
        photos = [self.photo_1, self.photo_2, self.photo_3]
        return [p for p in photos if p]

class Review(models.Model):
    listing = models.ForeignKey("Listing", on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey("Profile", on_delete=models.CASCADE, related_name="reviews_written")

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("listing", "reviewer")  # one review per user per listing
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.rating}/5 by {self.reviewer.user.username} on {self.listing_id}"

class Conversation(models.Model):
    """
    One conversation between two Profiles (participants), optionally about a Listing.
    """
    participants = models.ManyToManyField(
        "Profile",
        related_name="conversations"
    )

    # Link the conversation to a listing
    listing = models.ForeignKey(
        "Listing",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # bump when new messages arrive

    def __str__(self):
        return f"Conversation {self.id}"

    def other_participant(self, profile):
        """Return the other participant (useful in templates)."""
        return self.participants.exclude(id=profile.id).first()


class Message(models.Model):
    """
    A single message inside a conversation.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        "Profile",
        on_delete=models.CASCADE,
        related_name="messages_sent"
    )

    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Optional: read receipts
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["sender", "created_at"]),
        ]

    def __str__(self):
        return f"Msg {self.id} in Conv {self.conversation_id}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Conversation.objects.filter(id=self.conversation_id).update(updated_at=timezone.now())
