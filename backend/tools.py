import os 
from datetime import datetime
import pyttsx3
import msal
from dotenv import load_dotenv
import requests
import json
from datetime import datetime

def get_contact(name: str):
    if "myself" in name: 
        return ""
    return "1234@gmail.com"

def confirm(question: str): 
    answer = input(question)
    return answer

def get_date():
    return datetime.now()
    
def get_access_token(user_id:str): 
    load_dotenv() 

    CLIENT_ID = os.getenv("Client_ID")
    CLIENT_SECRET = os.getenv("Client_Secret")

    if not CLIENT_ID or not CLIENT_SECRET: 
        raise ValueError("API_KEY not set")
    
    TENANT = "common" 
    AUTHORITY = f"https://login.microsoftonline.com/{TENANT}"
    SCOPES = ["Calendars.ReadWrite"]
    CACHE_FILE = f"token_cache/{user_id}.bin"
    
    cache = msal.SerializableTokenCache()
    if os.path.exists(CACHE_FILE):
        cache.deserialize(open(CACHE_FILE, "r").read())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    accounts = app.get_accounts()
    
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
    else: 
        #Propagate an exception
        result = None

    with open(CACHE_FILE, "w") as f:
        f.write(cache.serialize())

    access_token = result["access_token"]
    
    return access_token


def create_event(user_id:str, start:datetime, end:datetime, participants: list, subject:str, location:str,  description:str = ""):
    access_token = get_access_token(user_id)
    url = "https://graph.microsoft.com/v1.0/me/calendar/events"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    attendees = [
        {
            "emailAddress": {
                "address": email,
                "name": email
            },
            "type": "required"
        }
        for email in participants
    ]

    event = {
        "subject": subject,
        "start": {
            "dateTime": start,
            "timeZone": "America/Toronto"
        },
        "end": {
            "dateTime": end,
            "timeZone": "America/Toronto"
        },
        "location": {
            "displayName": location
        },
        "attendees": attendees,
        "body": {
            "contentType": "HTML",
            "content": description
        }
    }

    response = requests.post(url, headers=headers, json=event)

    print(response.status_code)
    print(response.json())

    