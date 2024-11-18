# Functions.py
import json
import requests
import geopandas as gpd
import threading
import os
import sys
import re

# Landsat 8-9 OLI/TIRS C2 L2


def list_datasets(token, service_url, catalog_node="EE"):
    """
    List available datasets in a given catalog node.

    Parameters:
        token (str): The API token for authentication.
        service_url (str): The base URL of the USGS API.
        catalog_node (str): Catalog node, default is 'EE' (Earth Explorer).

    Returns:
        list: A list of available dataset names.
    """
    # Define dataset listing URL
    dataset_url = service_url + "dataset-search"
    dataset_payload = {"datasetName": None, "catalog": catalog_node, "publicOnly": True}

    # Send request to list available datasets
    headers = {"X-Auth-Token": token}
    response = requests.post(dataset_url, headers=headers, json=dataset_payload)

    # print("Status code:", response.status_code)  # Print status code for debugging
    # print("Response text:", response.text)  # Print full response for debugging

    dataset_results = response.json()
    # print("Dataset API response:", json.dumps(dataset_results, indent=2))

    # Check for errors in the response
    if dataset_results.get("errorCode"):
        print("Dataset Listing Error:", dataset_results["errorMessage"])
        return []
    # Process 'data' field if it contains datasets
    data = dataset_results.get("data")
    if data and isinstance(data, list):  # Ensure data is a list
        datasets = [
            dataset.get("collectionName")
            for dataset in data
            if "collectionName" in dataset
        ]
        print("Available datasets:", datasets)
        return datasets
    else:
        print("No datasets found or unexpected data structure.")
        return []


def computeBBOX(shapefile_path):

    gdf = gpd.read_file(shapefile_path)
    #aoi_geodf = gpd.read_file(shapefile_path)
    # print("Pre trnsformation", aoi_geodf.crs)
    gdf = gdf.to_crs("EPSG:4326")
    # print("Post trnsformation", gdf.crs)
    bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]

    # Define lower-left and upper-right points from the bounding box
    ll = {"longitude": bounds[0], "latitude": bounds[1]}
    ur = {"longitude": bounds[2], "latitude": bounds[3]}
    return ll, ur


def list_filters(datasetName, catalogNode, serviceUrl, token):
    # Define the payload for dataset-filters request
    dataset_filters_payload = {
        "datasetName": datasetName,  # Ensure this is your correct dataset name
        "catalog": catalogNode,  # Earth Explorer catalog
    }

    # URL for the dataset-filters endpoint
    filters_url = serviceUrl + "dataset-filters"

    # Send request to get dataset filters
    filters_response = requests.post(
        filters_url, headers={"X-Auth-Token": token}, json=dataset_filters_payload
    )
    filters_results = filters_response.json()

    # Check for errors
    if filters_results.get("errorCode"):
        print("Filter Retrieval Error:", filters_results["errorMessage"])
    else:
        # Print available filters for inspection
        print("Dataset Filters:", json.dumps(filters_results, indent=2))
    print(filters_results.get("data"))


# NOT SO USEFUL
def filterToSelectLandsat(datasetName, catalogNode, serviceUrl, token):
    dataset_filters_payload = {
        "datasetName": datasetName,
        "catalog": catalogNode,
    }
    filters_url = serviceUrl + "dataset-filters"
    filters_response = requests.post(
        filters_url, headers={"X-Auth-Token": token}, json=dataset_filters_payload
    )
    filters_results = filters_response.json()
    filterId = filters_results["data"][5]["id"]
    # print(f"Selected Satellite Filter ID: {filterId}")
    return filterId


def retriveBandsName(search_results, token, serviceUrl, datasetName):
    scenes = search_results.get("data", {}).get("results", [])
    first_scene = scenes[0]
    scene_id = first_scene.get("entityId")
    metadata_url = serviceUrl + "scene-metadata"
    metadata_payload = {
        "datasetName": datasetName,
        "entityIds": [scene_id],  # Requesting metadata for this specific scene
    }

    print("\nProcessing First Scene ID:", first_scene.get("entityId"))
    metadata = first_scene.get("metadata", [])
    headers = {"X-Auth-Token": token}
    # Send the metadata request
    metadata_response = requests.post(
        metadata_url, headers=headers, json=metadata_payload
    )
    metadata_results = metadata_response.json()

    # Check if metadata contains detailed band information
    if metadata_results.get("errorCode"):
        print("Metadata Retrieval Error:", metadata_results["errorMessage"])
    else:
        # Inspect metadata for band information
        metadata_data = (
            metadata_results.get("data", {}).get(scene_id, {}).get("bands", [])
        )
        if metadata_data:
            print("Band Information for Scene ID", scene_id)
            for band in metadata_data:
                print(
                    f" - Band Name: {band.get('name')}, Description: {band.get('description')}"
                )
        else:
            print("No band information found in detailed metadata.")

    # if metadata:
    #     print("Bands Information for First Scene:")
    #     for item in metadata:
    #         if "Band" in item.get("fieldName", ""):
    #             print(f" - {item['fieldName']}: {item.get('value')}")
    # else:
    #     print("No detailed band information found in metadata for the first scene.")


def plotAoi(aoi_geodf):
    import folium

    centroid_lat = aoi_geodf.geometry.centroid.y.mean()
    centroid_lon = aoi_geodf.geometry.centroid.x.mean()
    m = folium.Map(
        location=[centroid_lat, centroid_lon],
        zoom_start=8,
        tiles="openstreetmap",
        width="90%",
        height="90%",
        attributionControl=False,
    )  # add n estimate of where the center of the polygon would be located\
    # for the location [latitude longitude]
    for _, r in aoi_geodf.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"]).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(
            data=geo_j,
            style_function=lambda x: {
                "fillColor": "blue",
                "color": "black",
                "weight": 2,
                "fillOpacity": 0.3,
            },
        )
        geo_j.add_to(m)
    m  # display map
