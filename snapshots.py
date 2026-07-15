

import json

from fastapi import Body, Header 
from fastapi.responses import JSONResponse
from classCar import Oauth2
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal
from internal import VINHandlingInternal, authenticateInternal
from notifier import notifier
from database import Oauth2Data, database

class Snapshots:
    def __init__(self, mainData: list, OauthData: Oauth2):
        self.mainData = mainData
        self.OauthData = OauthData
    mainData: list 
    OauthData: Oauth2


snapshotsData = {}

def loadFileSnapshots():
    try:
        with open("snapshots.json","r") as file:
            data = json.load(file)
            for name, snapshot in data.items():
                mainData = snapshot.get("mainData", [])
                oauth_data_dict = snapshot.get("OauthData")
                if oauth_data_dict is not None:
                    oauth_data = Oauth2(**oauth_data_dict)
                else:
                    oauth_data = None
                snapshotsData[name] = Snapshots(mainData=mainData, OauthData=oauth_data)
    except FileNotFoundError:
        print("snapshots.json file not found. Starting with an empty snapshotsData.")

def saveFileSnapshots():
    data_to_save = {}
    for name, snapshot in snapshotsData.items():
        data_to_save[name] = {
            "mainData": snapshot.mainData,
            "OauthData": snapshot.OauthData.model_dump() if snapshot.OauthData is not None else None
        }
    with open("snapshots.json", "w") as file:
        json.dump(data_to_save, file, indent=4)



def snapshots(vcc_api_key:str,command:str,name:str):
    try:
        authenticateInternal(vcc_api_key)
        if command == "save":
            if vcc_api_key not in Oauth2Data.keys():
                storage = Snapshots(mainData=database[vcc_api_key].copy(deep=True), OauthData=None)
            else:
                storage = Snapshots(mainData=database[vcc_api_key].copy(deep=True), OauthData=Oauth2Data[vcc_api_key].copy(deep=True))
            snapshotsData[name] = storage
            return JSONResponse(content={"message": f"Snapshot '{name}' saved successfully."}, status_code=200)
        elif command == "load":
            if name in snapshotsData.keys():
                storage = snapshotsData[name]
                database[vcc_api_key] = storage.mainData.copy(deep=True)
                if storage.OauthData is not None:
                    Oauth2Data[vcc_api_key] = storage.OauthData.copy(deep=True)
                else:
                    if vcc_api_key in Oauth2Data:
                        del Oauth2Data[vcc_api_key]
                return JSONResponse(content={"message": f"Snapshot '{name}' loaded successfully."}, status_code=200)
            else:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid snapshot name: {name}"}}, status_code=400)
    except Exception as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"THIS IS INTERNAL API/Invalid API key", "details": str(e)}}, status_code=401)
