# Import Packages
from getpass import getpass
import json
import geopandas as gpd
import requests
import sys
from functions import list_datasets

# # Define EE M2M API Endpoint
# url = "https://m2m.cr.usgs.gov/api/api/json/stable/"

# # "data": "eyJjaWQiOjI3MDMzMjE4LCJzIjoiMTczMDgyNzg1NCIsInIiOjgxLCJwIjpbInVzZXIiLCJkb3dubG9hZCIsIm9yZGVyIl19",

# # Define prompts for logging in
# # p = ["Enter EROS Registration System (ERS) Username: ", "Enter ERS Account Password: "]
# # Read the token from the file
# token_file_path = r"C:\Users\Stefano\Desktop\3_Semester\TESI\USGS\USGS_TOKEN.txt"

# # Read the token from the file
# with open(token_file_path, "r") as file:
#     token = file.read().strip()

# serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
# url = serviceUrl + "login-token"
# # login-token
# payload = {"username": "Stefano98", "token": token}
# json_data = json.dumps(payload)
# response = requests.post(url, json_data)
# try:
#     httpStatusCode = response.status_code
#     if response == None:
#         print("No output from service")
#         sys.exit()
#     output = json.loads(response.text)
#     if output["errorCode"] != None:
#         print(output)
#         sys.exit()
#     if httpStatusCode == 404:
#         print("404 Not Found")
#         sys.exit()
#     elif httpStatusCode == 403:
#         print("401 Unauthorized")
#         sys.exit()
#     elif httpStatusCode == 500:
#         print("Error Code", httpStatusCode)
#         sys.exit()
# except Exception as e:
#     response.close()
#     print(e)

# response.close()
# apiKey = output["data"]
# print("API Key: " + apiKey)

serviceUrl = "https://m2m.cr.usgs.gov/api/api/json/stable/"
login_url = serviceUrl + "login"

pw_file = r"C:\Users\Stefano\Desktop\3_Semester\TESI\USGS\USGS_PW.txt"
with open(pw_file, "r") as file:
    pw = file.read().strip()

login_payload = {
    "username": "Stefano98",
    "password": pw,
}  # Replace with your actual password
response = requests.post(login_url, json=login_payload)
login_results = response.json()

# Check for login success
if login_results.get("errorCode"):
    print("Login Error:", login_results["errorMessage"])
else:
    token = login_results["data"]  # Retrieve API key if login is successful
    print("Login successful, token:", token)
    # Call the list_datasets function to get available datasets
    available_datasets = list_datasets(token, serviceUrl)
    print("Available datasets:", available_datasets)

# Load bounding box coordinates from shapefile
shapefile_path = (
    r"C:\Users\Stefano\Desktop\3_Semester\TESI\BBOX\BB_MetropolitanCityOfMilan.shp"
)
gdf = gpd.read_file(shapefile_path)
bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]

# Define lower-left and upper-right points from the bounding box
ll = {"longitude": bounds[0], "latitude": bounds[1]}
ur = {"longitude": bounds[2], "latitude": bounds[3]}

# Define dataset and catalog node for Landsat 8
dataset = "LANDSAT_8_C2_L2"
catalog_node = "EE"

# Set up the payload for scene_search
search_payload = {
    "datasetName": dataset,
    "catalog": catalog_node,
    "temporalFilter": {"start": "2015-06-27", "end": "2016-06-27"},
    "spatialFilter": {
        "filterType": "mbr",  # "mbr" for minimum bounding rectangle
        "lowerLeft": ll,
        "upperRight": ur,
    },
}
# Send request to scene_search endpoint
search_url = serviceUrl + "scene-search"
headers = {"X-Auth-Token": token}
# Set the search request headers with the obtained token
headers = {"X-Auth-Token": token}
response = requests.post(search_url, headers=headers, json=search_payload)
search_results = response.json()

# Check for search request errors
if search_results.get("errorCode"):
    print("Search Error:", search_results["errorMessage"])
else:
    print("Search results:", json.dumps(search_results, indent=2))


# dataset = "ccdc_v1_3"
# catalog_node = "EE"
# bbox = [44.1, -111.1, 45, -109.7]
# # Set up the payload for scene_search
# search_payload = {
#     "datasetName": dataset,
#     "catalog": catalog_node,
#     "temporalFilter": {"start": "1985-01-01", "end": "1994-12-31"},
#     "spatialFilter": {
#         "filterType": "mbr",
#         "lowerLeft": {"latitude": bbox[0], "longitude": bbox[1]},
#         "upperRight": {"latitude": bbox[2], "longitude": bbox[3]},
#     },
# }
