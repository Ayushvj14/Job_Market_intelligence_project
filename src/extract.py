#fetch data
import requests 
import os
from dotenv import load_dotenv
from config import RESULTS_PER_PAGE
load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/"

def fetch_jobs(search_term, page, country):
    url = BASE_URL.format(country=country) + str(page)

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": search_term,
        "results_per_page": RESULTS_PER_PAGE,
        "content-type": "application/json"
    }
    try:
        response = requests.get(
            url,
            params=params,
            timeout=20
        )
        response.raise_for_status()
        return response.json()# here we write return instead of print because we have to 
                           #send return value to the program if we use print function then it will 
                           # just print the data in console due to this we cant store,procces so instead we use return.
    except requests.exceptions.RequestException as e:
        print(
            f"Request failed | "
            f"Country: {country} | "
            f"Search: {search_term} | "
            f"Page: {page} | "
            f"Error: {e}"
        )

        return {}
     

