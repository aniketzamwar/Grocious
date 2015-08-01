from mongodbforms import DocumentForm, EmbeddedDocumentForm, documentform_factory
from app.models import *
from django import forms
import datetime

class MerchantForm(DocumentForm):
	merchant_name = forms.CharField(widget=forms.TextInput, required=True)
	contact_number = forms.CharField(widget=forms.TextInput, required=True)
	merchant_url = forms.URLField(widget=forms.URLInput)
	first_name = forms.CharField(widget=forms.TextInput, required=True)
	last_name  = forms.CharField(widget=forms.TextInput, required=True)
	password   = forms.CharField(widget=forms.PasswordInput, required=True)
	email      = forms.EmailField(required=True)
	username   = forms.CharField(widget=forms.TextInput, required=True)
	
	class Meta:
		document=Merchant
		fields=['merchant_name', 'contact_number', 'merchant_url', 'first_name', 'last_name', 'password', 'email', 'username', 'address',]


	def save(self, commit):
		'''
		'''
		print self.cleaned_data
		user = super(MerchantForm, self).save(commit=False)
		user.set_password(self.cleaned_data['password'])
		user.merchant_name = self.cleaned_data['merchant_name']
		user.contact_number = self.cleaned_data['contact_number']
		user.merchant_url =  self.cleaned_data['merchant_url']
		dbUser = user.save(commit=commit)
		return dbUser


class ProductForm(DocumentForm):
	'''
	'''

	@staticmethod
	def get_manufacturers():
		manufacturer_choices = []
		for manufacturer in Manufacturer.objects:
			m = [manufacturer.id, manufacturer.manufacturer_name]
			manufacturer_choices.append(m)
		return manufacturer_choices

	def __init__(self, *args, **kwargs):
		super(ProductForm, self).__init__(*args, **kwargs)
		self.fields['manufacturer_id'] = forms.ChoiceField(widget=forms.Select, choices=ProductForm.get_manufacturers(), label="Manufacturer")


	AVAILABILITY_CHOICES = ((True,'Available'), (False, 'Not Available'),)
	name = forms.CharField()
	quantity = forms.CharField()
	unit = forms.ChoiceField(widget=forms.Select, choices=UNIT_CHOICES)
	price = forms.CharField()
	desc = forms.CharField()
	is_available =  forms.BooleanField(widget=forms.Select(choices=AVAILABILITY_CHOICES), required=False)
	product_url = forms.URLField()
	stock_units = forms.CharField()
	#manufacturer = forms.ChoiceField(widget=forms.Select, choices=get_manufacturers())

	class Meta:
		document=Product
		fields=['name', 'quantity', 'unit', 'price', 'desc', 'weight', 'is_available', 'product_url', 'stock_units', 'manufacturer_id',]

	def save(self, merchant, commit):
		'''
		'''
		product = super(ProductForm, self).save(commit=False)
		product.manufacturer = Manufacturer.objects.get(id=self.cleaned_data['manufacturer_id'])
		product.merchant_id = merchant
		product.date_added = datetime.datetime.now()
		product.date_modified = datetime.datetime.now()
		dbProduct = product.save(commit=commit)
		return dbProduct


class ManufacturerForm(DocumentForm):
	'''
	'''
	manufacturer_url = forms.URLField()

	class Meta:
		document=Manufacturer
		fields=['manufacturer_name', 'manufacturer_url', 'manufacturer_desc',]
