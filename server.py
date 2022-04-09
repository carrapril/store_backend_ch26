import json
from unicodedata import category
from unittest import result
from flask import Flask, abort, request
from mock_data import catalog
from config import db
from bson import ObjectId
from flask_cors import CORS



app = Flask("Server")


@app.route("/")
def home():
    return "hello from flask"


@app.route("/me")
def about_me():
    return "April Carr"

#####################################    API Endpoints ALWAYS Return JSONS ############################
# #######################################################################################################
###################################################################################################

@app.route("/api/catalog", methods=["get"])
def get_catalog():

    products = []

    cursor = db.products.find({})

    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        products.append(prod)

    return json.dumps(cursor)    


    

@app.route("/api/catalog", methods=["post"])
def save_product():
    product = request.get_json()
    
    db.products.insert_one(product) 
    print(product)
    
    #fix_id

    product["_id"] = str(product["_id"])


    #crash
    return json.dumps(product)




#### get /api/catalog/count

@app.route("/api/catalog/count", methods=["get"])
def product_count():
    cursor = db.products.find({})
    count = 0
    for prod in cursor: 
        count += 1

    return json.dumps(count)

#get /api/catalog/total sum of all product prices

@app.route("/api/catalog/total", methods=["get"])
def total_price():
    
    total = 0
    cursor = db.products.find({})
    
    for prod in cursor:
        total += prod["price"]
    
    return json.dumps(total) 




#get /api/product/id

@app.route("/api/product/<id>")
def get_by_id(id):
    prod = db.products.find_one({"_id": ObjectId(id)})

    if not prod:
        return abort(404, "No Product with that ID")

    prod["_id"] = str(prod["_id"])
    return json.dumps(prod)
        

@app.route("/api/products/cheapest", methods=["get"])
def cheapest_product():
    
    products = catalog[0]

    for prices in catalog:
        if prices["price"] < products["price"]:
            products = prices
            
    return json.dumps(products)    

#get /api/categories

@app.route("/api/categories", methods=["get"])
def categories():
    uniquecategory = []
    for prod in catalog:
        category = prod["category"]
        if not category in uniquecategory:
            uniquecategory.append(category)
            
    return json.dumps(uniquecategory)        

#
# ticket 2345
#create an endpoint that allow the client to get all the products for a specified category

@app.route("/api/catalog/<category>")
def prods_by_category(category):
    
    products = []
    cursor = db.products.find({"category": category})
    for prod in cursor:
        prod["_id"] = str(prod["_id"])
        products.append(prod)
            
    return json.dumps(products)

@app.get("/api/someNumbers")
def some_numbers():
    #return a list with numbers from 1 to 50 as json
    numbers = []
    
    for num in range(1,51):
        numbers.append(num)
        
    return json.dumps(numbers)


#####################################
######################coupon code endpoints###############
####################################################

allCoupons = []

#create the get/api/couponCode
#return all coupons as json list

@app.route("/api/couponCode", methods=["GET"])
def get_coupons():
    coupons = []
    cursor = db.couponCode.find({})
    for code in cursor:
        code["_id"] = str(code["_id"])
        coupons.append(code)
        
    
    return json.dumps(coupons)

@app.route("/api/couponCode", methods=["POST"])
def save_coupon():
    coupon = request.get_json()
    
    #must contain code, discount
    
    if not "code" in coupon or not "discount" in coupon:
        return abort(400, "The coupon must contain code and discount number")
    
    #code should have at least 5 characters
    if len(coupon["code"]) <5:
        return abort(400,"The code is less than 5 Characters")
    
    #discount should not be lower than 5% and not greater than 50%
    
    if coupon["discount"] < 5 or coupon["discount"] > 50:
        return abort(400,"Invalid discount amount")
    
    db.couponCodes.insert_one(coupon)
    
    coupon["_id"] = str(coupon["_id"])
    return json.dumps(coupon)



@app.route("/api/couponCode/<code>")
def get_coupon_by_code(code):
    coupon = db.couponCodes.find_one({"code": code})
    if not coupon:
        return abort(404, "Invalid Code")

    coupon["_id"] = str(coupon["_id"])
    
    return json.dumps(coupon)

#################### Users Endpoint########
###########################################
##########################################

@app.route("/api/users", methods=["GET"])
def get_users():
    all_users = []
    cursor = db.users.find({})
    for user in cursor:
        user["_id"] = str(user["_id"])
        all_users.append(user)
        
    return json.dumps(all_users)


@app.route("/api/users", methods=["POST"])
def save_user():
    user = request.get_json()
    
    
    ## validate userName, password, email
    
    if not "userName" in user or not "password" in user or not "email" in user:
        return abort(400, "Must contain userName, email, and password")
    
    
    #check that the values are not empty
    
    if len(user["userName"]) < 1 or len(user["password"]) < 1 or len(user["email"]) < 1:
        return abort(400, "please enter values")
    
    db.users.insert_one(user)
    
    
    user["_id"] = str(user["_id"])
    return json.dumps(user)

@app.route("/api/users/<email>")
def get_user_by_email(email):
    user = db.user.find_one({"email: email"})
    if not user:
        return abort(404, "No user with that email")
    
    user["_id"] = str(user["_id"])
    
    return json.dumps(user)

### Validations


@app.route("/api/login", methods=["POST"])
def validate_user_data():
    data = request.get_json() #<= dict with the user and password
    
    if not 'user' in data:
        return abort(400, "The User is required for login")
    
    if not 'password' in data:
        return abort(400, "The Password is required for login")
    
    user = db.users.find_one({"userName": data["user"], "password": data["password"]})
    if not user:
        abort(401, "NO such user with that username or password")
        
    user["_id"] = str(user["_id"]) 
    user.pop("password")  #remove the key and values from the dict.
    
    return json.dumps(user)
    


app.run(debug=True)