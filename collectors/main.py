import os
from dotenv import load_dotenv
import requests

# Load .env
load_dotenv()
API_KEY = os.getenv("ABUSEIPDB_KEY")
