import requests
from fastapi import HTTPException


class VINExternalClient:
    """
    A client that exists solely to make outgoing requests to the external VIN API
    """

    endpoint = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

    def get_vin(self, vin):
        response = requests.get(url="".join([self.endpoint, vin, "?format=json"]))
        if response.status_code == 200:
            data = response.json()
            return data["Results"][0]
        else:
            # Pass any exceptions from external API to this API
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
