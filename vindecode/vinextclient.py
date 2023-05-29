import requests
from fastapi import HTTPException


class VINExternalClient:
    endpoint = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

    def get_vin(self, vin):
        response = requests.get(url="".join([self.endpoint, vin, "?format=json"]))
        if response.status_code == 200:
            data = response.json()
            return data["Results"][0]
        else:
            raise HTTPException(
                status_code=response.status_code, detail=response.json()
            )
