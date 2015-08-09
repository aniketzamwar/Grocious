import json, sys, bson
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from forms import MerchantForm, ProductForm, ManufacturerForm
from mongodbforms import documentform_factory
from app.models import Merchant, Address, Product, Manufacturer, Category
from django.contrib.auth import login, logout
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from app.customer.forms import AddressForm, LoginForm
from mongoengine.queryset import DoesNotExist
from app.models import UNIT_CHOICES

UNIT_CHOICES_SELECT = []
for unit in UNIT_CHOICES:
    UNIT_CHOICES_SELECT.append({"value": unit[0], "text": unit[1]})

CATEGORIES = []
cts = Category.objects.only("id", "category_type", "category_name")
if cts:
    for c in cts:
        CATEGORIES.append({"value": str(c.id), "text": c.category_name + " - " + c.category_type})

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
	manufacturers = []
	if products:
		mfs = Manufacturer.objects.only("id", "manufacturer_name")
		print mfs
		if mfs:
			for m in mfs:
				manufacturers.append({"value": str(m.id), "text": m.manufacturer_name})
	print manufacturers

	return render(request, 'merchant/main.html', { 'merchant': request.user.merchant_name, 'productForm' : ProductForm(), 'manufacturerForm' : ManufacturerForm(),
												   'merchant': request.user.merchant_name, 'products' : products,
												   'unit' : mark_safe(json.dumps(UNIT_CHOICES_SELECT)), 'manufacturers' : mark_safe(json.dumps(manufacturers)),
                                                   'categories' : mark_safe(json.dumps(CATEGORIES)) })

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

@login_required
def deleteProduct(request, pid):
    response = {}
    print pid
    try:
        product = Product.objects.get(id=bson.objectid.ObjectId(pid))
        if product:
            product.delete();
            response['status'] = 0
            response['msg'] = 'Product ' + product.name + ' deleted.'
        else:
            response['status'] = -1
            response['msg'] = 'Product not found'
    except:
        print "Unexpected error:", sys.exc_info()
        response['status'] = -1
        response['msg'] = 'Error occurred while updating database. Please try again later.'

    return HttpResponse(json.dumps(response), content_type="application/json")


@login_required
def updateProduct(request, field, pid):
    response = {}
    print field, pid
    if request.method == 'POST':
        value = request.POST.get(field)
        try:
            product = Product.objects.get(id=pid)
            print product.to_json()
            # todo add product merchange and current merchant id are same
            if product:
                print field, value
                flag = False
                if field == "name":
                    product.update(set__name=str(value))
                    flag = True
                elif field == "quantity":
                    product.update(set__quantity=str(value))
                    flag = True
                elif field == "unit":
                    product.update(set__unit=str(value))
                    flag = True
                elif field == "price":
                    product.update(set__price=str(value))
                    flag = True
                elif field == "manufacturer":
                    product.update(set__manufacturer=str(value))
                    flag = True
                elif field == "desc":
                    product.update(set__desc=str(value))
                    flag = True
                elif field == "producturl":
                    product.update(set__product_url=str(value))
                    flag = True
                elif field == "stockunits":
                    product.update(set__stock_units=str(value))
                    flag = True
                elif field == "isavailable":
                    product.update(set__is_available=str(value))
                    flag = True
                elif field == "category":
                    product.update(set__category=str(value))
                    flag = True
                product.reload()
                if flag:
                    response['status'] = 'success'
                else:
                    response['status'] = 'error'
                    response['msg'] = 'Invalid field modified or error occurred.'
            else:
                response['status'] = 'error'
                response['msg'] = 'Error occurred while updating product in database. No product found.'
        except:
            print "Unexpected error:", sys.exc_info()
            response['status'] = 'error'
            response['msg'] = 'Error occurred while updating database. Please try again later.'
    else:
        response['status'] = 'error'
        response['msg'] = 'We only support POST requests'
    print response
    return HttpResponse(json.dumps(response), content_type="application/json")
