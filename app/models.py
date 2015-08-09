from mongoengine import *
from mongoengine.django.auth import User

###############################################################################################################
'''models.py

Provides database spec for the application.
Written by Aniket Zamwar (aniketzamwar@gmail.com)

Copyright 2014

'''
###############################################################################################################

CITY_CHOICES  = (('AKL', 'Akola'), ('PUN', 'Pune'), ('NAG', 'Nagpur'))
STATE_CHOICES = (('MAH', 'Maharashtra'),)
COUNTRY_CHOICES = (('IN','India'),)

class Address(EmbeddedDocument):
    """
    """
    line1   = StringField(required=True,
                          max_length=50,
                          verbose_name="Address Line 1",
                          help_text="Please enter address with less than 50 characters each line.")
    line2   = StringField(required=False,
                          max_length=50,
                          verbose_name="Address Line 2",
                          help_text="Please enter address with less than 50 characters each line.")
    city    = StringField(required=True,
                          choices=CITY_CHOICES,
                          max_length=3,
                          verbose_name="City",
                          help_text="Please select city from given options.")
    state   = StringField(required=True,
                          choices=STATE_CHOICES,
                          max_length=3,
                          verbose_name="State",
                          help_text="Please select state from given options.")
    country = StringField(required=True,
                          choices=COUNTRY_CHOICES,
                          max_length=2,
                          verbose_name="Country",
                          help_text="Please select country from given options.")
    pincode = IntField(required=True,
                        verbose_name="Pin Code",
                        help_text="Please provide valid pin-code without spaces.")

###############################################################################################################

class Activity(EmbeddedDocument):
    """
    """
    #session = StringField()
    date_account_verified = DateTimeField()
    date_account_modified = DateTimeField()
    last_password_change_date_time = DateTimeField()
    access_history = ListField(DictField())

###############################################################################################################
GENDER_CHOICES = (
  ("ML", "Male"),
  ("FM", "Female"),
)

class UserProfile(User):
    """Information of User profile.

       Following fields come from User.
       first_name, last_name, password, email, username, date_joined, is_active"""

    mobile  = StringField(max_length=10, verbose_name="Mobile Number:", help_text="Please enter your mobile number.")
    address = EmbeddedDocumentField(Address)
    gender  = StringField(max_length=2, choices=GENDER_CHOICES, verbose_name="Gender:", help_text="Please select your gender.")
    dob     = DateTimeField(verbose_name="Date of Birth:", help_text="Please enter your birth date.")
    is_email_verified = BooleanField(default=False)
    #account_activity = EmbeddedDocumentField(Activity)

###############################################################################################################
class Manufacturer(Document):
    """
    """
    manufacturer_name = StringField(required=True, max_length=50, verbose_name="Manufacturer:", help_text="Please enter manufacturer name.")
    manufacturer_url  = URLField()
    manufacturer_desc = StringField(required=True, max_length=200, verbose_name="Manufacturer Description", help_text="Please enter manufacturer description.")
###############################################################################################################

CATEGORY_TYPE = (
    "Raw Material",
    "Ready Steady Go",
    "Desserts",
    "Dare & Care"
)

CATEGORY_NAME = {
    CATEGORY_TYPE[0] : (
        "Grains",
        "Pulses & Grams",
        "Flour (Atta)",
        "Condiments & Spices",
        "Baking Needs",
        "Frozen & Canned",
        "Oil & Ghee",
        "Salt & Sugar",
        "Nuts & Oilseeds",
        "Others (Poha, Rawa, Corn Flakes, etc.)"
    ),
    CATEGORY_TYPE[1] : (
        "Ready to Eat",
        "Snacks",
        "Fresh Baked",
        "Pickles",
        "Dairy",
        "Beverages",
        "Breakfast Food",
        "Dried Food Items",
        "Dry Fruits",
        "Condiments & Sauces"
    ),
    CATEGORY_TYPE[2] : (
        "Sweets",
        "Chocoloates & Candies",
        "Ice Cream",
        "Fruit Juices (Soda)"
    ),
    CATEGORY_TYPE[3] : (
        "Health Care",
        "Personal Care",
        "Body Care",
        "House & Kitchen Care"
    ),
}

'''
## This is to import the catefory to data store

import pymongo
connection = pymongo.MongoClient("mongodb://localhost")
db = connection.sample_database
collection = db.category
for key, value in CATEGORY_NAME.iteritems():
    for c in value:
        collection.insert({ "category_type" : c, "category_name" : key })
'''

class Category(Document):
    category_type = StringField(required=True, verbose_name="Category Type")
    category_name = StringField(required=True, verbose_name="Category Name")

###############################################################################################################
class Merchant(UserProfile):
  """Information of Merchant.

       Following fields come from User.
       first_name, last_name, password, email, username, date_joined, is_active"""

  merchant_name  = StringField(required=True, verbose_name="Merchant Name: ")
  contact_number = IntField(required=True, verbose_name="Contact Number: ")
  merchant_url   = URLField(required=True)
  users          = ListField(UserProfile)
  is_merchant    = BooleanField(default=True)
  address        = EmbeddedDocumentField(Address)

###############################################################################################################
UNIT_CHOICES = (
  ('KG','Kilogram'),
  ('GM','Gram'),
  ('LT','Litre'),
  ('PK','Pack'),
  ('OT','Other'),
)

class Product(Document):
    name              = StringField(required=True, max_length=100, verbose_name="Product Name:", help_text="Please enter product name.")
    quantity          = DecimalField(required=True, verbose_name="Quantity for the given price:", help_text="Please enter quantity for given price.")
    unit              = StringField(required=True, max_length=2, choices=UNIT_CHOICES, default="KG")
    price             = DecimalField(required=True, verbose_name="Price for given quantity:", help_text="Please enter price for given quantity.")
    manufacturer      = ReferenceField(Manufacturer, verbose_name="Manufacturer")
    desc              = StringField(required=True, max_length=250, verbose_name="Product Description:", help_text="Please enter product description.")
    date_added        = DateTimeField(required=True)
    date_modified     = DateTimeField(required=True)
    is_available      = BooleanField(required=True, verbose_name="Is product available:", help_text="Please select if product is available.")
    product_url       = URLField(verbose_name="Product Link", help_text="Please provide product link for reference.") #todo remove this later
    stock_units       = IntField(verbose_name="Please enter number of units of quantity above", help_text="Please enter positive integer.")
    merchant_id       = ReferenceField(Merchant)
    category          = ReferenceField(Category)
    #product_images =

    meta = {'indexes': [
        {'fields': ['$name', "$desc"],
         'default_language': 'english',
         'weight': {'name': 10, 'desc': 5}
        }
    ]}

###############################################################################################################
class CartItem(EmbeddedDocument):
    """
    """
    per_unit_price = DecimalField(required=True)
    total_quantity = DecimalField(required=True)
    item_id        = ObjectIdField(Product)

DELIVERY_OPTION_CHOICES = (
  ('SP', 'Self Pickup'),
  ('SS', 'Standard shipping'),
  ('OS', 'One day shipping'),
  ('TS', 'Two day shipping'),
)

DELIVERY_CHARGES = {
    'SP' : 0.0,
    'SS' : 12.50,
    'OS' : 27.56,
    'TS' : 21.50,
}

DELIVERY_OPTION_CHOICES_AND_CHARGES = list()
for option in DELIVERY_OPTION_CHOICES:
    entry = { 'value' : option[0], 'name' : option[1], 'price' : DELIVERY_CHARGES[option[0]] }
    DELIVERY_OPTION_CHOICES_AND_CHARGES.append(entry)


class Delivery(EmbeddedDocument):
    delivery_type = StringField(max_length=2, choices=DELIVERY_OPTION_CHOICES)
    delivery_price = DecimalField()
    expected_delivery_date = DateTimeField()

PAYMENT_OPTIONS_CHOICES = (
    ('CD', 'Cash on delivery'),
)

class Payment(EmbeddedDocument):
    payment_time = StringField(max_length=2, choices=PAYMENT_OPTIONS_CHOICES)
    payment_amount = DecimalField()

###############################################################################################################

ORDER_STATUS_OPTIONS = (
    ('OP', 'Order Placed'),
    ('OR', 'Order Received'),
    ('OP1', 'Order Processing'),
    ('OP2', 'Order Processed'),
    ('OS', 'Order Shipped'),
    ('OD', 'Order Delivered'),
    ('OC','Order Cancelled'),
)

class Order(Document):
    customer_id         = ObjectIdField(UserProfile)
    ordered_items       = ListField(EmbeddedDocumentField(CartItem))
    date_of_order       = DateTimeField()
    total_amount        = DecimalField()
    cart_amount         = DecimalField()
    delivery_info       = EmbeddedDocumentField(Delivery)
    payment_info        = EmbeddedDocumentField(Payment)
    order_status        = StringField(min_length=2, max_length=3, choices=ORDER_STATUS_OPTIONS, default='OP')


###############################################################################################################
class Comment(EmbeddedDocument):
    customer        = ObjectIdField(UserProfile)
    date_of_comment = DateTimeField()
    comment         = StringField()
    is_harsh        = BooleanField()
    comments        = ListField(EmbeddedDocumentField('self'))

###############################################################################################################
class Review(Document):
    product           = ObjectIdField(Product)
    order             = ObjectIdField(Order)
    customer          = ObjectIdField(UserProfile)
    ratings           = IntField()
    review_state      = BooleanField()
    review_desc       = StringField()
    review_useful     = BooleanField()
    review_not_useful = BooleanField()
    date_added        = DateTimeField()
    is_harsh          = BooleanField()
    comments          = SortedListField(EmbeddedDocumentField(Comment), ordering="date_of_comment", reverse=True)
    #product_images   =


###############################################################################################################
