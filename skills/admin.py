from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Profile, Skill, Listing, Location


# Register your models here.
@admin.register(Profile)
class ProfileAdmin(SummernoteModelAdmin):
    summernote_fields = ("bio",)

@admin.register(Skill)
class SkillAdmin(SummernoteModelAdmin):
    summernote_fields = ("description",)

@admin.register(Listing) 
class ListingAdmin(SummernoteModelAdmin):
    summernote_fields = ("profile", "skill")

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass 