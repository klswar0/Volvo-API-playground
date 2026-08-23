

import json
from copy import deepcopy
from os import name

from fastapi.encoders import jsonable_encoder
from fastapi import Body, Header 
from fastapi.responses import JSONResponse
from classCar import Car, AdditionalData
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal
from internal import VINHandlingInternal, authenticateInternal
from notifier import notifier
from database import AdditionalDatabase, database

class Snapshots:
    def __init__(self, mainData: list[Car], Additional: AdditionalData | None):
        self.mainData = mainData
        self.Additional = Additional
    mainData: list[Car]
    Additional: AdditionalData


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
                additional_data_dict = snapshot.get("Additional")
                if additional_data_dict is not None:
                    oauth_data = AdditionalData(**additional_data_dict)
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
            "OauthData": snapshot.Additional.model_dump() if snapshot.Additional is not None else None
        }
    with open("snapshots.json", "w") as file:
        json.dump(data_to_save, file, indent=4)


def loadSnapshots(vcc_api_key:str, name:str):
    if name in snapshotsData.keys():
        storage = snapshotsData[name]
        database[vcc_api_key] = deepcopy(storage.mainData)
        for car in database[vcc_api_key]:
            car_instance = VINHandlingInternal(car.VIN, vcc_api_key)
            notifier.trigger_update_multiple(car.VIN, car_instance, list(car.model_dump().keys()))
        if storage.Additional is not None:
            AdditionalDatabase[vcc_api_key] = deepcopy(storage.Additional)
        else:
            if vcc_api_key in AdditionalDatabase:
                del AdditionalDatabase[vcc_api_key]
        return True,name
    else:
        return False, name
  
def saveSnapshots(vcc_api_key:str, name:str):
    if vcc_api_key not in AdditionalDatabase.keys():
        storage = Snapshots(mainData=deepcopy(database[vcc_api_key]), Additional=None)
    else:
        storage = Snapshots(mainData=deepcopy(database[vcc_api_key]), Additional=deepcopy(AdditionalDatabase[vcc_api_key]))
    snapshotsData[name] = storage
    return True,name
   
def snapshots(vcc_api_key:str,command:str,name:str):
    try:
        authenticateInternal(vcc_api_key)
        if command == "save":
            response = saveSnapshots(vcc_api_key, name)
            if response[0] == True:
                try:
                    saveFileSnapshots()
                except Exception as e:
                    print(f"Error saving snapshots to file: {e}")
                    
                return JSONResponse(content={"message": f"Snapshot '{response[1]}' saved successfully."}, status_code=200)
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/internal error"}}, status_code=500)
        elif command == "load":
            response = loadSnapshots(vcc_api_key, name)
            if response[0]==True:
               return JSONResponse(content={"message": f"Snapshot '{response[1]}' loaded successfully."}, status_code=200)
            elif response[0] == False:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid snapshot name: {response[1]}"}}, status_code=400)
        else:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid command: {command}"}}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"THIS IS INTERNAL API/Invalid API key", "details": str(e)}}, status_code=401)