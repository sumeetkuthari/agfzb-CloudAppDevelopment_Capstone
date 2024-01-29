import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    
    # If argument contain API KEY
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    print(kwargs)
    print(f"POST to: {url}")
    print(json_payload)
    response = requests.post(url, params=kwargs, json=json_payload)
    print(f"With status: {response.status_code}")
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    print(json_result)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
         
            dealer_doc = dealer
         
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list

def get_dealer_by_id_from_cf(url, id):
    
    print("In get_dealer_by_id_from_cf")
    #mod_url = url + f"?id={str(id)}"
    json_result = get_request(url, dealerId=id)
    print(f"Json result is: {json_result}")
    if json_result:
        dealers = json_result
        dealer_doc = dealers[0]
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"], short_name=dealer_doc["short_name"], 
                                full_name=dealer_doc["full_name"], st=dealer_doc["st"], zip=dealer_doc["zip"])
    return dealer_obj

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_reviews_from_cf(url, dealer_id):
# - Call get_request() with specified arguments
# - Parse JSON results into a list of DealerReview objects

def get_dealer_reviews_from_cf(url, dealer_id, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealer_id)
    print(f"In get_dealer_reviews")
    print(f"json_result is: {json_result}")
    if json_result:
        # Get the row list in JSON as reviews
        reviews = json_result
        # For each reviews object
        for review in reviews:
            # Get its content in `doc` object
            review_doc = review
            # Create a DealerReview object with values in `doc` object
            sentiment = analyze_review_sentiments(review_doc["review"])
            #sentiment = 'neutral'
            review_obj = DealerReview(id=review_doc["id"],name=review_doc["name"],dealership=review_doc["dealership"],
                                    review=review_doc["review"],purchase=review_doc["purchase"],
                                    purchase_date=review_doc["purchase_date"],car_make=review_doc["car_make"],
                                    car_model=review_doc["car_model"],car_year=review_doc["car_year"],
                                    sentiment=sentiment)
            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/ff361456-255b-4008-9234-5cca1de4c519"
    api_key = "ZnM34eLHoZ0dRclGuc_u_maw5O1AwplNtXpjl_myuvge"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+"hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+"hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    print(f"Sentiment analysis is: {label}")
    return(label)

