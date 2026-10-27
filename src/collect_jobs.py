# ============================================================
# JOB MARKET INTELLIGENCE PROJECT
# collect_jobs.py
#
# Purpose:
# Collect job-market data from the Adzuna API.
#
# API limits:
# - 25 requests per minute
# - 250 requests per day
#
# Our target:
# - 16 search terms
# - 15 pages per search term
# - 16 × 15 = 240 requests
#
# We intentionally wait 2.5 seconds between requests
# to stay around 24 requests/minute.
# ============================================================

import time
import requests
import os
from dotenv import load_dotenv
from config import DOMAINS, COUNTRIES, MAX_PAGES

# LOAD ENVIRONMENT VARIABLES

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")

# API CONFIGURATION

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/"

# Adzuna allows 25 requests/minute.
# 2.5 seconds between requests = approximately 24/minute.
REQUEST_DELAY = 2.5

# Maximum number of requests we intend to make today.
# 16 domains × 15 pages = 240 requests.
DAILY_REQUEST_TARGET = 240



# CHECK API CREDENTIALS
if not APP_ID or not APP_KEY:
    raise ValueError(
        "APP_ID or APP_KEY is missing. "
        "Check your .env file."
    )

# FETCH ONE PAGE

def fetch_jobs(search_term, page, country):
    """
    Fetch one page of jobs from Adzuna.

    Parameters
    ----------
    search_term : str
        Job title/search keyword.
    page : int
        API page number.
    country : str
        Adzuna country code, e.g. 'in'
    Returns
    -------
    dict or None
        API response as JSON.
        Returns None if the request fails.
    """

    url = BASE_URL.format(country=country) + str(page)

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": search_term,
        "results_per_page": 50,
        "content-type": "application/json"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        # Raise an exception for HTTP errors.
        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError as error:

        print(
            f"Request failed | "
            f"Country: {country} | "
            f"Search: {search_term} | "
            f"Page: {page} | "
            f"Error: {error}"
        )

        return None

    except requests.exceptions.RequestException as error:

        print(
            f"Request failed | "
            f"Country: {country} | "
            f"Search: {search_term} | "
            f"Page: {page} | "
            f"Error: {error}"
        )

        return None

# COLLECT ALL JOBS
def collect_all_jobs():
    """
    Collect jobs for all configured countries,
    search terms and pages.
    Returns
    -------
    list
        List containing all collected job dictionaries.
    """
    all_jobs = []

    request_count = 0
    successful_requests = 0
    failed_requests = 0

    print("\n" + "=" * 60)
    print("STARTING JOB COLLECTION")
    print("=" * 60)

    print(f"Search terms : {len(DOMAINS)}")
    print(f"Countries    : {len(COUNTRIES)}")
    print(f"Max pages    : {MAX_PAGES}")

    expected_requests = (
        len(DOMAINS)
        * len(COUNTRIES)
        * MAX_PAGES
    )

    print(f"Expected requests: {expected_requests}")
    print(f"Daily target: {DAILY_REQUEST_TARGET}")
    print(f"Delay/request: {REQUEST_DELAY} seconds")
    
    if expected_requests > DAILY_REQUEST_TARGET:
        raise ValueError(
            f"Expected requests ({expected_requests}) "
            f"exceed daily target ({DAILY_REQUEST_TARGET})."
        )

    print("=" * 60)
    # COUNTRY LOOP

    for country_code, country_name in COUNTRIES.items():

        print(
            f"\n{'=' * 60}\n"
            f"COUNTRY: {country_name} ({country_code})\n"
            f"{'=' * 60}")
        # SEARCH TERM LOOP
        for search_term in DOMAINS:
            print(f"\nSearching: {search_term}")
            # PAGE LOOP
            for page in range(1, MAX_PAGES + 1):

                # Stop if we reach our daily target.
                if request_count >= DAILY_REQUEST_TARGET:

                    print(
                        "\nDaily request target reached.")
                    print(
                        f"Requests made: {request_count}")
                    return all_jobs
                # MAKE API REQUEST
                request_count += 1
                print(
                    f"Request {request_count}/"
                    f"{DAILY_REQUEST_TARGET} | "
                    f"{search_term} | "
                    f"Page {page}"
                )
                data = fetch_jobs(
                    search_term,
                    page,
                    country_code
                )

                # WAIT BEFORE NEXT REQUEST
                # This keeps us below the 25 requests/minute
                # rate limit.
                time.sleep(REQUEST_DELAY)
               
                # HANDLE FAILED REQUEST

                if data is None:
                    failed_requests += 1
                    print(
                        f"Skipped | "
                        f"{search_term} | "
                        f"Page {page}"
                    )
                    continue

                # EXTRACT RESULTS
                results = data.get("results", [])
                
                # HANDLE EMPTY PAGE

                if not results:

                    print(
                        f"No jobs returned | "
                        f"{search_term} | "
                        f"Page {page}")
                    # If a page is empty, later pages are
                    # usually unlikely to contain additional
                    # results for this search.
                    break
               
                # ADD JOBS
                all_jobs.extend(results)
                successful_requests += 1
                print(
                    f"Jobs received: {len(results)} | "
                    f"Total jobs: {len(all_jobs)}"
                )
    # COLLECTION SUMMARY
    print("\n" + "=" * 60)
    print("COLLECTION COMPLETED")
    print("=" * 60)
    print(
        f"Total API requests : {request_count}")
    print(
        f"Successful requests: {successful_requests}")
    print(
        f"Failed requests    : {failed_requests}")
    print(
        f"Total jobs collected: {len(all_jobs)}")
    print("=" * 60)
    return all_jobs
# RUN DIRECTLY

if __name__ == "__main__":

    jobs = collect_all_jobs()

    print(
        f"\nFinal jobs collected: {len(jobs)}")