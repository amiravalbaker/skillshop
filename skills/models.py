from django.db import models
from django.contrib.auth.models import User
#from cloudinary.models import CloudinaryField

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)   
    bio = models.TextField(blank=True)
    is_provider =models.BooleanField(default=False)
    #profile_image = CloudinaryField('image',default='placeholder')

    def __str__(self):
        return self.user.username


#To create a user profile on sign-up we need to include:
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

