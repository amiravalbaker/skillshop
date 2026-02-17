from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Listing, Skill


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name","bio", "is_provider"]

NEW_SKILL_VALUE = "__new__"

class ListingForm(forms.ModelForm):
    location_text = forms.CharField(
        required=True,
        max_length=120,
        help_text="Enter a town/city or postcode"
    )
    skill_choice = forms.ChoiceField(label="Skill")
    new_skill = forms.CharField(label="New skill name",required=False, max_length=100,)
    
    class Meta:
        model = Listing
        fields = ["description", "price", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Build dropdown choices from Skill table + add "Other/New skill..."
        skill_choices = [(str(s.id), s.name) for s in Skill.objects.order_by("name")]
        skill_choices.append((NEW_SKILL_VALUE, "Other / New skill…"))
        self.fields["skill_choice"].choices = [("", "Select a skill…")] + skill_choices

        # If editing an existing listing, preselect its current skill
        if self.instance and getattr(self.instance, "pk", None):
            self.fields["skill_choice"].initial = str(self.instance.skill_id)
    
    def clean(self):
        cleaned = super().clean()
        chosen = cleaned.get("skill_choice")
        new_skill = (cleaned.get("new_skill") or "").strip()

        # Must pick existing OR type a new one
        if not chosen:            
            raise forms.ValidationError("Please select a skill")

        if chosen == NEW_SKILL_VALUE:
            if not new_skill:
                raise forms.ValidationError("Please type the new skill name.")
        else:
            # If they picked an existing skill, ignore any typed new_skill
            cleaned["new_skill"] = ""

        return cleaned
    
    def save(self, commit=True):
        listing = super().save(commit=False)
        
        chosen = self.cleaned_data["skill_choice"]
        new_skill = (self.cleaned_data.get("new_skill") or "").strip()

        if chosen == NEW_SKILL_VALUE:
            # Create or reuse skill (case-insensitive)
            skill_obj = Skill.objects.filter(name__iexact=new_skill).first()
            if not skill_obj:
                skill_obj = Skill.objects.create(name=new_skill)
            listing.skill = skill_obj
        else:
            listing.skill_id = int(chosen)

        if commit:
            listing.save()
            self.save_m2m()

        return listing