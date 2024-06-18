from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)

# View to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
        else:
            return JsonResponse({"error": "Invalid credentials"}, status=401)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

# View to handle sign out request
def logout_request(request):
    logout(request)
    return JsonResponse({"userName": ""})

# View to handle sign up request
@csrf_exempt
def registration(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')

        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        else:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password, email=email)
            login(request, user)
            return JsonResponse({"userName": username, "status": "Authenticated"})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

# View to fetch dealerships based on state
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

# View to fetch reviews of a dealer
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# View to fetch details of a dealer
def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

# View to add a review
@csrf_exempt
def add_review(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            data = json.loads(request.body)
            try:
                response = post_review(data)
                return JsonResponse({"status": 200, "message": "Review posted successfully"})
            except Exception as e:
                logger.error(f"Error posting review: {e}")
                return JsonResponse({"status": 500, "message": "Internal Server Error"})
        else:
            return JsonResponse({"error": "Method not allowed"}, status=405)
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})

# View to fetch car models
def get_cars(request):
    if request.method == 'GET':
        count = CarMake.objects.count()
        if count == 0:
            initiate()
        car_models = CarModel.objects.select_related('car_make')
        cars = [{"CarModel": car_model.name, "CarMake": car_model.car_make.name} for car_model in car_models]
        return JsonResponse({"CarModels": cars})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
