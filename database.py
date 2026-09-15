import base64
import json
import uuid
import secrets

from classCar import Car, AdditionalData, Oauth2, Scopes
from scopes import scopesList
from time import time
from datetime import datetime, timezone
from classCar import readConfig

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
    "vcc_api_key": AdditionalData(ScopesData=Scopes(scopes=["openid","conve:vehicle_relation","location:read"])),
    "all_values": AdditionalData()
}

def createCar(api_key: str, car: Car):
    if api_key in database:
        database[api_key].append(car)
    else:
        database[api_key] = [car]
        
    if api_key not in AdditionalDatabase:
        AdditionalDatabase[api_key] = AdditionalData()
        
        
def tokenGenerator(api_key:str,timeGen:int,scopes:list=None):
    header={"alg": "HS256", "kid": api_key}# api key is used here bc i dont use this data

    if scopes is None:
        scopes=scopesList
    payload={"scope":scopes,"authorization_details": [],"client_id": api_key,"sub":"user", "iss": "https://playground.kls.hackclub.app","aud": "https://playground.kls.hackclub.app","exp": int(timeGen + 3599),"iat": int(timeGen)}
    # TODO
    # if multi user change sub
    # while doing that rewrtie Oauth2 logic (kid)
    #
    if readConfig("DEFAULT","ShortKeys",True)==True:
        signature = secrets.token_urlsafe(2).rstrip("=") 
    signature = secrets.token_urlsafe(16).rstrip("=") # testing secret is used here bc i dont use this data
    return f"{base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')}.{base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')}.{signature}"
#  TODO: add 3 part token generatori header payload signature

def oauth2Generator(api_key:str,oauth2:Oauth2):
    additonal=AdditionalDatabase[api_key]
    scopes=None
    if additonal.ScopesData is not None:
        scopes=list(additonal.ScopesData.scopes)
    
    timeGeneration=time()
    if readConfig("DEFAULT","ShortKeys",True)==True:
        oauth2.access_token = "access_token_"+tokenGenerator(api_key, timeGeneration, scopes=scopes) #generate
        oauth2.refresh_token = "refresh_token_"+base64.urlsafe_b64encode(uuid.uuid4().bytes).decode() #generate
        
    oauth2.access_token = tokenGenerator(api_key, timeGeneration, scopes=scopes) #generate
    oauth2.refresh_token = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip('=') #generate
    oauth2.code = "" #invalidate code
    oauth2.expires_in = time() + 3599 

    return oauth2