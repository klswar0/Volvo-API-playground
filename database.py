from classCar import Car, Oauth2

from datetime import datetime, timezone

database = {
    "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID")],
    "all_values": [Car(VIN="VIN321", fuelType="HYBRID",)], #add diffrent values for testing
    "vcc_api_key_Oauth2": [Car(VIN="VIN123", fuelType="HYBRID")]
}

#client id == api key for this playground
Oauth2Data={
    "vcc_api_key_Oauth2": Oauth2(client_secret="client_secret", code="code", access_token="access_token", refresh_token="refresh_token")
}