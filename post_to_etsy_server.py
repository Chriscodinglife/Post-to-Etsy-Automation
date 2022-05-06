#! python

'''

 ______     __  __     ______     __     ______    
/\  ___\   /\ \_\ \   /\  == \   /\ \   /\  ___\   
\ \ \____  \ \  __ \  \ \  __<   \ \ \  \ \___  \  
 \ \_____\  \ \_\ \_\  \ \_\ \_\  \ \_\  \/\_____\ 
  \/_____/   \/_/\/_/   \/_/ /_/   \/_/   \/_____/ 
                                                   

Post To Etsy Automation
April 2022

The goal of this script to post onto Etsy the official listing for a given stream package.

This script will utilize the FASTAPI to create a server instead of flask.


'''
## Imports
import os
import csv
import sys
import json
import pkce
import array
import random
import string
import uvicorn
import requests
from fastapi import FastAPI
from dotenv import load_dotenv
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse


# Load in the secret variables
load_dotenv()

# Grab and store the directory of the script
file_dir = os.path.dirname(__file__)

description_file = input("Input the location of the description file for this project: ")
stripped_desc_file = description_file.replace('"', "")
desc_file_location = os.path.normpath(stripped_desc_file)
post_description = ""
if not os.path.isfile(desc_file_location):
    print("You did not enter a proper description file. Exiting...")
    exit()
with open(desc_file_location, "r") as file:
    for line in file:
        post_description += line

etsy_listing_images = input("Please put in the path for the Etsy Images: ")
etsy_images_stripped = etsy_listing_images.replace('"', "")
etsy_images_path = os.path.normpath(etsy_images_stripped)
if not os.path.isdir(etsy_images_path):
    print("You did not enter a proper folder for the images. Exiting...")
    exit()

etsy_title = input("What is the title of this Etsy Post?: ")

## Functions


# Create a basic password generator for the state key
def password_generator(length):

    '''This will create a password based on the length provided.'''

    length = int(length)
    lower = string.ascii_lowercase
    upper = string.ascii_uppercase
    num = string.digits
    symbols = string.punctuation
    all = lower + upper + num + symbols
    temp = random.sample(all, length)
    password = "".join(temp)
    return password


def get_tags_and_materials():

    '''This function will return an array of strings by asking the user for input'''

    # For some reason we pass in the list as described by Etsy API documentation but
    # No dice for something. Will leave this here becuase still pretty cool to use.
    material_list = []
    tags_list = []
    
    while len(material_list) < 13:
        inputted_materials = input("This listing requires a list of materials. Input a list of keywords, seperated by commas(,): ")
        inputted_list = inputted_materials.strip().split(",")
        for item in inputted_list:
            if len(material_list) < 13:
                material_list.append(item)
                print("We still need more items to be added to the Materials List.")

    materials_for_tags = input("Do you want to use materials as your tags?[yes/no]: ")
    if materials_for_tags == "yes" or materials_for_tags == "y":
        tags_list = material_list
    else: 
        while len(tags_list) < 13:
            inputted_tags = input("This listing requires a list of Tags. Input a list of keywords, seperated by commas(,): ")
            inputted_list = inputted_tags.strip().split(",")
            for item in inputted_list:
                if len(tags_list) < 13:
                    tags_list.append(item)
                    print("We still need more items to be added to the Tags list.")

    return material_list, tags_list

materials, tags = get_tags_and_materials()

# Load in a csv that contains the Etsy listing details and convert them
# Into a dictionary as a payload for requests.post
def get_draft_payload():

    '''This function will build the payload for the Etsy Listing'''

    payload = {}

    payload['quantity'] = 100
    payload['title'] = etsy_title
    payload['description'] = post_description
    payload['price'] = 10
    payload['who_made'] = "i_did"
    payload['when_made'] = "2020_2022"
    payload['taxonomy_id'] = 77
    payload['materials'] = materials
    payload['tags'] = tags
    payload['is_personalizable'] = False
    payload['personalization_is_required'] = False
    payload['should_auto_renew'] = True
    payload['type'] = "download"

    return payload


## Variables
auth_code = ""
response_type = "code"
redirect_uri = "http://localhost:5000/redirection"
scope = 'listings_w'
client_id = os.getenv("client_id")
client_secret = os.getenv("client_secret")
state = password_generator(20)
code_verifier = pkce.generate_code_verifier(length=128)
code_challenge = pkce.get_code_challenge(code_verifier)
code_challenge_method = "S256"
shop_id = os.getenv("shop_id")
access_token = ""
listing_id = ""

original_token = f"{file_dir}/original_token.json"
original_token_path = os.path.normpath(original_token)
if not os.path.isfile(original_token_path):
    print("A token file is not present.")

mod_time = datetime.fromtimestamp(os.path.getmtime(original_token))
current_time = datetime.now()
etsy_token_url = 'https://api.etsy.com/v3/public/oauth/token'

# Initiate the Fastapi App
app = FastAPI()

## Web Endpoints


# Make a generic welcome page
@app.get("/")
def welcome():

    '''This is a generic welcome page to let the user know how to start'''
    
    return "Welcome. Please go to /oauth to start the draft listing."


# Get the auth code and the
@app.get("/oauth")
def oauth():

    '''This endpoint will handle getting the auth code and authenticate with Etsy.'''

    # Create a payload to use if needed
    payload = {
        'response_type': response_type,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'client_id': client_id,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': code_challenge_method,
    }

    # Check first if there is a local original access_token file.
    if os.path.exists(original_token) and (current_time - mod_time) > timedelta(hours=1) and not (current_time - mod_time) >= timedelta(days=90):

        with open(original_token, "r") as json_file:

            token_data = json.load(json_file)
            # Pull out the refresh token
            refresh_token = token_data['refresh_token']

        payload_refresh = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'refresh_token': refresh_token,
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # send the refresh token post request
        response = requests.post(etsy_token_url, data=payload_refresh, headers=headers)

        if response.status_code == requests.codes.ok:
            token_data = response.json()
            global access_token

            # Create a local file to store the access_token 
            with open(original_token, "w") as output_file:
                json.dump(token_data, output_file)

            access_token = token_data['access_token']
           
            return RedirectResponse("http://localhost:5000/draft")
        else:
            return response.json()

    elif not os.path.exists(original_token) or (current_time - mod_time) >= timedelta(days=90):
        # Since the modification date of the token file is more than 90 days OR
        # The file doesn't exist then get a new access_token with a refresh_token
        url = requests.get('https://www.etsy.com/oauth/connect', params=payload)
        return RedirectResponse(f"{url.url}")

    else:
        # Here is the case where the token file is still pretty young (within 1 hour of creating it)
        # so we will just use the same access_token otherwise we will have to make a new one
        # or annoy Etsy some more for an access token.
        if os.path.exists(original_token):
            with open(original_token, "r") as json_file:

                token_data = json.load(json_file)
                # pull out the access_token from the data
                access_token = token_data['access_token']

            return RedirectResponse("http://localhost:5000/draft")
        else:
            return "There was an error reading the token file"


# This is an automation for posting up the draft posting to Etsy MAIN CAKE
@app.get("/draft")
def draft():

    '''This function will pass the payload to create a draft for 
    an Etsy Listing'''

    url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings"

    headers = {
        'x-api-key': client_id,
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    payload = get_draft_payload()

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 201:
        draft_data = response.json()
        global listing_id
        listing_id = draft_data["listing_id"]
        return RedirectResponse("http://localhost:5000/images")
    else:
        return "Something went wrong"


# This will post the images on the given draft listing
@app.get("/images")
def images():

    '''This function will handle posting the images to the Draft listing.'''

    headers = {
        'x-api-key': client_id,
        'Authorization': f'Bearer {access_token}',
    }

    url = f"https://openapi.etsy.com/v3/application/shops/{shop_id}/listings/{listing_id}/images"

    for file_name in os.listdir(etsy_images_path):

        payload = {}

        file_path = os.path.join(os.path.abspath(etsy_images_path), file_name)

        with open(file_path, "rb") as this_image:
            payload['image'] = this_image
            response = requests.post(url, files=payload, headers=headers)

    if response.status_code == 201:
        data = response.json()
        return "All Images were posted up and the draft is ready. You may close this server."
    else:
        return json.dumps(response.json())


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)