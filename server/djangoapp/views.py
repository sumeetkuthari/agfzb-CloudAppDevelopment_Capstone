from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarDealer, DealerReview, CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_by_id_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import post_request

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create an `about` view to render a static about page
def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


# Create a `contact` view to return a static contact page
#def contact(request):
def contact(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, 'djangoapp/index', context)
    else: 
        return render(request, 'djangoapp/index', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    print(f"Log out the user: {request.user.username}")
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            user.objects.get(username=username)
            user_exist = True
        except:
            logger.debug(f"{username} is a new user")

        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
            login(request, user)
            return redirect('djangoapp:index')
        else:
            return render(request, "djangoapp/registration.html", context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://sumeetkuthar-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context['dealership_list'] = dealerships
        # Return a list of dealer short name
        #return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)
        

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        dealer_url = f"https://sumeetkuthar-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get?id={str(dealer_id)}"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
        print(f"Dealer is: {dealer}")
        context["dealer"] = dealer
        review_url = f"https://sumeetkuthar-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews?id={str(dealer_id)}"
        
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id)
        context["reviews"] = reviews
        print(f"Reviews list is: {reviews}")
        #return HttpResponse(reviews)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...
def add_review(request, dealer_id):
    #Check if user is authenticated
    context = {}
    dealer_url = f"https://sumeetkuthar-3000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get?id={str(dealer_id)}"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=dealer_id)
    context['dealer'] = dealer
    
    if request.method == "GET":
        cars = CarModel.objects.all()
        context["cars"] = cars
        return render(request, "djangoapp/add_review.html", context)
    
    if request.method == 'POST':
        #check if user is authenticated
        if request.user.is_authenticated:
            username = request.user.username
            payload = dict()
            car_id = request.POST['car']
            car = CarModel.objects.get(id=car_id)
            #payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = dealer_id
            payload["review"] = request.POST['content']
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST['purchasecheck'] == "on":
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST['purchasedate']
            payload["car_model"] = car.name
            payload["car_make"] = car.car_make.name
            payload["car_year"] = int(car.year.strftime("%Y"))
            payload["another"] = "field"
            payload["id"] = dealer_id
            #payload["id"] = dealer_id
            new_payload = {}
            new_payload = payload
            print(f"New payload is: {new_payload}")
            post_url = "https://sumeetkuthar-5000.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            post_request(post_url, json_payload=new_payload, id=dealer_id)
            return redirect("djangoapp:dealer_details", dealer_id=dealer_id)
