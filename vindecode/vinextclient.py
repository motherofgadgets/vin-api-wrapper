import requests


class VINExternalClient:
    endpoint = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/"

    def get_vin(self, vin):
        response = requests.get(url="".join([self.endpoint, vin, "?format=json"]))
        data = response.json()
        if response.status_code == 200 and data["Count"] > 0:
            return data["Results"][0]


class VINTestClient:
    success_vin = {
        "ErrorCode": '0',
        "Make": "TestMake",
        "Model": "TestModel",
        "ModelYear": "TestModelYear",
        "BodyClass": "TestBodyClass",
    }

    def get_vin(self, vin):
        if vin == "1XPWD40X1ED215307":
            return self.success_vin


if __name__ == '__main__':
    client = VINExternalClient()
    end_result = client.get_vin("19XZE4F95KE027095")
