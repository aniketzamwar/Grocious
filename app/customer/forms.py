from mongodbforms import DocumentForm, EmbeddedDocumentForm
from django.forms.extras.widgets import SelectDateWidget
from app.models import UserProfile, Address, Order, Payment, Delivery
from app.models import CITY_CHOICES, STATE_CHOICES, COUNTRY_CHOICES, GENDER_CHOICES
from django import forms

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
    line2   = forms.CharField(widget=forms.TextInput)
    city    = forms.ChoiceField(widget=forms.Select, choices=CITY_CHOICES, required=True)
    state   = forms.ChoiceField(widget=forms.Select, choices=STATE_CHOICES, required=True)
    country = forms.ChoiceField(widget=forms.Select, choices=COUNTRY_CHOICES, required=True)
    pincode = forms.CharField(widget=forms.TextInput, required=True)

    class Meta:
        document=Address
        embedded_field_name = 'address'
        fields=['line1', 'line2', 'city', 'state', 'country', 'pincode',]

#class ActivityForm(EmbeddedDocumentForm):

class OrderForm(DocumentForm):

    class Meta:
        document=Order
        fields=['customer_id', 'order_total_amount', 'order_cart_amount', 'ordered_items', 'delivery_info', 'payment_info', ]

    def save(self, items, commit):
        order = super(OrderForm, self).save(commit=False)
        dbOrder = order.save(commit=commit)
        for item in items:
            print "item", item.to_mongo()
            dbOrder.ordered_items.append(item)
        return dbOrder

class DeliveryForm(EmbeddedDocumentForm):

    class Meta:
        document = Delivery
        embedded_field_name = 'delivery_info'
        fields = ['option', 'price','fname', 'lname', 'line1', 'line2', 'city', 'state', 'country', 'pincode', ]

class PaymentForm(EmbeddedDocumentForm):
    class Meta:
        document = Payment
        embedded_field_name = 'payment_info'
        fields = ['option', 'amount', 'trans_id', 'card_digits',]
