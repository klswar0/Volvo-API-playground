from fastapi import Body, FastAPI, Header ,Request ,Query, Response, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import JSONResponse, FileResponse ,HTMLResponse 
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

import json
import secrets
from copy import deepcopy


from notifier import notifier
from classCar import Car, options, config, timestampGenerator, Oauth2,Scopes
from database import database, AdditionalDatabase,createCar
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal

#internal endpoints 


def Internal():
    return JSONResponse(content={"message": "Welcome to the internal API", "description": config.items()}, status_code=200) # here will be displayed any options like authetication using tokens and so on.


def Terminal(VIN: str, key: str, request: Request):
    return templates.TemplateResponse(name="terminal.html", request=request, context={"VIN": VIN, "key": key})


#OAuth2 endpoints for testing and dashboard purposes. Not part of the official API.

def OAuthActivateInternal(vcc_api_key:str = Header(...),client_secret:str = Body(...),PKCE:bool = Body(...),redirect_uri:str = Body(default="")):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"Invalid API key"}}, status_code=401)
    else:
        if vcc_api_key not in AdditionalDatabase or AdditionalDatabase[vcc_api_key].Oauth2Data is None:
            oauth2 = Oauth2(client_secret=client_secret, PKCE=PKCE,redirect_uri=redirect_uri)
            AdditionalDatabase[vcc_api_key].Oauth2Data = oauth2
            return JSONResponse(content={"message": "OAuth2 activated successfully"}, status_code=200)
        elif AdditionalDatabase[vcc_api_key].Oauth2Data.PKCE != PKCE or AdditionalDatabase[vcc_api_key].Oauth2Data.client_secret != client_secret or AdditionalDatabase[vcc_api_key].Oauth2Data.redirect_uri != redirect_uri:
            oauth2 = Oauth2(client_secret=client_secret, PKCE=PKCE,redirect_uri=redirect_uri)
            AdditionalDatabase[vcc_api_key].Oauth2Data = oauth2
            return JSONResponse(content={"message": "OAuth2 updated successfully"}, status_code=200)
        else:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"OAuth2 already activated for this API key"}}, status_code=400)
        
def OAuthDeactivateInternal(vcc_api_key:str = Header(...)):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"Invalid API key"}}, status_code=401)
    else:
        if vcc_api_key not in AdditionalDatabase or AdditionalDatabase[vcc_api_key].Oauth2Data is None:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"OAuth2 already deactivated for this API key"}}, status_code=400)
        else:
            AdditionalDatabase[vcc_api_key].Oauth2Data = None
            return JSONResponse(content={"message": "OAuth2 deactivated successfully"}, status_code=200)
        
def OAuthRegenerateInternal(vcc_api_key:str = Header(...)):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"Invalid API key"}}, status_code=401)
    else:
        if vcc_api_key not in AdditionalDatabase or AdditionalDatabase[vcc_api_key].Oauth2Data is None:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"OAuth2 not activated for this API key"}}, status_code=400)
        else:
            oauth2=AdditionalDatabase[vcc_api_key].Oauth2Data
            oauth2.client_secret = "client_secret_"+secrets.token_urlsafe(32)
            oauth2.code = ""
            oauth2.access_token =  "access_token_"+secrets.token_urlsafe(32)
            oauth2.refresh_token = "refresh_token_"+secrets.token_urlsafe(32)
            #oauth2.expires_in = 
            data={"access_token": oauth2.access_token, "refresh_token": oauth2.refresh_token, "token_type": "Bearer", "expires_in": 3599}
            return JSONResponse(content=data, status_code=200)

def OAuthGetInternal(vcc_api_key:str = Header(...)):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"Invalid API key"}}, status_code=401)
    else:
        if vcc_api_key not in AdditionalDatabase or AdditionalDatabase[vcc_api_key].Oauth2Data is None:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"OAuth2 not activated for this API key"}}, status_code=400)
        else:
            oauth2=AdditionalDatabase[vcc_api_key].Oauth2Data
            data={"client_secret": oauth2.client_secret, "code": oauth2.code, "access_token": oauth2.access_token, "refresh_token": oauth2.refresh_token, "token_type": "Bearer", "expires_in": 3599, "redirect_uri": oauth2.redirect_uri}
            return JSONResponse(content=data, status_code=200)


# scopes

def setScopesInternal(vcc_api_key:str = Header(...),scopes: list = Body(default=None)):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return JSONResponse(content={"error": {"message": "UNAUTHORIZED","description": f"Invalid API key"}}, status_code=401)
    else:
        if scopes is None or scopes == []:
            AdditionalDatabase[vcc_api_key].Scopes = None
            return JSONResponse(content={"message": "Scopes disabled successfully"}, status_code=200)
        else:
            if vcc_api_key not in AdditionalDatabase or AdditionalDatabase[vcc_api_key].Scopes is None:
                AdditionalDatabase[vcc_api_key].Scopes = Scopes()
            scope=AdditionalDatabase[vcc_api_key].Scopes
            for s in scopes:
                if not scope.addScope(s):
                    return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"Invalid scope: {s}"}}, status_code=400)
        return JSONResponse(content={"message": "Scopes set successfully"}, status_code=200)
            

#internal endpoints for testing and dashboard purposes. Not part of the official API.


def authenticateInternal(vcc_api_key: str):
    if vcc_api_key not in database:
        raise ValueError("Invalid API key")
    
def VINHandlingInternal(VIN:str, vcc_api_key: str):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError:
        raise ValueError("Invalid API key")
    for car in database[vcc_api_key]:
        if car.VIN == VIN:
            return car
    raise ValueError("Invalid VIN")
    
def update(VIN:str, attribute: str, value: str, vcc_api_key: str):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        value = car.update(attribute, value,True)
        if value == True and (config["DEFAULT"]["statusNotification"] == "SET" or config["DEFAULT"]["statusNotification"] == "ALL"):
            notifier.trigger_update(VIN, car, attribute)
        return value 
    except ValueError as e:
        raise ValueError(str(e))



def getStatus(VIN: str = Header(...),vcc_api_key: str = Header(...)):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        data = car.model_dump()
        return JSONResponse(content=data, status_code=200)

    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponseInternal()
        elif str(e) == "Invalid VIN":
            return BadRequestResponseInternal(VIN)
        

async def statusWS(websocket: WebSocket):
    await websocket.accept()
    
    if config["DEFAULT"]["Websocket"] == "False":
        await websocket.send_text("{\"error\": {\"message\": \"BAD_REQUEST\",\"description\": \"Websocket is disabled in the configuration.\"}}")
        await websocket.close()
        return
    
    params = websocket.query_params
    vin = params.get("VIN")
    api_key = params.get("key")
    queue = notifier.subscribe(vin)

    try:
        car = VINHandlingInternal(vin, api_key)
        if not car:
            raise ValueError("Car not found or invalid API key")
        car_data = car.model_dump()
        await websocket.send_text(json.dumps(car_data))
        
        while True:
            packet = await queue.get()
    
            packet["key"] = api_key
            
            
            await websocket.send_text(json.dumps(packet))
            
    except WebSocketDisconnect:
        print("Dashboard disconnected")
    except ValueError as e:
        await websocket.send_text("Invalid API key or VIN")
        await websocket.close()
        return
    finally:
        notifier.unsubscribe(vin, queue)
        print(f"Disconnected car: {vin} with key: {api_key}")


def internal_update(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: str = Body(...), value: str = Body(...)):
    try:
        response=update(VIN, attribute, value, vcc_api_key)
        if response:
            return JSONResponse(content={"message": f"THIS IS INTERNAL API/attribute {attribute} updated successfully"}, status_code=200)
        else:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute}"}}, status_code=400)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponseInternal()
        elif str(e) == "Invalid VIN":
            return BadRequestResponseInternal(VIN)
        else:
            return JSONResponse(
            content={"error": {"message": "VALUE_ERROR", "description": str(e)}}, 
            status_code=400
            )



def internal_updates(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: list = Body(...), value: list = Body(...)):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        if len(attribute) != len(value):
            return JSONResponse(content={"error": {"message": "BAD_REQUEST", "description": "THIS IS INTERNAL API/attribute and value lists must have the same length"}}, status_code=400)

        update_data = dict(zip(attribute, value))
        validity = car.checkValidityMultiple(update_data)
        if validity is not True:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST", "description": f"THIS IS INTERNAL API/invalid attribute or value. field:{validity[1]}"}}, status_code=400)

        for attr, val in update_data.items():
            car.update(attr, val, True)

        if config["DEFAULT"]["statusNotification"] == "ALL" or config["DEFAULT"]["statusNotification"] == "SET":
            notifier.trigger_update_multiple(VIN, car, list(update_data.keys()))

        return JSONResponse(content={"message": f"THIS IS INTERNAL API/attributes updated successfully"}, status_code=200)

    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponseInternal()
        elif str(e) == "Invalid VIN":
            return BadRequestResponseInternal(VIN)
        else:
            return JSONResponse(
            content={"error": {"message": "VALUE_ERROR", "description": str(e)}}, 
            status_code=400
            )



def genAPIKey():                    
    api_key=secrets.token_hex(16)
    database[api_key] = []
    return JSONResponse(content={"message": api_key,"description": f"THIS IS INTERNAL API/API key generated successfully"}, status_code=200)


def addCar(vcc_api_key: str = Header(...), VIN: str = Body(...), attributes: dict = Body(default={})):
    try:
        cars =database[vcc_api_key]
        if any(car.VIN == VIN for car in cars):
            return BadRequestResponseInternal(VIN)
        
        new_car = Car(VIN=VIN)
        for attribute in attributes.keys():
            try:
                new_car.update(attribute, attributes[attribute],True)
            except ValueError:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute}"}}, status_code=400)

        createCar(vcc_api_key, new_car)
        return JSONResponse(content={"message": f"THIS IS INTERNAL API/Car added successfully: {VIN}"}, status_code=200)

    except KeyError:
        return UnauthorizedResponseInternal()
    
#def removeCar

   

def delCar(vcc_api_key: str = Header(...), VIN: str = Body(...), attributes: dict = Body(default={})): #add to DOCS
    try:
        cars =database[vcc_api_key]
        for i, car in enumerate(cars):
            if car.VIN == VIN:
                del cars[i]
                return JSONResponse(content={"message": f"THIS IS INTERNAL API/Car deleted successfully: {VIN}"}, status_code=200)
        return BadRequestResponseInternal(VIN)

    except KeyError:
        return UnauthorizedResponseInternal()

