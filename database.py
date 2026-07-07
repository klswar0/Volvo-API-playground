from classCar import Car, Oauth2

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
Oauth2Data={
    "vcc_api_key_Oauth2": Oauth2(client_secret="client_secret", code="code", access_token="access_token", refresh_token="refresh_token")
}