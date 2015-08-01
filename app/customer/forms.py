from mongodbforms import DocumentForm, EmbeddedDocumentForm, documentform_factory
from mongoengine.django.auth import User
from django.utils.translation import gettext as _
from django.forms.extras.widgets import SelectDateWidget
from app.models import *
from django import forms
from mongoengine import *
import datetime

class LoginForm(forms.Form):
    username    = forms.CharField(max_length = 25, required = True, label = "Username:")
    password    = forms.CharField(max_length = 32, required = True, label = "Password:", widget = forms.PasswordInput)

class UserProfileForm(DocumentForm):

    BIRTH_YEAR_CHOICES = range(1940, 2005)

    first_name = forms.CharField(widget=forms.TextInput, required=True)
    last_name  = forms.CharField(widget=forms.TextInput, required=True)
    password   = forms.CharField(widget=forms.PasswordInput, required=True)
    email      = forms.EmailField(required=True)
    username   = forms.CharField(widget=forms.TextInput, required=True)
    dob        = forms.DateField(widget=SelectDateWidget(years=BIRTH_YEAR_CHOICES), required=True)
    gender     = forms.ChoiceField(widget=forms.Select, choices=GENDER_CHOICES, required=True)

    class Meta:
        document=UserProfile
        fields=['first_name', 'last_name', 'password', 'email', 'username', 'mobile', 'gender', 'dob', 'address', ]


    def save(self, commit):
        user = super(UserProfileForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.mobile = self.cleaned_data['mobile']
        user.gender = self.cleaned_data['gender']
        user.dob =  self.cleaned_data['dob']
        dbUser = user.save(commit=commit)
        return dbUser


class AddressForm(EmbeddedDocumentForm):
    line1   = forms.CharField(widget=forms.TextInput, required=True)
    line2   = forms.CharField(widget=forms.TextInput, required=True)
    city    = forms.ChoiceField(widget=forms.Select, choices=CITY_CHOICES, required=True)
    state   = forms.ChoiceField(widget=forms.Select, choices=STATE_CHOICES, required=True)
    country = forms.ChoiceField(widget=forms.Select, choices=COUNTRY_CHOICES, required=True)
    pincode = forms.CharField(widget=forms.TextInput, required=True)

    class Meta:
        document=Address
        embedded_field_name = 'address'
        fields=['line1', 'line2', 'city', 'state', 'country', 'pincode',]

#class ActivityForm(EmbeddedDocumentForm):
