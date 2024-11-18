# comment: ctrl+K then ctrl+C -- uncomment ctrl+K then ctrl+U
# Import Packages
import requests
import sys
import geopandas as gpd
import xarray as rxr
import functionsForDownload
import functions
#import threading
#import os
#import json

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
    apiKey = login_results["data"]  # Retrieve API key if login is successful
    print("Login successful, apiKey:", apiKey)

# Load bounding box coordinates from shapefile
shapefile_path = (
    r"C:\Users\Stefano\Desktop\3_Semester\TESI\BBOX\BB_MetropolitanCityOfMilan.shp"
)

lowerLeft, upperRight = functions.computeBBOX(shapefile_path)

datasetName = "landsat_ot_c2_l2"
catalogNode = "EE"
startDate = "2015-06-27"
endDate = "2016-06-31"
filterid = "61af9273566bb9a8"
#downloadDirectory= r"C:\Users\Stefano\Desktop\3_Semester\TESI\USGS\Results"
downloadDirectory= r"E:\TESI\USGS\Results2"
downloadFileType = 'band_group'
#downloadFileType = "band"
bandNames = {"ST_B10", "ST_QA", "QA_PIXEL"}
fileGroupIds = {"ls_c2l2_st_band"} #surfacte temperature
maxThreads = 5
#sema = threading.Semaphore(value=maxThreads)
#data_dir = os.path.join(downloadDirectory, 'data')
#utils_dir = os.path.join(downloadDirectory, 'utils')

dataset_filters_payload = {
    "datasetName": datasetName,
    "catalog": catalogNode,
}
filters_url = serviceUrl + "dataset-filters"
filters_response = requests.post(
    filters_url, headers={"X-Auth-Token": apiKey}, json=dataset_filters_payload
)
filters_results = filters_response.json()
filterId = filters_results["data"][5]["id"]
# print(f"Selected Satellite Filter ID: {filterId}")
# Check the "Satellite" filter ID and values in your filter list
for filter_data in filters_results["data"]:
    if filter_data["fieldLabel"] == "Satellite":
        print(f"Satellite Filter ID: {filter_data['id']}")
        print("Available Values:", filter_data["valueList"])

# Set up the payload for scene_search
search_payload = {
    "datasetName": datasetName,
    "catalog": catalogNode,
    "sceneFilter": {
        "spatialFilter": {
            "filterType": "mbr",  # "mbr" for minimum bounding rectangle
            "lowerLeft": lowerLeft,
            "upperRight": upperRight,
         },
        'acquisitionFilter': {"start": startDate, "end": endDate},
        'metadataFilter': {"filterType": "value", "filterId": filterId, "value": "8"},
        #'cloudCoverFilter': {'min': 0, 'max': 20}
    }
}

# Send request to scene_search endpoint
search_url = serviceUrl + "scene-search"
headers = {"X-Auth-Token": apiKey}
response = requests.post(search_url, headers=headers, json=search_payload)
search_results = response.json()

#retriveBandsName(search_results)
#retriveBandsName(search_results, apiKey, serviceUrl, datasetName)

# Check for errors and display search results
if search_results.get("errorCode"):
    print("Search Error:", search_results["errorMessage"])
else:
    scenes = search_results.get("data", {}).get("results", [])
    print(f"Number of retrieved elements: {len(scenes)}")
    #print("Search results:", json.dumps(search_results, indent=2))


functionsForDownload.setupOutputDir(downloadDirectory)
functionsForDownload.downloadMain(url, maxThreads, downloadFileType, search_payload, datasetName, serviceUrl, bandNames, apiKey, fileGroupIds, downloadDirectory)

endpoint = "logout"  
if functionsForDownload.sendRequest(serviceUrl + endpoint, None, apiKey) == None:        
    print("\nLogged Out\n")
else:
    print("\nLogout Failed\n")

    
