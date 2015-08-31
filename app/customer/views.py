import json, bson
import sys, logging
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
from django.contrib.auth import login, logout
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.contrib import messages
from app.models import DoesNotExist

from forms import UserProfileForm, AddressForm, LoginForm
from app.models import UserProfile, Product, Category
from app.models import CITY_CHOICES, STATE_CHOICES, COUNTRY_CHOICES, DELIVERY_OPTION_CHOICES_AND_CHARGES

CITY_CHOICES_SELECT = []
for city in CITY_CHOICES:
    CITY_CHOICES_SELECT.append({"value": city[0], "text": city[1]})

STATE_CHOICES_SELECT = []
for state in STATE_CHOICES:
    STATE_CHOICES_SELECT.append({"value": state[0], "text": state[1]})

COUNTRY_CHOICES_SELECT = []
for country in COUNTRY_CHOICES:
    COUNTRY_CHOICES_SELECT.append({"value": country[0], "text": country[1]})

# Create your views here.
@login_required
def main(request):
    #if not request.user or not request.user.is_authenticated():
    #    return HttpResponseRedirect('/index/')
    message = None
    if "message" in request.session:
        message = request.session["message"]
        request.session.pop("message")
    return render(request, 'customer/main.html', { 'uname': request.user.get_full_name(), "message": message  })

def index(request):
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect('/main/')
    userProfileForm = UserProfileForm()
    addressForm = AddressForm(UserProfile)
    login_form = LoginForm()
    print login_form
    return render(request, 'customer/index.html', { 'loginForm' : login_form })

@require_POST
def loginUser(request):
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect('/main/')
    messages.set_level(request, messages.INFO)
    loginForm = LoginForm(request.POST)
    if loginForm.is_valid():
        try:
            user = UserProfile.objects.get(username=loginForm.cleaned_data['username'])  #authenticate(username=loginForm.cleaned_data['username'], password=loginForm.cleaned_data['password'])
            if user and user.is_active and user.check_password(request.POST['password']):
                user.backend = 'mongoengine.django.auth.MongoEngineBackend'
                login(request, user)
                request.session.set_expiry(60 * 60 * 1) # 1 hour timeout
                return HttpResponseRedirect('/main/')
        except DoesNotExist:
            print "Unexpected error:", sys.exc_info()[0]
        except:
            print "Unexpected error:", sys.exc_info()[0]
        messages.add_message(request, messages.ERROR, "Username/password not found!!", extra_tags="alert-danger", fail_silently=False)
        return HttpResponseRedirect('/index/')
    else:
        print "Invalid form"
        print loginForm
        return HttpResponseRedirect('/index/')

@login_required
def logoutUser(request):
    if request.user and request.user.is_authenticated():
        logout(request)
    return HttpResponseRedirect('/index/')

@require_POST
def newAccount(request):
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect('/main/')
    if request.method == 'POST':
        userForm = UserProfileForm(request.POST)
        if userForm.is_valid():
            user = userForm.save(commit=False)
            addForm = AddressForm(user, request.POST, position=8)
            if addForm.is_valid():
                addForm.save(commit=True)
                user.save()
                messages.add_message(request, messages.INFO, "Account Created!! Please login.", extra_tags="alert-info", fail_silently=False)
                return HttpResponseRedirect('/index/')
            else:
                return render(request, 'customer/create.html', { 'loginForm': LoginForm(), 'userForm': userForm, 'addressForm': addForm, 'messages': ['Error with account create.'] })
        else:
            print userForm
            addressForm = AddressForm(UserProfile)
            return render(request, 'customer/create.html', { 'loginForm': LoginForm(), 'userForm': userForm, 'addressForm': addressForm, 'messages': ['Error with account create.'] })
    else:
        return render(request, 'customer/create.html', { 'loginForm': LoginForm(), 'userForm': UserProfileForm(), 'addressForm': AddressForm(UserProfile) })


@require_GET
def getCategories(request):
    data = {};
    for category in Category.objects:
        if category.category_name not in data:
            data[category.category_name] = []
        data[category.category_name].append({'id': str(category.id), 'name' : category.category_type})
    return HttpResponse(json.dumps(data), content_type="application/json")

@require_GET
def search(request, cId, page, query):
    if cId == "global":
        cId = None

    p = 1
    try:
        p = int(page)
        if p <= 0:
            p = 1
    except ValueError:
        print "Unexpected error:", sys.exc_info()[0]
        p = 1

    ITEMS_PER_PAGE = 15
    offset = (p - 1) * ITEMS_PER_PAGE
    data = {}
    query = query.strip()
    try:
        products = []
        if query and cId:
            products = Product.objects(category=bson.objectid.ObjectId(cId)).search_text(query).order_by('$text_score').skip(offset).limit(ITEMS_PER_PAGE + 1).only('name', 'desc', 'quantity', 'unit', 'price', 'id')
        elif query:
            products = Product.objects.search_text(query).order_by('$text_score').skip(offset).limit(ITEMS_PER_PAGE + 1).only('name', 'desc', 'quantity', 'unit', 'price', 'id')
        elif cId:
            products = Product.objects(category=bson.objectid.ObjectId(cId)).skip(offset).limit(ITEMS_PER_PAGE + 1).only('name', 'desc', 'quantity', 'unit', 'price', 'id')
        else:
            products = Product.objects.skip(offset).limit(ITEMS_PER_PAGE + 1).only('name', 'desc', 'quantity', 'unit', 'price', 'id')(name__icontains=query)
        if products and len(products) > ITEMS_PER_PAGE:
            data["products"] = products[0 : ITEMS_PER_PAGE].to_json()
            data['next'] = p + 1
        else:
            data["products"] = products.to_json()
        if p > 1:
            data['prev'] = p - 1
    except:
        data["products"] = []
        print "Unexpected error:", sys.exc_info()[0]

    data["cartCount"] = request.session.get('cartCount', 0)
    return HttpResponse(json.dumps(data), content_type="application/json")

@require_GET
def getProduct(request, pId):
    data = {}
    try:
        product = Product.objects.get(id=bson.objectid.ObjectId(pId))
        if product:
            data["product"] = product.to_json()
    except:
        print "Unexpected error:", sys.exc_info()[0]
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
@require_GET
def addToCart(request, pId, count):
    data = {}
    message = None
    cartCount = request.session.get('cartCount', 0)
    status = 0
    try:
        product =  Product.objects.only('name', 'unit').get(id=bson.objectid.ObjectId(pId))
        if product:
            message = product.name + " " + str(count) + " " + product.get_unit_display() + " added to your cart."
            cart = request.session.get('cart', {})
            if pId in cart:
                newCount = int(cart[pId]) + int(count)
                if (newCount > 10):
                    message = "You already have %d %s in cart, you can add only %d more of these products to cart." %(int(cart[pId]), product.name, 10 - int(cart[pId]))
                    count = 0
                else:
                    cart[pId] = newCount
            else:
                cart[pId] = int(count)
            cartCount = cartCount + int(count)
            request.session['cartCount'] = cartCount
            request.session['cart'] = cart
        else:
            status = -1
            message = "Sorry!! No such product found to add to cart."
    except:
        print "Unexpected error:", sys.exc_info()[0]
        status = -1
        message = "Unexpected error occurred while adding the product to cart."

    data["status"] = status
    data["message"] = message
    data["cartCount"] = cartCount
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
@require_GET
def updateCart(request, pId, count):
    data = {}
    message = None
    cartCount = request.session.get('cartCount', 0)
    status = 0
    try:
        product =  Product.objects.only('name', 'unit').get(id=bson.objectid.ObjectId(pId))
        if product:
            message =  product.name + " count updated in cart to " + str(count)
            cart = request.session.get('cart',{})
            if pId in cart:
                prevCount = int(cart[pId])
                difference = int(count) - prevCount
                cartCount = cartCount + difference
                request.session['cartCount'] = cartCount
                if count > 0:
                    cart[pId] = int(count)
                elif count == 0:
                    message = "Product " + product.name + " removed from cart."
                    del cart[pId]
                request.session['cart'] = cart
            else:
                status = -1
                message = "No product found in cart to perform count update."
        else:
            status = -1
            message = "Sorry!! No such product found to update in your cart!"
    except:
        print "Unexpected error:", sys.exc_info()
        status = -1
        message = "Unexpected error occurred while updating the cart."

    data["status"] = status
    data["message"] = message
    data["cartCount"] = cartCount
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
@require_GET
def deleteFromCart(request, pId):
    data = {}
    message = None
    cartCount = request.session.get('cartCount', 0)
    status = 0
    cart = request.session.get('cart',{})
    if pId in cart:
        count = cart.pop(pId)
        cartCount = cartCount - count
        request.session['cart'] = cart
        request.session['cartCount'] = cartCount
        product =  Product.objects.only('name', 'desc', 'quantity', 'unit', 'price', 'id').get(id=bson.objectid.ObjectId(pId))
        if product:
            message = product.name + " " + str(count)  + " " + product.get_unit_display()  + ("s" if (count > 1) else "") + " deleted from your cart!!"
        else:
            message = "Product removed from cart, but no such product found in inventory."
    else:
        status = -1
        message = "Sorry!! No such product found that was added to cart!"

    data["status"] = status
    data["message"] = message
    data["cartCount"] = cartCount
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def viewCart(request):
    #if not request.user or not request.user.is_authenticated():
    #    return HttpResponseRedirect('/index/')

    data = {
        "status" : 0
    };
    cart = request.session.get('cart',{})
    for key in cart.keys():
        product =  Product.objects.only('name', 'desc', 'quantity', 'unit', 'price', 'id').get(id=bson.objectid.ObjectId(key))
        if product:
            cartItem = {
                'name': product.name,
                'count': cart[key],
                'price':str(product.price),
                'unit': product.get_unit_display(),
                'quantity': str(product.quantity)
            };
            if "products" not in data:
                data["products"] = {}
            data["products"][key] = cartItem
        else:
            del cart[key]
    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def checkoutCart__OLDD(request):
    #if not request.user or not request.user.is_authenticated():
    #    return HttpResponseRedirect('/index/')
    message = None
    if "message" in request.session:
        message = request.session["message"]
        request.session.pop("message")

    products = []
    cart = request.session.get('cart',{})
    totalPrice = 0
    for key in cart:
        product =  Product.objects.only('name', 'desc', 'quantity', 'unit', 'price', 'id').get(id=bson.objectid.ObjectId(key))
        if product:
            productDict = product.to_mongo()
            productDict['quantity'] = product.quantity
            productDict['count'] = cart[key]
            productDict['total'] = product.price * long(cart[key])
            productDict['id'] = key
            productDict['unit'] = product.get_unit_display()
            totalPrice = totalPrice + productDict['total']
            products.append(productDict)
    t = get_template('customer/checkoutCart.html')
    print products
    if len(products) == 0:
        products = None
    html = t.render(RequestContext(request, { 'uname': request.user.get_full_name(),
                                              'products' : products,
                                              'totalPrice': totalPrice,
                                              'message' : message }))
    return HttpResponse(html)

@login_required
@csrf_exempt
def checkoutCart(request):
    data = {}

    # process request information
    # validate information
    # update the shipping inforamtion in the session
    print request.POST

    # Get cart information to return to client
    cart = request.session.get('cart',{})
    for key in cart.keys():
        product =  Product.objects.only('name', 'desc', 'quantity', 'unit', 'price', 'id').get(id=bson.objectid.ObjectId(key))
        if product:
            cartItem = {
                'name': product.name,
                'count': cart[key],
                'price':str(product.price),
                'unit': product.get_unit_display(),
                'quantity': str(product.quantity)
            };
            if "products" not in data:
                data["products"] = {}
            data["products"][key] = cartItem
        else:
            del cart[key]

    data['shippingOptions'] = DELIVERY_OPTION_CHOICES_AND_CHARGES
    data['message'] = "Success!!"
    data['success'] = True

    return HttpResponse(json.dumps(data), content_type="application/json")

@login_required
def myInfo(request):
    user = UserProfile.objects.get(id=bson.objectid.ObjectId(request.user.id))
    if not user:
        return HttpResponseRedirect('/index/')

    userDict = user.to_mongo()
    t = get_template('customer/user.html')
    print userDict
    html = t.render(RequestContext(request, { "user" : userDict, "cities" : mark_safe(json.dumps(CITY_CHOICES_SELECT)), "states" : mark_safe(json.dumps(STATE_CHOICES_SELECT)), "countries" : mark_safe(json.dumps(COUNTRY_CHOICES_SELECT))} ))
    return HttpResponse(html)

@login_required
def updateUser(request, field):
    response = {}
    if request.method == 'POST':
        value = request.POST.get(field)
        try:
            user = UserProfile.objects.get(id=request.user.id)
            if user:
                print field, value
                flag = False
                if field == "fname":
                    user.update(set__first_name=str(value))
                    flag = True
                elif field == "lname":
                    user.update(set__last_name=str(value))
                    flag = True
                elif field == "email":
                    user.update(set__email=str(value))
                    flag = True
                elif field == "gender":
                    user.update(set__gender=str(value))
                    flag = True
                elif field == "mobile":
                    user.update(set__mobile=str(value))
                    flag = True
                user.reload()
                if flag:
                    response['status'] = 'success'
                else:
                    response['status'] = 'error'
                    response['msg'] = 'Invalid field modified or error occurred.'
                request.user = user
            else:
                response['status'] = 'error'
                response['msg'] = 'Error occurred while updating user in database. No user found.'
        except:
            print "Unexpected error:", sys.exc_info()[0]
            response['status'] = 'error'
            response['msg'] = 'Error occurred while updating database. Please try again later.'
    else:
        response['status'] = 'error'
        response['msg'] = 'We only support POST requests'
    return HttpResponse(json.dumps(response), content_type="application/json")
