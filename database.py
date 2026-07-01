from classCar import Car, Oauth2

from datetime import datetime, timezone

database = {
    "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID", commands=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP","FLASH","HONK", "HONK_AND_FLASH","LOCK","UNLOCK"])],
    "vcc_api_key_Oauth2": [Car(VIN="VIN123", fuelType="HYBRID", commands=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP","FLASH","HONK", "HONK_AND_FLASH","LOCK","UNLOCK"])]
}

#client id == api key for this playground
Oauth2Data={
    "vcc_api_key_Oauth2": Oauth2(client_secret="client_secret", code="code", access_token="access_token", refresh_token="refresh_token")
}