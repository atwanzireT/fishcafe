from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Setting(models.Model):
    hotel_name = models.CharField(max_length=255)
    about_description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    instagram = models.CharField(max_length=3060, blank=True, null=True)
    twitter = models.CharField(max_length=3060, blank=True, null=True)
    facebook = models.CharField(max_length=3060, blank=True, null=True)
    api_key = models.CharField(max_length=3060, blank=True, null=True)


    def clean(self):
        if Setting.objects.exists() and not self.pk:
            raise ValidationError("Only one setting instance is allowed.")

    def __str__(self):
        return f"Settings for {self.hotel_name}"
    
    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            # If there's an existing instance and we're trying to create a new one, raise an error
            raise ValidationError("There is already an instance of Settings. You can only update the existing one.")
        super(Setting, self).save(*args, **kwargs)



# Create your models here.
class Profile(models.Model):
    GENDER_CHOICE = (
        ("", "Select Gender"),
        ("male", "male"),
        ("female", "female"),
    )

    USERTYPE_CHOICE = (
        ("", "Select Gender"),
        ("admin", "admin"),
        ("reception", "reception"),
        ("kitchen", "kitchen"),
    )
    # add additional fields here'
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(_("Email Address"), unique=True, blank=True)
    about = models.TextField(default="No About ...")
    address = models.CharField(blank=True, null=True, max_length=100)
    nationality = models.CharField(blank=True, null=True, max_length=100)
    phonenumber = models.CharField(blank=True, max_length=50,help_text='Contact phone number')
    gender = models.CharField(choices=GENDER_CHOICE, max_length=30, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return self.user.username
    
