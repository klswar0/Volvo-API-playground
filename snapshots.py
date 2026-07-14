

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
