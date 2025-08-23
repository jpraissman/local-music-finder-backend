from src.google_maps.dto.address_components_response_dto import (
    AddressComponentsResponseDTO,
)
from app import API_KEY, GOOGLE_MAPS_MODE
import requests
from requests.exceptions import HTTPError


def get_geocode_response(url: str):
    if GOOGLE_MAPS_MODE == "wifi-free":
        pass
    else:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()


def get_address_components(
    address: str = None, place_id: str = None
) -> AddressComponentsResponseDTO:
    if not address and not place_id:
        raise ValueError("Either address or place_id must be provided.")

    if place_id:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?place_id={place_id}&key={API_KEY}"
    else:
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx/5xx errors

        geo_data = response.json()["results"][0]["geometry"]["location"]
        lat = geo_data["lat"]
        lng = geo_data["lng"]

        formatted_address = response.json()["results"][0]["formatted_address"]

        address_components = response.json()["results"][0]["address_components"]
        for component in address_components:
            if len(component["types"]) > 0:
                if component["types"][0] == "administrative_area_level_2":
                    county = component["long_name"]
                elif component["types"][0] == "locality":
                    town = component["long_name"]

        # TODO: Handle cases where county or town is not found (send email alert)
        return AddressComponentsResponseDTO(
            lat=lat,
            lng=lng,
            address=formatted_address,
            county=county if "county" in locals() else "Unknown",
            town=town if "town" in locals() else "Unknown",
        )
    except HTTPError as e:
        # TODO: Send an email saying we need to look into this issue
        # TODO: Raise exception (can't keep going because we need lat and lng for basic searching)
        pass
    except Exception as e:
        # TODO: Send an email saying we need to look into this issue
        if "lat" in locals() and "lng" in locals() and "formatted_address" in locals():
            return AddressComponentsResponseDTO(
                lat=lat,
                lng=lng,
                county=county if "county" in locals() else "Unknown",
                town=town if "town" in locals() else "Unknown",
                formatted_address=formatted_address,
            )

        # Raise exception (can't keep going because we need lat and lng for basic searching and address)
