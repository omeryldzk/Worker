import requests
from google.cloud import storage
import json
from flask import Flask, jsonify
import os

# Path to the service account JSON key inside the container
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "/app/service_account.json")

app = Flask(__name__)

# Cloud Run API URL
CLOUD_RUN_API_URL = "https://footballapi-936574418751.us-central1.run.app/api/football"

# Initialize Google Cloud Storage client
client = storage.Client()

def fetch_leagues():
    """Fetch league information from the Cloud Run API."""
    try:
        response = requests.get(CLOUD_RUN_API_URL + "/leagues")
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching leagues: {e}")
        return []

def fetch_leagues_fixtures(request):
    """Fetch league information from the Cloud Run API."""
    try:
        response = requests.get(request)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching leagues: {e}")
        return []
    
def fetch_leagues_standings(request):
    """Fetch league information from the Cloud Run API."""
    try:
        response = requests.get(request)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching leagues: {e}")
        return []

def create_bucket(bucket_name):
    """Create a bucket in Google Cloud Storage."""
    client = storage.Client()
    try:
        bucket = client.bucket(bucket_name)
        bucket.storage_class = "COLDLINE"
        new_bucket = client.create_bucket(bucket, location="US")
        print(f"Bucket {new_bucket.name} created.")
        return new_bucket
    except Exception as e:
        print(f"Error creating bucket {bucket_name}: {e}")
        return None

def worker():
    """Fetch leagues from API and create buckets."""
    leagues = fetch_leagues()
    bucket = client.get_bucket("archonph-footballapi-2024")

    for league in leagues:
        league_name = league.get("name")
        league_id = league.get("id")
        
        fixture_request = CLOUD_RUN_API_URL + "/fixtures/" + str(league_id)
        standing_request = CLOUD_RUN_API_URL + "/standings/" + str(league_id)
        # Make bucket names unique (GCS bucket names must be globally unique)
        
        blop_name = league_name.lower().replace(" ", "-") + "-bucket"
        subddir_fixture = "footballapi/" + blop_name + "/fixtures"
        subddir_standings = "footballapi/" + blop_name + "/standings"
        
        blob_fixture = bucket.blob(subddir_fixture + "/" + league_name + ".json")
        blob_standing = bucket.blob(subddir_standings + "/" + league_name + ".json")

        # Upload the JSON data as a string to the blob
        fixtures = fetch_leagues_fixtures(fixture_request)
        standings = fetch_leagues_standings(standing_request)
        fixtures_json = json.dumps(fixtures)  # Convert to JSON string
        standings_json = json.dumps(standings)
        blob_fixture.upload_from_string(fixtures_json, content_type="application/json")
        blob_standing.upload_from_string(standings_json, content_type="application/json")
        
        print(f"Creating buckets for league: {league_name}")

@app.route('/trigger-worker', methods=['POST'])
def trigger_worker():
    worker()
    return jsonify({"message": "Worker triggered successfully"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)