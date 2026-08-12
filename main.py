
import base64

from fastapi import Body, FastAPI, Header ,Request ,Query, Response, WebSocket, Form
from fastapi.responses import FileResponse, JSONResponse ,HTMLResponse, RedirectResponse 
from fastapi.templating import Jinja2Templates
import uvicorn
import secrets
import hashlib
from typing import Union

from scenarios import scenariosFunc
from snapshots import snapshots,loadFileSnapshots, saveFileSnapshots
import internal
import dashboard
from notifier import notifier
from classCar import Car, options, AuthHeaderPOST,AuthHeaderGET,Tracking,ResponseHeaderGenerator,Tracking, startUp, timestampGenerator, Oauth2
from database import database, Oauth2Data
from readyResponses import ErrorResponse, UnauthorizedResponse, BadRequestResponse, NotSupportedResponse, NormalResponse, autoErrorResponse


templates = Jinja2Templates(directory="templates")


app = FastAPI()

loadFileSnapshots()  # Load snapshots from file at startup

AuthHeader = Union[AuthHeaderPOST, AuthHeaderGET]

@app.get("/")
def index():
    if startUp["Public"]:
        return FileResponse("templates/index.html")
    else:
        return RedirectResponse(url="/internal/welcome")
    
    


        


def authenticate(auth_header: AuthHeader):
    if auth_header.vcc_api_key not in database:
        raise ValueError("Invalid API key")
    if auth_header.vcc_api_key in Oauth2Data:
        if auth_header.authorization != f"Bearer {Oauth2Data[auth_header.vcc_api_key].access_token}":
            raise ValueError("Invalid access token")
    if isinstance(auth_header, AuthHeaderPOST):
        if auth_header.content_type.split(";")[0].lower() != "application/json": #NOTE: lower case to avoid case sensitivity issues checks needed
            raise ValueError("Invalid Content-Type")
    elif isinstance(auth_header, AuthHeaderGET):
        output = auth_header.accept.split(";")[0].lower()
        if output != "application/json" and output != "*/*" and output != "application/*": 
            raise ValueError("Invalid Accept header")
    else:
        raise ValueError("Invalid auth header type")
        
    return True


def VINHandling(VIN:str, auth_header: AuthHeader):
    try:
        authenticate(auth_header)
    except Exception as e:
        raise ValueError(str(e))
    
    for car in database[auth_header.vcc_api_key]:
        if car.VIN == VIN:
            return car
    raise ValueError("Invalid VIN")

# Oauth2.0 section

# DOES NOT IMPLEMENT THE FULL OAUTH2.0 FLOW. IT IS ONLY A SIMULATION FOR TESTING PURPOSES.


def PKCE(code_challenge:str, code_challenge_method:str, oauth2: Oauth2):
    if code_challenge_method == "S256":
        oauth2.code_challenge = code_challenge
        oauth2.code_challenge_method = code_challenge_method
        return True
    elif code_challenge_method == "plain":
        oauth2.code_challenge = code_challenge
        oauth2.code_challenge_method = code_challenge_method
        return True
    return False

def PKCECheck(code_verifier: str, oauth2: Oauth2):
    method = oauth2.code_challenge_method
    code_challenge = oauth2.code_challenge

    if method == "S256":
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode() #NOTE: when aproved need to check this 
        ok = expected == code_challenge
    elif method == "plain":
        ok = code_verifier == code_challenge
    else:
        ok = False

    if ok:
        oauth2.code_challenge_method = ""
        oauth2.code_challenge = ""

    return ok

    


#client id == api key for this playground
@app.get("/as/authorization.oauth2") #scopes are not checked and dont work
def oauth2(request: Request, response_type:str=Query(...),client_id:str=Query(...),redirect_uri:str=Query(...),scope:str=Query(default=""),state:str=Query(default=""),code_challenge:str=Query(default=""),code_challenge_method:str=Query(default="")):
    if response_type != "code":
        return HTMLResponse(content="<h1>BAD_REQUEST</h1><p>response_type must be 'code'</p>", status_code=400)
    if client_id not in Oauth2Data:
        return HTMLResponse(content="<h1>BAD_REQUEST</h1><p>Invalid client_id</p>", status_code=400)
    oauth2 = Oauth2Data[client_id]
    if oauth2.redirect_uri != "":
        if redirect_uri != Oauth2Data[client_id].redirect_uri:
            return HTMLResponse(content="<h1>BAD_REQUEST</h1><p>Invalid redirect_uri</p>", status_code=400)
    # site needed for "login"
    return templates.TemplateResponse(name="oauth2login.html", request=request, context={"client_id": client_id, "redirect_uri": redirect_uri, "scope": scope, "state": state, "code_challenge": code_challenge, "code_challenge_method": code_challenge_method})
    
 

@app.post("/as/authorization.internal")
def oauth2_post(client_id: str = Form(...), redirect_uri: str = Form(...), state: str = Form(default=""), login: str = Form(...), code_challenge: str = Form(default=""), code_challenge_method: str = Form(default="")):
    if client_id != login:
        return HTMLResponse(content="<p style='color: red;'>Wrong client_id or login</p>", status_code=200)
    oauth2 = Oauth2Data[client_id]

    if oauth2.PKCE == True :
        if PKCE(code_challenge, code_challenge_method, oauth2) == False:
            return HTMLResponse(content="<p style='color: red;'>ERROR with PKCE code_challenge_method</p>", status_code=200)
    oauth2.code = "code_"+secrets.token_urlsafe(32) #generate 
    url=f"{redirect_uri}?code={oauth2.code}"
    if state != "":
        url += f"&state={state}"
    response = Response()
    response.headers["HX-Redirect"] = url
    return response

@app.get("/internal/test")
def test(code:str=Query(...),state:str=Query(default="")):
    # testing first step of oauth2
    return HTMLResponse(content=f"<h1>Code: {code}</h1><p>State: {state}</p>", status_code=200)


@app.post("/as/token.oauth2") #scopes are not checked and dont work
def OAuthToken(content_type:str=Header(...,alias="content-type"),authorization:str=Header(...),grant_type:str=Form(...),refresh_token:str=Form(default=""),code:str=Form(default=""),redirect_uri:str=Form(default=""),code_verifier:str=Form(default=""),):
    if content_type != "application/x-www-form-urlencoded":
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "content-type must be 'application/x-www-form-urlencoded'"}}, status_code=400)
    
    try:
        auth_parts = authorization.split(" ")
        if len(auth_parts) != 2 or auth_parts[0].lower() != "basic":
            raise ValueError()
        
        decoded_bytes = base64.b64decode(auth_parts[1])
        decoded_str = decoded_bytes.decode("utf-8")
        client_id, client_secret = decoded_str.split(":", 1)
    except Exception:
        return JSONResponse(content={"error": "invalid_client", "error_description": "Malformed Authorization header"}, status_code=401)
    
    if client_id not in Oauth2Data:
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "Invalid client_id"}}, status_code=400)
    oauth2 = Oauth2Data[client_id]
    if oauth2.client_secret != client_secret:
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "Invalid client_secret"}}, status_code=400)
    
    if grant_type == "authorization_code":
        if oauth2.PKCE == True:
            if PKCECheck(code_verifier,oauth2) == False:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "Invalid code_verifier"}}, status_code=400)

        if oauth2.code != code or oauth2.code == "": # forgot to check if there is any code available FIXED
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "No code available. Please request a new code"}}, status_code=400)
        else:
            if oauth2.redirect_uri != "":
                if redirect_uri != oauth2.redirect_uri:
                 return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "Invalid redirect_uri"}}, status_code=400)
    elif grant_type == "refresh_token":
        if oauth2.refresh_token != refresh_token:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "Invalid refresh_token"}}, status_code=400)
    else:
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "grant_type must be 'authorization_code' or 'refresh_token'"}}, status_code=400)
    
    oauth2.access_token = "access_token_"+secrets.token_urlsafe(32) #generate
    oauth2.refresh_token = "refresh_token_"+secrets.token_urlsafe(32) #generate
    # NOTE: what i meant?  added the acces_token for simplicity of development but Bearer is still ineeded
    oauth2.code = "" #invalidate code
    #oauth2.expires_in = 
    data={"access_token": oauth2.access_token, "refresh_token": oauth2.refresh_token, "token_type": "Bearer", "expires_in": 3599}
    return JSONResponse(content=data, status_code=200)
    


# https://api.volvocars.com/connected-vehicle/v2/ section

@app.get("/vehicles")
def listVehicles(auth_header: AuthHeaderGET = Header(...)):
    """list all vehicles associated with the provided API key."""
    try:
        authenticate(auth_header)
    except ValueError as e:
        return UnauthorizedResponse(str(e))
    else:
        vehicles=[]
        for car in database[auth_header.vcc_api_key]:
            vehicle={"vin": car.VIN,}
            vehicles.append(vehicle)
        data={"data": vehicles}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.get("/vehicles/{VIN}")
def getVehicle(VIN:str, auth_header: AuthHeaderGET = Header(...)): #TODO: implement the data in car class
    """get vehicle information for the specified VIN. Mostly static data but enough to test your apps"""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data={
        "data": {
            "vin": VIN,
            "modelYear": car.modelYear,
            "gearbox" : car.gearboxType,
            "fuelType" : car.fuelType,
            "externalColour": "SAVILE GREY STATIC",
            "batteryCapacityKWH": 78.0,
            "images": {
            "exteriorImageUrl": "link-to-exterior-image",
            "internalImageUrl": "link-to-internal-image"
            },
            "descriptions": {
            "model": "V60 II STATIC",
            "upholstery": "CHARCOAL/LEAC/CHARC STATIC",
            "steering": "LEFT STATIC"
            }}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))

#climetization commands
def climate(VIN:str, auth_header: AuthHeader = Header(...), command:str=None):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        if command not in car.commands:
            return NotSupportedResponse(command)
        else:
            invoiceStatus="Let the dev know if you see this message. Something went wrong with the invoiceStatus"
            if command == "CLIMATIZATION_START":
                invoiceStatus = car.InvoiceStatus("climate",True) # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
                if invoiceStatus[1]:
                    car.update("climate",True)
                    return NormalResponse(VIN, invoiceStatus[0],headers=ResponseHeaderGenerator(auth_header))
            elif command == "CLIMATIZATION_STOP":
                invoiceStatus = car.InvoiceStatus("climate",False) # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
                if invoiceStatus[1]:
                    car.update("climate",False)
                    return NormalResponse(VIN, invoiceStatus[0], headers=ResponseHeaderGenerator(auth_header))
            
            if invoiceStatus[1] == False:
                return NormalResponse(VIN, invoiceStatus[0], status_code=403, headers=ResponseHeaderGenerator(auth_header)) #  rejected what status code should be sent 
    return JSONResponse(
    content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500, headers=ResponseHeaderGenerator(auth_header))
# What if climate is already off?

@app.post("/vehicles/{VIN}/commands/climatization-start")
def climateStart(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to start the climatization."""
    return climate(VIN, auth_header, command="CLIMATIZATION_START")


@app.post("/vehicles/{VIN}/commands/climatization-stop")
def climateStop(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to stop the climatization."""
    return climate(VIN, auth_header, command="CLIMATIZATION_STOP")

#engine commands
def engine(VIN:str, auth_header: AuthHeader = Header(...), command:str=None, runtimeMinutes:int = 0):   
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
         # invoice possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
        if command not in car.commands:
            return NotSupportedResponse(command)
        else:
            invoiceStatus="Let the dev know if you see this message. Something went wrong with the invoiceStatus"
            if command == "ENGINE_START":
                invoiceStatus = car.InvoiceStatus("engine",True)
                if invoiceStatus[1]:
                    car.update("engineStatus", "RUNNING")
                    car.update("engineTime", runtimeMinutes)
                    return NormalResponse(VIN, invoiceStatus[0], headers=ResponseHeaderGenerator(auth_header))
            elif command == "ENGINE_STOP":
                invoiceStatus = car.InvoiceStatus("engine",False)
                if invoiceStatus[1]:
                    car.update("engineStatus", "STOPPED")
                    car.update("engineTime", 0)
                return NormalResponse(VIN, invoiceStatus[0], headers=ResponseHeaderGenerator(auth_header))

            if invoiceStatus[1] == False:
                return NormalResponse(VIN, invoiceStatus[0], status_code=500, headers=ResponseHeaderGenerator(auth_header)) # what if rejected what status code should be sent and all of the other BAD invoices
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500, headers=ResponseHeaderGenerator(auth_header))
    # what if engine is already stopped? Need to check docs or a real car (not in mine doesnt have that option)



@app.get("/vehicles/{VIN}/engine-status")
def engineStatus(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current engine status for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data = {"data": {"engineStatus": {"value": car.engineStatus, "timestamp": car.timestamp()}}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


@app.post("/vehicles/{VIN}/commands/engine-start")
def engineStart(VIN:str, auth_header: AuthHeaderPOST = Header(...), runtimeMinutes:dict = Body(...)):
    """send a command to start the engine for the specified VIN. The runtimeMinutes >0 and <15."""
    runtimeMinutes = runtimeMinutes.get("runtimeMinutes", 0)
    if runtimeMinutes < 1 or runtimeMinutes >= 15:
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "runtimeMinutes can be maximaly 15 min"}}, status_code=400, headers=ResponseHeaderGenerator(auth_header))
    return engine(VIN, auth_header,command="ENGINE_START", runtimeMinutes=runtimeMinutes)

@app.post("/vehicles/{VIN}/commands/engine-stop")
def engineStop(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to stop the engine for the specified VIN."""
    return engine(VIN, auth_header,command="ENGINE_STOP")

# doors, windows, locks section



@app.get("/vehicles/{VIN}/windows")
def windows(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current status of the windows and sunroof for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data={"data": {"frontLeftWindow": { "value": car.frontLeftWindow, "timestamp": car.timestamp()},"frontRightWindow": {"value": car.frontRightWindow,"timestamp": car.timestamp()},"rearLeftWindow": { "value": car.rearLeftWindow,"timestamp": car.timestamp()}, "rearRightWindow": {"value": car.rearRightWindow,"timestamp": car.timestamp()},"sunroof": {"value": car.sunroof,"timestamp": car.timestamp()}}}

        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))

@app.get("/vehicles/{VIN}/doors")
def doors(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current status of the doors and locks for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        timestamp = car.timestamp()
        data={"data": {"centralLock": {"value": car.centralLock,"timestamp": timestamp},"frontLeftDoor": {"value": car.frontLeftDoor,"timestamp": timestamp},"frontRightDoor": {"value": car.frontRightDoor,"timestamp": timestamp},"hood": {"value": car.hood,"timestamp": timestamp},"rearLeftDoor": {"value": car.rearLeftDoor,"timestamp": timestamp},"rearRightDoor": {"value": car.rearRightDoor,"timestamp": timestamp},"tailGate": {"value": car.tailGate,"timestamp": timestamp},"tankLid": {"value": car.tankLid,"timestamp": timestamp}}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))

@app.post("/vehicles/{VIN}/commands/lock")
def doorLock(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to lock the doors for the specified VIN."""
    try:
        car =VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        command = "LOCK"
        if command not in car.commands:
            return NotSupportedResponse(command)
        invoiceStatus = car.InvoiceStatus("locks") # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        if invoiceStatus[1] == True:
            car.update("centralLock", "LOCKED")
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))   
        else:
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=500, headers=ResponseHeaderGenerator(auth_header)) # what if rejected what status code should be sent and all of the other BAD invoices


@app.post("/vehicles/{VIN}/commands/lock-reduced-guard") #only for AAOS not Sensus
def doorLockReduce(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to lock the doors with reduced guard for the specified VIN. Only for AAOS not Sensus."""
    try:
        car =VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        command = "LOCK_REDUCED_GUARD"
        if command not in car.commands:
            return NotSupportedResponse(command)
        invoiceStatus = car.InvoiceStatus("locks") # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        if invoiceStatus[1] == True:
            car.update("centralLock", "LOCKED")
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))   
        else:
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=500, headers=ResponseHeaderGenerator(auth_header)) # what

@app.post("/vehicles/{VIN}/commands/unlock") # doesnt work like in real life you must click button of the trunk
def doorUnlock(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to unlock the doors for the specified VIN."""
    try:
        car =VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        command = "UNLOCK"
        if command not in car.commands:
            return NotSupportedResponse(command)
        invoiceStatus = car.InvoiceStatus("UNLOCK") # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        if invoiceStatus[1] == True:
            car.update("centralLock","UNLOCKED")
            data={"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": "","readyToUnlock": True ,"readyToUnlockUntil": 5,"details": "Not fully implemented manual button press needed in real life"}} #whend would readyToUnlock be false?
            return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))
        else:
            return NormalResponse(VIN, invoiceStatus[0],status_code=409, headers=ResponseHeaderGenerator(auth_header))

#lights and horn

def lightsAndHorn(VIN:str, auth_header: AuthHeader = Header(...), command:str=None):
    """send a command to start the lights and horn for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        if command not in car.commands:
            return NotSupportedResponse(command)
        else:
            invoiceStatus = car.InvoiceStatus(command)
            if invoiceStatus[1] == True:
                car.update("lightTimestamp",car.timestamp())
                if command == "FLASH":
                    car.update("lightTimestamp",car.timestamp())
                elif command == "HONK":
                    car.update("hornTimestamp",car.timestamp())
                elif command == "HONK_AND_FLASH":
                    car.update("hornTimestamp",car.timestamp())
                    car.update("lightTimestamp",car.timestamp())
                else:
                    return BadRequestResponse(VIN)
                return NormalResponse(VIN, invoiceStatus[0], headers=ResponseHeaderGenerator(auth_header))
            else:
                return NormalResponse(VIN, invoiceStatus[0],status_code=409, headers=ResponseHeaderGenerator(auth_header))

@app.post("/vehicles/{VIN}/commands/flash")
def flash(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to flash the lights for the specified VIN."""
    return lightsAndHorn(VIN, auth_header, command="FLASH")
            
    
@app.post("/vehicles/{VIN}/commands/honk")
def honk(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to honk the horn for the specified VIN."""
    return lightsAndHorn(VIN, auth_header, command="HONK")


@app.post("/vehicles/{VIN}/commands/honk-and-flash")
def honkAndFlash(VIN:str, auth_header: AuthHeaderPOST = Header(...)):
    """send a command to honk the horn and flash the lights for the specified VIN."""
    return lightsAndHorn(VIN, auth_header, command="HONK_AND_FLASH")

#statistics

@app.get("/vehicles/{VIN}/statistics") #STATIC
def statistics(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get vehicle statistics for the specified VIN. Mostly static data but enough to test your apps"""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        timeStamp = car.timestamp()
        #units are always the same NO imperial units. l/100km, kWh/100km, km/h, km
        data={
            "data": {
                "averageFuelConsumption": {
                    "value": 7.2374,
                    "unit": "l/100km",
                    "timestamp": timeStamp
                },
                "averageEnergyConsumption": {
                    "value": 7.2374,
                    "unit": "kWh/100km",
                    "timestamp": timeStamp
                },
                "averageFuelConsumptionAutomatic": {
                    "value": 7.4732,
                    "unit": "l/100km",
                    "timestamp": timeStamp
                },
                "averageEnergyConsumptionAutomatic": {
                    "value": 7.4732,
                    "unit": "kWh/100km",
                    "timestamp": timeStamp
                },
                "averageEnergyConsumptionSinceCharge": {
                    "value": 7.4732,
                    "unit": "kWh/100km",
                    "timestamp": timeStamp
                },
                "averageSpeed": {
                    "value": 50,
                    "unit": "km/h",
                    "timestamp": timeStamp
                },
                "averageSpeedAutomatic": {
                    "value": 66,
                    "unit": "km/h",
                    "timestamp": timeStamp
                },
                "tripMeterManual": {
                    "value": 500.0,
                    "unit": "km",
                    "timestamp": timeStamp
                },
                "tripMeterAutomatic": {
                    "value": 420.0,
                    "unit": "km",
                    "timestamp": timeStamp
                },
                "distanceToEmptyTank": {
                    "value": 1312,
                    "unit": "km",
                    "timestamp": timeStamp
                },
                "distanceToEmptyBattery": {
                    "value": 312,
                    "unit": "km",
                    "timestamp": timeStamp
                }
            }
            }
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


#tyres
@app.get("/vehicles/{VIN}/tyres")
def tyres(VIN:str, auth_header: AuthHeaderGET= Header(...)):
    """get the current tyre warnings status for the specified VIN.""" 
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data={"data":{"frontLeft":{"value":car.frontLeft,"timestamp":car.timestamp()},"frontRight":{"value":car.frontRight,"timestamp":car.timestamp()},"rearLeft":{"value":car.rearLeft,"timestamp":car.timestamp()},"rearRight":{"value":car.rearRight,"timestamp":car.timestamp()}}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))
    
        


#commands 
@app.get("/vehicles/{VIN}/commands")
def commands(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get a list of available commands for the specified VIN."""
    href=f"/v2/vehicles/{VIN}/commands/" 
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data = []
        for command in car.commands:
            data.append({
                "command": command,
                "href": href + command.lower().replace("_", "-")
            })
        return JSONResponse(content={"data": data}, status_code=200, headers=ResponseHeaderGenerator(auth_header))




@app.get("/vehicles/{VIN}/command-accessibility")
def commandAccessibility(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """check if the car is ready to receive commands or why it is not for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        if car.availabilityStatus_value == "AVAILABLE" or car.availabilityStatus_value == "UNSPECIFIED": 
            data = {"availabilityStatus": {"value": car.availabilityStatus_value,"timestamp":car.timestamp()}}
        else:
            data = {"availabilityStatus": {"value": car.availabilityStatus_value, "unavailableReason": car.availabilityStatus_unavailableReason,"timestamp":car.timestamp()}}     
                
        return JSONResponse(content={"data": data}, status_code=200, headers=ResponseHeaderGenerator(auth_header))  


                     
#Fuel section
@app.get("/vehicles/{VIN}/fuel")
def getFuel(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current fuel level or/and battery charge level"""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:   # docs says  thath only liters and % are  valid
        FuelType = car.fuelType
        #openapi saya int but docs says str so i will use int for now
        FuelLevel = car.fuelICE 
        FuelLevelElectric = car.fuelElectric
        if FuelType == "PETROL" or FuelType == "DIESEL":
            data = {"data":{"fuelAmount":{"value" : FuelLevel, "unit":"l","timestamp":car.timestamp()}}} 
        elif FuelType == "ELECTRIC":
            data = {"data":{"batteryChargeLevel":{"value" : FuelLevelElectric, "unit":"%","timestamp":car.timestamp()}}} 
        elif FuelType == "HYBRID":
            data = {"data":{"fuelAmount":{"value" : FuelLevel, "unit":"l","timestamp":car.timestamp()}, "batteryChargeLevel":{"value" : FuelLevelElectric, "unit":"%","timestamp":car.timestamp()}}} 
        else:
            return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


    
#Odometer section
@app.get("/vehicles/{VIN}/odometer")
def getOdometer(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    
    """get the current odometer reading for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:   #Units and timestamp here again only km is valid Why volvo Why?
        Odometer = car.odometer #in docs its str but in openapi is int
        data = {"data":{"odometer" : { "value": Odometer, "unit" : "km","timestamp" : car.timestamp()}}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


    
#diagnostic section
@app.get("/vehicles/{VIN}/engine")
def engineDiagnostics(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current engine diagnostics for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data={"data":{"engineCoolantLevelWarning":{"value":car.engineCoolantLevel,"timestamp":car.timestamp()},"oilLevelWarning":{"value":car.oilLevel,"timestamp":car.timestamp()}}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))

@app.get("/vehicles/{VIN}/diagnostics")  # there is additional washer fluid data sent by the api but docs dont talk about it there ? and units?
def diagnostics(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current diagnostics for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        toService = car.timeToService
        
        unit=""
        if toService < 62: #when volvo uses day and when months 
            unit="days"
        else:
            unit="months"
            toService = toService//31
            
        if car.serviceWarning != "NO_WARNING" and car.serviceTrigger != "UNSPECIFIED":
            data={"data":{"serviceWarning":{"value":car.serviceWarning,"timestamp":car.timestamp()},"serviceTrigger":{"value":car.serviceTrigger,"timestamp":car.timestamp()},"engineHoursToService":{"value":car.engineHoursToService,"unit":"h","timestamp":car.timestamp()},"distanceToService":{"value":car.distanceToService,"unit":"km","timestamp":car.timestamp()},"washerFluidLevelWarning":{"value":car.washerFluidLevelWarning,"timestamp":car.timestamp()},"timeToService":{"value":toService,"unit":unit,"timestamp":car.timestamp()}}}
        else:
            data={"data":{"serviceWarning":{"value":car.serviceWarning,"timestamp":car.timestamp()},"engineHoursToService":{"value":car.engineHoursToService,"unit":"h","timestamp":car.timestamp()},"distanceToService":{"value":car.distanceToService,"unit":"km","timestamp":car.timestamp()},"washerFluidLevelWarning":{"value":car.washerFluidLevelWarning,"timestamp":car.timestamp()},"timeToService":{"value":toService,"unit":unit,"timestamp":car.timestamp()}}}
        
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


@app.get("/vehicles/{VIN}/brakes")
def Brakes(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current brake status for the specified VIN."""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data={"data":{"brakeFluidLevelWarning":{"value":car.brakeFluidLevel,"timestamp":car.timestamp()}}}
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


@app.get("/vehicles/{VIN}/warnings") 
def Warnings(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    """get the current warning status for the specified VIN. STATIC for now"""
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        return autoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        timestamp = car.timestamp()
        # Possible values: UNSPECIFIED, NO_WARNING, FAILURE.
        data={
            "data": {
                "brakeLightLeftWarning": {
                "value": car.brakeLightLeftWarning,
                "timestamp": car.timestamp()
                },
                "brakeLightCenterWarning": {
                "value": car.brakeLightCenterWarning,
                "timestamp": car.timestamp()
                },
                "brakeLightRightWarning": {
                "value": car.brakeLightRightWarning,
                "timestamp": car.timestamp()
                },
                "fogLightFrontWarning": {
                "value": car.fogLightFrontWarning,
                "timestamp": car.timestamp()
                },
                "fogLightRearWarning": {
                "value": car.fogLightRearWarning,
                "timestamp": car.timestamp()
                },
                "positionLightFrontLeftWarning": {
                "value": car.positionLightFrontLeftWarning,
                "timestamp": car.timestamp()
                },
                "positionLightFrontRightWarning": {
                "value": car.positionLightFrontRightWarning,
                "timestamp": car.timestamp()
                },
                "positionLightRearLeftWarning": {
                "value": car.positionLightRearLeftWarning,
                "timestamp": car.timestamp()
                },
                "positionLightRearRightWarning": {
                "value": car.positionLightRearRightWarning,
                "timestamp": car.timestamp()
                },
                "highBeamLeftWarning": {
                "value": car.highBeamLeftWarning,
                "timestamp": car.timestamp()
                },
                "highBeamRightWarning": {
                "value": car.highBeamRightWarning,
                "timestamp": car.timestamp()
                },
                "lowBeamLeftWarning": {
                "value": car.lowBeamLeftWarning,
                "timestamp": car.timestamp()
                },
                "lowBeamRightWarning": {
                "value": car.lowBeamRightWarning,
                "timestamp": car.timestamp()
                },
                "daytimeRunningLightLeftWarning": {
                "value": car.daytimeRunningLightLeftWarning,
                "timestamp": car.timestamp()
                },
                "daytimeRunningLightRightWarning": {
                "value": car.daytimeRunningLightRightWarning,
                "timestamp": car.timestamp()
                },
                "turnIndicationFrontLeftWarning": {
                "value": car.turnIndicationFrontLeftWarning,
                "timestamp": car.timestamp()
                },
                "turnIndicationFrontRightWarning": {
                "value": car.turnIndicationFrontRightWarning,
                "timestamp": car.timestamp()
                },
                "turnIndicationRearLeftWarning": {
                "value": car.turnIndicationRearLeftWarning,
                "timestamp": car.timestamp()
                },
                "turnIndicationRearRightWarning": {
                "value": car.turnIndicationRearRightWarning,
                "timestamp": car.timestamp()
                },
                "registrationPlateLightWarning": {
                "value": car.registrationPlateLightWarning,
                "timestamp": car.timestamp()
                },
                "sideMarkLightsWarning": {
                "value": car.sideMarkLightsWarning,
                "timestamp": car.timestamp()
                },
                "hazardLightsWarning": {
                "value": car.hazardLightsWarning,
                "timestamp": car.timestamp()
                },
                "reverseLightsWarning": {
                "value": car.reverseLightsWarning,
                "timestamp": car.timestamp()
                }
            }
            }
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))


#internal endpoints 


@app.get("/internal")
def Internal():
   """internal endpoint that shows version and instance information"""
   return internal.Internal() # here will be displayed any options like authetication using tokens and so on.


@app.get("/internal/oauth2")
def AuthGetInternal(vcc_api_key:str = Header(...)):
    return internal.OAuthGetInternal(vcc_api_key)

@app.post("/internal/oauth2/activate")
def AuthActivateInternal(vcc_api_key:str = Header(...),client_secret:str = Body(...),PKCE:bool = Body(...),redirect_uri:str = Body(default="")):
    return internal.OAuthActivateInternal(vcc_api_key, client_secret, PKCE, redirect_uri)

@app.post("/internal/oauth2/deactivate")
def AuthDeactivateInternal(vcc_api_key:str = Header(...)):
    return internal.OAuthDeactivateInternal(vcc_api_key)

@app.post("/internal/oauth2/regenerate")
def AuthRegenerateInternal(vcc_api_key:str = Header(...)):
    return internal.OAuthRegenerateInternal(vcc_api_key)




@app.get("/internal/terminal")
def Terminal(VIN:str,key:str, request: Request):
    """For testing and development purposes. Use as help."""
    return internal.Terminal(VIN, key, request) #file response

#site section
@app.get("/internal/style.css", include_in_schema=False)
def Style():
    return dashboard.style() #file response




@app.get("/internal/dashboard/car", include_in_schema=False)
def DashboardCar(key: str,VIN: str, request: Request):
    return dashboard.DashboardCar(key, VIN, request)
    
@app.get("/internal/dashboard/redirect", include_in_schema=False)
def DashboardRedirect(key: str,VIN: str, request: Request):
    return dashboard.DashboardRedirect(key, VIN, request) 
    
@app.websocket("/internal/dashboard/ws")
async def DashboardWS(websocket: WebSocket):
    return await dashboard.DashboardWS(websocket)
    
@app.post("/internal/dashboard/update", include_in_schema=False) # html request here for dashboard
def DashboardUpdate(key: str,VIN: str, request: Request, attribute: str = Body(...), value: str = Body(...)):
    return dashboard.DashboardUpdate(key, VIN, request, attribute, value)




@app.get("/internal/dashboard", include_in_schema=False)
def Dashboard(key: str, request: Request):
    return dashboard.Dashboard(key, request)



@app.get("/internal/welcome", include_in_schema=False)
def Welcome():
    return dashboard.Welcome() #file response

@app.get("/internal/welcome/Check", include_in_schema=False)
def WelcomeCheck(vcc_api_key: str):
    return dashboard.WelcomeCheck(vcc_api_key)

@app.get("/internal/welcome/APIKey", include_in_schema=False) 
def WelcomeAPIKey(request: Request):
    return dashboard.WelcomeAPIKey(request)

@app.post("/internal/dashboard/NewCar", include_in_schema=False) 
def WelcomeNewCar(request: Request, key: str, VIN: str):
    return dashboard.WelcomeNewCar(request, key, VIN)

@app.delete("/internal/dashboard/delCar", include_in_schema=False) 
def deleteCar(request: Request, key: str, VIN: str):
    return dashboard.deleteCar(key, VIN, request)

@app.get("/internal/dashboard/OAuth2settings", include_in_schema=False)
def OAuth2Settings(request: Request,key: str):
    return dashboard.OAuth2Settings(key, request)

@app.post("/internal/dashboard/OAuth2change", include_in_schema=False)
def OAuth2Change(request: Request, attribute: str=Body(...), value: str=Body(...), key: str=Query(...)):
    return dashboard.OAuth2Change(key, attribute, value, request)

@app.get("/internal/dashboard/loading", include_in_schema=False)
def scenariosDash(request: Request,key: str, VIN: str,name: str=Query(default="")):
    if name == "":
        return dashboard.scenarios(key, VIN, request)
    else:
        return dashboard.scenarioLoad(key, VIN, name, request)
    
@app.get("/internal/dashboard/snapshots", include_in_schema=False)
def snapshotDash(request: Request,key: str):
    return dashboard.snapshots(key, request)

@app.get("/internal/dashboard/snapshots/command", include_in_schema=False)
def snapshotDashUpdate(request: Request,key: str,command: str, name: str):
    if command == "save":
        return dashboard.snapshotsSave(key, name, request)
    elif command == "load":
        return dashboard.snapshotsLoad(key, name, request)
    else:
        return JSONResponse(content={"error": {"message": "BAD_REQUEST", "description": "Invalid command"}}, status_code=400)

#internal endpoints for testing and development. Not part of the official API.

@app.get("/internal/status") 
def getStatus(VIN: str = Header(...),vcc_api_key: str = Header(...,alias="vcc-api-key")): 
    """internal endpoint for getting car status without using commands and without a token"""
    return internal.getStatus(VIN, vcc_api_key)
        
@app.websocket("/internal/status/ws") 
async def statusWS(websocket: WebSocket):
    return await internal.statusWS(websocket)

@app.post("/internal/update") # internal endpoint for updating car status without using commands (for testing purposes and dashboard) 
def internal_update(VIN: str = Header(...),vcc_api_key: str = Header(...,alias="vcc-api-key"),attribute: str = Body(...), value: str = Body(...)):
    """internal endpoint for updating car without using commands and without a token"""
    return internal.internal_update(VIN, vcc_api_key, attribute, value)


@app.post("/internal/updates") 
def internal_updates(VIN: str = Header(...),vcc_api_key: str = Header(...,alias="vcc-api-key"),attribute: list = Body(...), value: list = Body(...)):
    """internal endpoint for updating multiple car attributes without using commands and without a token/ NEED TO BE REWRITTEN"""
    return internal.internal_updates(VIN, vcc_api_key, attribute, value)


@app.get("/internal/APIKey")
def genAPIKey():            
    """internal endpoint for creating a new API key"""        
    return internal.genAPIKey()

@app.post("/internal/addCar")
def addCar(vcc_api_key: str = Header(...,alias="vcc-api-key"), VIN: str = Body(...), attributes: dict = Body(default={})):
    """internal endpoint for adding a new car to the database"""
    return internal.addCar(vcc_api_key, VIN, attributes)
@app.delete("/internal/delCar")
def delCar(vcc_api_key: str = Header(...,alias="vcc-api-key"), VIN: str = Body(...), attributes: dict = Body(default={})):
    """internal endpoint for deleting a car from the database"""
    return internal.delCar(vcc_api_key, VIN, attributes)




@app.post("/internal/scenario")
def scenario(vcc_api_key: str = Header(...,alias="vcc-api-key"), VIN: str = Body(...), scenario: str = Body(...)):
    """internal endpoint for simulating a scenario for the specified VIN"""
    return scenariosFunc(vcc_api_key, VIN, scenario)





@app.post("/internal/snapshot")
def snapshot(vcc_api_key: str = Header(...,alias="vcc-api-key"), command: str = Body(...), name: str = Body(...)):
    """internal endpoint for taking a snapshot of the current status for the specified VIN"""
    return snapshots(vcc_api_key, command, name)

if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)

