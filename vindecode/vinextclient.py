import requests

ENDPOINT = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"


class VINExternalClient:
    def get_vin(self, vin):
        response = requests.get(url="".join([ENDPOINT, vin, "?format=json"]))
        data = response.json()
        return data


if __name__ == '__main__':
    client = VINExternalClient()
    end_result = client.get_vin("19XZE4F95KE027095")
