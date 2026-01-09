import os 
from dotenv import load_dotenv

load_dotenv() 

class Config: 
    CLIENT_ID = os.getenv("Client_ID")
    CLIENT_SECRET = os.getenv("Client_Secret")
    #Change this later
    SECRET_KEY = 'secret'
    
