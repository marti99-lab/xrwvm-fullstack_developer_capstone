# Uncomment the required imports before adding the code

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate

from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName": ""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    context = {}

    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except User.DoesNotExist:
        # If not, simply log this is a new user
        logger.debug(f"{username} is a new user")

    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
        return JsonResponse(data)
    else:
        data = {"userName": username, "error": "Already Registered"}
        return JsonResponse(data)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    url = "YOUR_DEALERSHIP_API_URL"
    dealerships = get_request(url)
    context = {"dealership_list": dealerships}
    return render(request, 'djangoapp/index.html', context)

# Create a `get_dealer_reviews` view to render the reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    url = f"YOUR_DEALER_REVIEWS_API_URL/{dealer_id}"
    reviews = get_request(url)
    context = {"reviews": reviews}
    return render(request, 'djangoapp/dealer_reviews.html', context)

# Create a `get_dealer_details` view to render the dealer details
def get_dealer_details(request, dealer_id):
    url = f"YOUR_DEALER_DETAILS_API_URL/{dealer_id}"
    dealer_details = get_request(url)
    context = {"dealer": dealer_details}
    return render(request, 'djangoapp/dealer_details.html', context)

# Create an `add_review` view to submit a review
@csrf_exempt
def add_review(request):
    if request.method == "POST":
        data = json.loads(request.body)
        review = {
            "name": data["name"],
            "dealership": data["dealership"],
            "review": data["review"],
            "purchase": data["purchase"],
            "purchase_date": data["purchase_date"],
            "car_make": data["car_make"],
            "car_model": data["car_model"],
            "car_year": data["car_year"]
        }
        json_payload = {"review": review}
        url = "YOUR_SUBMIT_REVIEW_API_URL"
        response = post_review(json_payload)
        return JsonResponse(response)

def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
    return JsonResponse({"CarModels": cars})