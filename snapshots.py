

from fastapi import Body, Header 
from fastapi.responses import JSONResponse
from classCar import Oauth2
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal
from internal import VINHandlingInternal, authenticateInternal
from notifier import notifier
from database import Oauth2Data, database

class Snapshots:
    mainData: list 
    OuathData: Oauth2


snapshots = {}




def snapshots(vcc_api_key:str,command:str,name:str):
    try:
        authenticateInternal(vcc_api_key)
        if command == "save":
            storage = Snapshots(mainData=database[vcc_api_key], OuathData=Oauth2Data[vcc_api_key])
            snapshots[name] = storage
            return JSONResponse(content={"message": f"Snapshot '{name}' saved successfully."}, status_code=200)
        elif command == "load":
            if name in snapshots.keys():
                storage = snapshots[name]
                database[vcc_api_key] = storage.mainData
                Oauth2Data[vcc_api_key] = storage.OuathData
                return JSONResponse(content={"message": f"Snapshot '{name}' loaded successfully."}, status_code=200)
            else:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid snapshot name: {name}"}}, status_code=400)
    except:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"THIS IS INTERNAL API/Invalid API key"}}, status_code=401)
