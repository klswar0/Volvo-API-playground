from classCar import Car, AdditionalData, Oauth2, Scopes


from datetime import datetime, timezone

database = {
    "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID")],
    "all_values": [
        Car(
            VIN="VIN321",
            fuelType="HYBRID",
            frontLeftWindow="OPEN",
            frontRightWindow="CLOSED",
            rearLeftWindow="AJAR",
            rearRightWindow="UNSPECIFIED",
            sunroof="OPEN",
            centralLock="LOCKED",
            frontLeftDoor="OPEN",
            frontRightDoor="CLOSED",
            rearLeftDoor="AJAR",
            rearRightDoor="UNSPECIFIED",
        ),
        Car(
            VIN="VIN322",
            fuelType="ELECTRIC",
            fuelElectric=100,
            engineStatus="RUNNING",
            availabilityStatus_value="AVAILABLE",
            frontLeft="NO_WARNING",
            frontRight="VERY_LOW_PRESSURE",
            rearLeft="LOW_PRESSURE",
            rearRight="HIGH_PRESSURE",
        ),
        Car(
            VIN="VIN323",
            fuelType="PETROL",
            fuelICE=55,
            odometer=12345,
            serviceWarning="REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE",
            serviceTrigger="DISTANCE",
            tankLid="OPEN",
            hood="CLOSED",
            tailGate="AJAR",
        ),
    ],
    "vcc_api_key_Oauth2": [Car(VIN="VIN123", fuelType="HYBRID")]
}

#client id == api key for this playground
# could we changes this to additonal data for scopes?
AdditionalDatabase={
    "vcc_api_key_Oauth2": AdditionalData(Oauth2Data=Oauth2(client_secret="client_secret", code="code", access_token="access_token", refresh_token="refresh_token")),
    "vcc_api_key": AdditionalData(ScopesData=Scopes(scopes=["openid","conve:vehicle_relation"])),
    "all_values": AdditionalData()
}

def createCar(api_key: str, car: Car):
    if api_key in database:
        database[api_key].append(car)
    else:
        database[api_key] = [car]
        
    if api_key not in AdditionalDatabase:
        AdditionalDatabase[api_key] = AdditionalData()