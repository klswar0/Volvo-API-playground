

import json
from copy import deepcopy

from fastapi.encoders import jsonable_encoder
from fastapi import Body, Header 
from fastapi.responses import JSONResponse
from classCar import Car, Oauth2
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal
from internal import VINHandlingInternal, authenticateInternal
from notifier import notifier
from database import Oauth2Data, database

class Snapshots:
    def __init__(self, mainData: list[Car], OauthData: Oauth2 | None):
        self.mainData = mainData
        self.OauthData = OauthData
    mainData: list[Car]
    OauthData: Oauth2 | None


snapshotsData = {}


def decode_main_data(main_data_raw):
    decoded: list[Car] = []
    if isinstance(main_data_raw, list):
        for item in main_data_raw:
            if isinstance(item, Car):
                decoded.append(item)
            elif isinstance(item, dict):
                decoded.append(Car(**item))
    return decoded

def loadFileSnapshots():
    try:
        with open("snapshots.json","r") as file:
            data = json.load(file)
            for name, snapshot in data.items():
                mainData = decode_main_data(snapshot.get("mainData", []))
                oauth_data_dict = snapshot.get("OauthData")
                if oauth_data_dict is not None:
                    oauth_data = Oauth2(**oauth_data_dict)
                else:
                    oauth_data = None
                snapshotsData[name] = Snapshots(mainData=mainData, OauthData=oauth_data)
    except FileNotFoundError:
        print("snapshots.json file not found. Starting with an empty snapshotsData.")
    except Exception as e:
        print(f"Error loading snapshots: {e}")

def saveFileSnapshots():
    data_to_save = {}
    for name, snapshot in snapshotsData.items():
        data_to_save[name] = {
            "mainData": jsonable_encoder(snapshot.mainData),
            "OauthData": snapshot.OauthData.model_dump() if snapshot.OauthData is not None else None
        }
    with open("snapshots.json", "w") as file:
        json.dump(data_to_save, file, indent=4)



def snapshots(vcc_api_key:str,command:str,name:str):
    try:
        authenticateInternal(vcc_api_key)
        if command == "save":
            if vcc_api_key not in Oauth2Data.keys():
                storage = Snapshots(mainData=deepcopy(database[vcc_api_key]), OauthData=None)
            else:
                storage = Snapshots(mainData=deepcopy(database[vcc_api_key]), OauthData=deepcopy(Oauth2Data[vcc_api_key]))
            snapshotsData[name] = storage
            return JSONResponse(content={"message": f"Snapshot '{name}' saved successfully."}, status_code=200)
        elif command == "load":
            if name in snapshotsData.keys():
                storage = snapshotsData[name]
                database[vcc_api_key] = deepcopy(storage.mainData)
                for car in database[vcc_api_key]:
                    car_instance = VINHandlingInternal(car.VIN, vcc_api_key)
                    notifier.trigger_update_multiple(car.VIN, car_instance, list(car.model_dump().keys()))
                if storage.OauthData is not None:
                    Oauth2Data[vcc_api_key] = deepcopy(storage.OauthData)
                else:
                    if vcc_api_key in Oauth2Data:
                        del Oauth2Data[vcc_api_key]
                return JSONResponse(content={"message": f"Snapshot '{name}' loaded successfully."}, status_code=200)
            else:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid snapshot name: {name}"}}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"THIS IS INTERNAL API/Invalid API key", "details": str(e)}}, status_code=401)
