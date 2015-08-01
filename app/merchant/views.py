from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from forms import MerchantForm, ProductForm, ManufacturerForm
from mongodbforms import documentform_factory
from app.models import Merchant, Address, Product
from django.contrib.auth import login, logout
from app.customer.forms import AddressForm, LoginForm
from mongoengine.queryset import DoesNotExist

def merchantIndex(request):
	'''
	'''
	if request.user and request.user.is_authenticated():
		return HttpResponseRedirect('/merchant/main/')
	return render(request, 'merchant/index.html', {'address_form': AddressForm(Merchant), 'merchant_form' : MerchantForm(), 'login_form' : LoginForm() })

def merchantMain(request):
	'''
	'''
	if not request.user or not request.user.is_authenticated():
		print "user not authenticated"
		return HttpResponseRedirect('/merchant/index/')
	products = Product.objects.filter(merchant_id=request.user)
	return render(request, 'merchant/main.html', { 'merchant': request.user.merchant_name, 'productForm' : ProductForm(), 'manufacturerForm' : ManufacturerForm(),
												   'merchant': request.user.merchant_name, 'products' : products})

def merchantLoginUser(request):
	'''
	'''
	if request.user and request.user.is_authenticated():
		return HttpResponseRedirect('/merchant/main/')
	if request.method == 'POST':
		loginForm = LoginForm(request.POST)
		if loginForm.is_valid():
			try:
				merchant = Merchant.objects.get(username=loginForm.cleaned_data['username'])  #authenticate(username=loginForm.cleaned_data['username'], password=loginForm.cleaned_data['password'])
			except DoesNotExist as detail:
				print "Such merchant does not exist", detail
				return HttpResponseRedirect('/merchant/index/')
			if merchant is not None and merchant.is_active and merchant.check_password(request.POST['password']):
				merchant.backend = 'mongoengine.django.auth.MongoEngineBackend'
				login(request, merchant)
				return HttpResponseRedirect('/merchant/main/')
			else:
				return HttpResponseRedirect('/merchant/index/')
		else:
			return HttpResponseRedirect('/merchant/index/')
	else:
		return HttpResponseRedirect('/merchant/index/')


def merchantLogoutUser(request):
	'''
	'''
	if request.user and request.user.is_authenticated():
		logout(request)
	return HttpResponseRedirect('/merchant/index/')


def merchantNewAccount(request):
	'''
	'''
	if request.user and request.user.is_authenticated():
		return HttpResponseRedirect('/merchant/main/')
	if request.method == 'POST':
		merchantForm = MerchantForm(request.POST)
		if merchantForm.is_valid():
			user = merchantForm.save(commit=False)
			addForm = AddressForm(user, request.POST, position=8)
			if addForm.is_valid():
				address = addForm.save(commit=True)
				user.save()
				return render(request, 'merchant/index.html', {'loginForm' : LoginForm(), 'message' : 'Your Merchandise account is created!! Please login and start selling..' })
			else:
				print addForm
				return render(request, 'merchant/create.html', {'address_form': addForm, 'merchant_form' : merchantForm, 'login_form' : LoginForm(), 'messages': ['Error with account create.']  })
		else:
			print merchantForm
			return render(request, 'merchant/create.html', {'address_form': AddressForm(Merchant), 'merchant_form' : merchantForm, 'login_form' : LoginForm(), 'messages': ['Error with account create.']  })
	else:
		return render(request, 'merchant/create.html', {'address_form': AddressForm(Merchant), 'merchant_form' : MerchantForm(), 'login_form' : LoginForm() })

def createManufacturer(request):
	'''
	'''
	if not request.user or not request.user.is_authenticated():
		print "user not authenticated"
		return HttpResponseRedirect('/merchant/index/')

	if request.method == 'POST':
		'''
		'''
		mForm = ManufacturerForm(request.POST)
		print mForm
		if mForm.is_valid():
			mForm.save(commit=True)
			return HttpResponseRedirect('/merchant/main/')
		else:
			return HttpResponseRedirect('/merchant/main/')
	else:
		return HttpResponseRedirect('/merchant/main/')

def createProduct(request):
	'''
	'''
	if not request.user or not request.user.is_authenticated():
		print "user not authenticated"
		return HttpResponseRedirect('/merchant/index/')

	if request.method == 'POST':
		'''
		'''
		print request.POST
		pForm = ProductForm(request.POST)
		if pForm.is_valid():
			pForm.save(request.user, commit=True)
			return HttpResponseRedirect('/merchant/main/')
		else:
			print pForm
			return HttpResponseRedirect('/merchant/main/')
	else:
		return HttpResponseRedirect('/merchant/main/')

def viewProducts(request):
	'''
	'''
	if not request.user or not request.user.is_authenticated():
		print "user not authenticated"
		return HttpResponseRedirect('/merchant/index/')

	products = Product.objects.filter(merchant_id=request.user)
	return render(request, 'merchant/view.html', { 'merchant': request.user.merchant_name, 'products' : products })
