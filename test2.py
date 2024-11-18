# comment: ctrl+K then ctrl+C -- uncomment ctrl+K then ctrl+U
# Import Packages
import json
import requests
import sys
import geopandas as gpd
import xarray as rxr
from functions import list_filters, computeBBOX, list_datasets, retriveBandsName

token_file_path = r"C:\Users\Stefano\Desktop\3_Semester\TESI\USGS\USGS_TOKEN.txt"
# Read the token from the file
with open(token_file_path, "r") as file:
    token = file.read().strip()

# Define EE M2M API Endpoint
serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
url = serviceUrl + "login-token"
# login-token
payload = {"username": "Stefano98", "token": token}

response = requests.post(url, json=payload)
login_results = response.json()
# Check for login success
if login_results.get("errorCode"):
    print("Login Error:", login_results["errorMessage"])
    sys.exit(1)
else:
    token = login_results["data"]  # Retrieve API key if login is successful
    print("Login successful, token:", token)
    # available_datasets = list_datasets(token, serviceUrl)

# Load bounding box coordinates from shapefile
shapefile_path = (
    r"C:\Users\Stefano\Desktop\3_Semester\TESI\BBOX\BB_MetropolitanCityOfMilan.shp"
)

lowerLeft, upperRight = computeBBOX(shapefile_path)
# print(lowerLeft, upperRight)
# test_lowerLeft = {"latitude": 44.1, "longitude": -111.1}
# test_upperRight = {"latitude": 45, "longitude": -109.7}

datasetName = "landsat_ot_c2_l2"
# dataset = "Landsat 8-9 OLI/TIRS C2 L2"
# dataset = "landsat_8-9_oli/tirs_c2_l2"
catalogNode = "EE"
startDate = "2015-06-27"
endDate = "2016-31-12"
filterid = "61af9273566bb9a8"

# dataset_filters_payload = {
#     "datasetName": datasetName,
#     "catalog": catalogNode,
# }
# filters_url = serviceUrl + "dataset-filters"
# filters_response = requests.post(
#     filters_url, headers={"X-Auth-Token": token}, json=dataset_filters_payload
# )
# filters_results = filters_response.json()
# filterId = filters_results["data"][5]["id"]
# # print(f"Selected Satellite Filter ID: {filterId}")
# # Check the "Satellite" filter ID and values in your filter list
# for filter_data in filters_results["data"]:
#     if filter_data["fieldLabel"] == "Satellite":
#         print(f"Satellite Filter ID: {filter_data['id']}")
#         print("Available Values:", filter_data["valueList"])

list_filters(datasetName, catalogNode, serviceUrl, token)

# Set up the payload for scene_search
search_payload = {
    "datasetName": datasetName,
    "catalog": catalogNode,
    "temporalFilter": {"start": startDate, "end": endDate},
    "spatialFilter": {
        "filterType": "mbr",  # "mbr" for minimum bounding rectangle
        "lowerLeft": lowerLeft,
        "upperRight": upperRight,
    },
    "sceneFilter": {
        "metadataFilter": {"filterType": "value", "filterId": filterId, "value": "8"}
    },
    # "cloudCoverFilter": {"min": 0, "max": 20},
}

# Send request to scene_search endpoint
search_url = serviceUrl + "scene-search"
headers = {"X-Auth-Token": token}
response = requests.post(search_url, headers=headers, json=search_payload)
search_results = response.json()

# Check for errors and display search results
if search_results.get("errorCode"):
    print("Search Error:", search_results["errorMessage"])
# else:
#     print("Search results:", json.dumps(search_results, indent=2))

# Assuming `search_results` holds the API response data
# filtered_results = [
#     scene
#     for scene in search_results.get("data", {}).get("results", [])
#     if scene.get("displayId", "").startswith("LC08")  # Keep only Landsat 8 scenes
# ]

# print("Filtered Landsat 8 Scenes:")
# for scene in filtered_results:
#     print(f"Scene ID: {scene.get('displayId')}, Cloud Cover: {scene.get('cloudCover')}")
