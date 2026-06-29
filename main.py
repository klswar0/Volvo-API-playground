from fastapi import Body, FastAPI, Header ,Request ,Query, Response, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import JSONResponse, FileResponse ,HTMLResponse 
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field 
import uvicorn
import json
import secrets



import internal
from notifier import notifier
from classCar import Car, options, AuthHeader, startUp, timestampGenerator
from database import database
from readyResponses import ErrorResponse, UnauthorizedResponse, BadRequestResponse, NotSupportedResponse, NormalResponse

#TODO: redo internal responses
templates = Jinja2Templates(directory="templates")


app = FastAPI()



def authenticate(auth_header: AuthHeader):
    if auth_header.vcc_api_key not in database:
        raise ValueError("Invalid API key")
    if startUp["TOKENcheck"] == True:
        if auth_header.authorization != "Bearer valid_token": # real token endpoints needed
            raise ValueError("Invalid token")


def VINHandling(VIN:str, auth_header: AuthHeader):
    try:
        authenticate(auth_header)
    except ValueError:
        raise ValueError("Invalid API key")
    for car in database[auth_header.vcc_api_key]:
        if car.VIN == VIN:
            return car
    raise ValueError("Invalid VIN")

# https://api.volvocars.com/connected-vehicle/v2/ section

@app.get("/vehicles")
def listVehicles(auth_header: AuthHeader = Header(...)):
    try:
        authenticate(auth_header)
    except ValueError:
        return UnauthorizedResponse()
    else:
        vehicles=[]
        for car in database[auth_header.vcc_api_key]:
            vehicle={"vin": car.VIN,}
            vehicles.append(vehicle)
        data={"data": vehicles}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)



#climetization commands
def climate(VIN:str, auth_header: AuthHeader = Header(...), command:str=None):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        if command not in car.commands:
            return NotSupportedResponse(command)
        else:
            invoiceStatus="Let the dev know if you see this message. Something went wrong with the invoiceStatus"
            if command == "CLIMATIZATION_START":
                invoiceStatus = car.InvoiceStatus("climate",True) # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
                if invoiceStatus[1]:
                    car.update("climate",True)
                    return NormalResponse(VIN, invoiceStatus[0])
            elif command == "CLIMATIZATION_STOP":
                invoiceStatus = car.InvoiceStatus("climate",False) # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
                if invoiceStatus[1]:
                    car.update("climate",False)
                    return NormalResponse(VIN, invoiceStatus[0])
            
            if invoiceStatus[1] == False:
                return NormalResponse(VIN, invoiceStatus[0],500) # FIXME:what if rejected what status code should be sent 
    return JSONResponse(
    content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)
# What if climate is already off?

@app.post("/vehicles/{VIN}/commands/climatization-start")
def climateStart(VIN:str, auth_header: AuthHeader = Header(...)):
    return climate(VIN, auth_header, command="CLIMATIZATION_START")


@app.post("/vehicles/{VIN}/commands/climatization-stop")
def climateStop(VIN:str, auth_header: AuthHeader = Header(...)):
    return climate(VIN, auth_header, command="CLIMATIZATION_STOP")

#engine commands
def engine(VIN:str, auth_header: AuthHeader = Header(...), command:str=None, runtimeMinutes:int = 0):   
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
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
                    return NormalResponse(VIN, invoiceStatus[0])
            elif command == "ENGINE_STOP":
                invoiceStatus = car.InvoiceStatus("engine",False)
                if invoiceStatus[1]:
                    car.update("engineStatus", "STOPPED")
                    car.update("engineTime", 0)
                return NormalResponse(VIN, invoiceStatus[0])
            
            if invoiceStatus[1] == False:
                return NormalResponse(VIN, invoiceStatus[0],500) # what if rejected what status code should be sent and all of the other BAD invoices
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)
    # what if engine is already stopped? Need to check docs or a real car (not in mine doesnt have that option)



@app.get("/vehicles/{VIN}/engine-status")
def engineStatus(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data = {"vin": VIN, "engineStatus": car.engineStatus}
        return JSONResponse(content={"data": data}, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)


@app.post("/vehicles/{VIN}/commands/engine-start")
def engineStart(VIN:str, auth_header: AuthHeader = Header(...), runtimeMinutes:int = Body(...)):
    if runtimeMinutes < 1 or runtimeMinutes >= 15:
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "runtimeMinutes can be maximaly 15 min"}}, status_code=400)
    return engine(VIN, auth_header,command="ENGINE_START", runtimeMinutes=runtimeMinutes)

@app.post("/vehicles/{VIN}/commands/engine-stop")
def engineStop(VIN:str, auth_header: AuthHeader = Header(...)):
    return engine(VIN, auth_header,command="ENGINE_STOP")

# doors, windows, locks section



@app.get("/vehicles/{VIN}/windows")
def windows(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data={"data": {"frontLeftWindow": { "value": car.frontLeftWindow, "timestamp": "placeholder"},"frontRightWindow": {"value": car.frontRightWindow,"timestamp": "placeholder"},"rearLeftWindow": { "value": car.rearLeftWindow,"timestamp": "placeholder"}, "rearRightWindow": {"value": car.rearRightWindow,"timestamp": "placeholder"},"sunroof": {"value": car.sunroof,"timestamp": "placeholder"}}}

        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.get("/vehicles/{VIN}/doors")
def doors(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data={"data": {"centralLock": {"value": car.centralLock,"timestamp": "placeholder"},"frontLeftDoor": {"value": car.frontLeftDoor,"timestamp": "placeholder"},"frontRightDoor": {"value": car.frontRightDoor,"timestamp": "placeholder"},"hood": {"value": car.hood,"timestamp": "placeholder"},"rearLeftDoor": {"value": car.rearLeftDoor,"timestamp": "placeholder"},"rearRightDoor": {"value": car.rearRightDoor,"timestamp": "placeholder"},"tailGate": {"value": car.tailGate,"timestamp": "placeholder"},"tankLid": {"value": car.tankLid,"timestamp": "placeholder"}}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.post("/vehicles/{VIN}/commands/lock")
def doorLock(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car =VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        command = "LOCK"
        if command not in car.commands:
            return NotSupportedResponse(command)
        invoiceStatus = car.InvoiceStatus("locks") # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        if invoiceStatus[1] == True:
            car.update("centralLock", "LOCKED")
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=200)   
        else:
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=500) # what if rejected what status code should be sent and all of the other BAD invoices
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

# @app.post("/vehicles/{VIN}/commands/lock-reduced-guard") #only for AAOS not Sensus
# def doorLockReduce(VIN:str, auth_header: AuthHeader = Header(...)):
#     try:
#         car =VINHandling(VIN, auth_header)
#     except ValueError as e:
#         if str(e) == "Invalid API key":
#             return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
#         elif str(e) == "Invalid VIN":
#             return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
#     else:
#         invoiceStatus = "COMPLETED" # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
#         car.update("centralLock", "LOCKED")
#         data = {{"data": {"vin": VIN,"invokeStatus": invoiceStatus,"message": ""}}}
#         return JSONResponse(content=data, status_code=200)
#     return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.post("/vehicles/{VIN}/commands/unlock") # doesnt work like in real life you must click button of the trunk
def doorUnlock(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car =VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        command = "UNLOCK"
        if command not in car.commands:
            return NotSupportedResponse(command)
        invoiceStatus = car.InvoiceStatus("UNLOCK") # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        if invoiceStatus[1] == True:
            car.update("centralLock","UNLOCKED")
            data={"vin": VIN,"invokeStatus": invoiceStatus[0],"message": "","readyToUnlock": True ,"readyToUnlockUntil": 5} #whend would readyToUnlock be false?
            return JSONResponse(content=data, status_code=200)
        else:
            return NormalResponse(VIN, invoiceStatus[0],500)
         # FIXME:what if rejected what status code should be sent and all of the other BAD invoices
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

#ligts and horn

def lightsAndHorn(VIN:str, auth_header: AuthHeader = Header(...), command:str=None):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
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
                return NormalResponse(VIN, invoiceStatus[0])
            else:
                return NormalResponse(VIN, invoiceStatus[0],500) #FIXME: what if rejected what status code should be sent and all of the other BAD invoices
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.post("/vehicles/{VIN}/commands/flash")
def flash(VIN:str, auth_header: AuthHeader = Header(...)):
    return lightsAndHorn(VIN, auth_header, command="FLASH")
            
    
@app.post("/vehicles/{VIN}/commands/honk")
def honk(VIN:str, auth_header: AuthHeader = Header(...)):
    return lightsAndHorn(VIN, auth_header, command="HONK")


@app.post("/vehicles/{VIN}/commands/honk-and-flash")
def honkAndFlash(VIN:str, auth_header: AuthHeader = Header(...)):
    return lightsAndHorn(VIN, auth_header, command="HONK_AND_FLASH")

#statistics

@app.get("/vehicles/{VIN}/statistics") #STATIC
def statistics(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
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
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

#tyres
@app.get("/vehicles/{VIN}/tyres")
def tyres(VIN:str, auth_header: AuthHeader= Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data={"data":{"frontLeft":{"value":car.frontLeft,"timestamp":car.timestamp()},"frontRight":{"value":car.frontRight,"timestamp":car.timestamp()},"rearLeft":{"value":car.rearLeft,"timestamp":car.timestamp()},"rearRight":{"value":car.rearRight,"timestamp":car.timestamp()}}}
        return JSONResponse(content=data, status_code=200)
    
        


#commands 
@app.get("/vehicles/{VIN}/commands")
def commands(VIN:str, auth_header: AuthHeader = Header(...)):
    href=f"/v2/vehicles/{VIN}/commands/" 
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data = []
        for command in car.commands:
            data.append({
                "command": command,
                "href": href + command.lower().replace("_", "-")
            })
        return JSONResponse(content={"data": data}, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)



@app.get("/vehicles/{VIN}/command-accessibility")
def commandAccessibility(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        if car.availabilityStatus_value == "AVAILABLE" or car.availabilityStatus_value == "UNSPECIFIED": 
            data = {"availabilityStatus": {"value": car.availabilityStatus_value,"timestamp":car.timestamp()}}
        else:
            data = {"availabilityStatus": {"value": car.availabilityStatus_value, "unavailableReason": car.availabilityStatus_unavailableReason,"timestamp":car.timestamp()}}     
                
        return JSONResponse(content={"data": data}, status_code=200)  
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

                     
#Fuel section
@app.get("/vehicles/{VIN}/fuel")
def getFuel(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:   #TODO: unit and timestamp . docs says  thath only liters and % are  valid?
        FuelType = car.fuelType
        FuelLevel = str(car.fuelICE)
        FuelLevelElectric = str(car.fuelElectric)
        if FuelType == "PETROL" or FuelType == "DIESEL":
            data = {"data":{"fuelAmount":{"value" : FuelLevel, "unit":"l","timestamp":car.timestamp()}}} 
        elif FuelType == "ELECTRIC":
            data = {"data":{"batteryChargeLevel":{"value" : FuelLevelElectric, "unit":"%","timestamp":car.timestamp()}}} 
        elif FuelType == "HYBRID":
            data = {"data":{"fuelAmount":{"value" : FuelLevel, "unit":"l","timestamp":car.timestamp()}, "batteryChargeLevel":{"value" : FuelLevelElectric, "unit":"%","timestamp":car.timestamp()}}} 
        else:
            return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

    
#Odometer section
@app.get("/vehicles/{VIN}/odometer")
def getOdometer(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:   #Units and timestamp here again only km is valid Why volvo Why?
        Odometer =str(car.odometer)
        data = {"data":{"odometer" : { "value": Odometer, "unit" : "km","timestamp" : car.timestamp()}}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

    
#diagnostic section
@app.get("/vehicles/{VIN}/engine")
def engineDiagnostics(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data={"data":{"engineCoolantLevelWarning":{"value":car.engineCoolantLever,"timestamp":car.timestamp()},"oilLevelWarning":{"value":car.oillevel,"timestamp":car.timestamp()}}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.get("/vehicles/{VIN}/diagnostics")  # there is additional washer fluid data sent by the api but docs dont talk about it there ? and units?
def diagnostics(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        toService = car.timeToService
        
        unit=""
        if toService < 62:
            unit="days"
        else:
            unit="months"
            toService = toService//31
            
        if car.serviceWarning != "NO_WARNING" and car.serviceTrigger != "UNSPECIFIED":
            data={"data":{"serviceWarning":{"value":car.serviceWarning,"timestamp":car.timestamp()},"serviceTrigger":{"value":car.serviceTrigger,"timestamp":car.timestamp()},"engineHoursToService":{"value":car.engineHoursToService,"unit":"h","timestamp":car.timestamp()},"distanceToService":{"value":car.distanceToService,"unit":"km","timestamp":car.timestamp()},"washerFluidLevelWarning":{"value":car.washerFluidLevelWarning,"timestamp":car.timestamp()},"timeToService":{"value":toService,"unit":unit,"timestamp":car.timestamp()}}}
        else:
            data={"data":{"serviceWarning":{"value":car.serviceWarning,"timestamp":car.timestamp()},"engineHoursToService":{"value":car.engineHoursToService,"unit":"h","timestamp":car.timestamp()},"distanceToService":{"value":car.distanceToService,"unit":"km","timestamp":car.timestamp()},"washerFluidLevelWarning":{"value":car.washerFluidLevelWarning,"timestamp":car.timestamp()},"timeToService":{"value":toService,"unit":unit,"timestamp":car.timestamp()}}}
        
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)


@app.get("/vehicles/{VIN}/brakes")
def Brakes(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        data={"data":{"brakFluidLevelWarning":{"value":car.brakeFluidLevel,"timestamp":car.timestamp()}}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

app.get("/vehicles/{VIN}/warnings") #STATIC for now
def Warnings(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponse()
        elif str(e) == "Invalid VIN":
            return BadRequestResponse(VIN)
    else:
        timestamp = car.timestamp()
        # Possible values: UNSPECIFIED, NO_WARNING, FAILURE.
        data={
            "data": {
                "brakeLightLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "brakeLightCenterWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "brakeLightRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "fogLightFrontWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "fogLightRearWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "positionLightFrontLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "positionLightFrontRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "positionLightRearLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "positionLightRearRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "highBeamLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "highBeamRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "lowBeamLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "lowBeamRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "daytimeRunningLightLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "daytimeRunningLightRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "turnIndicationFrontLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "turnIndicationFrontRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "turnIndicationRearLeftWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "turnIndicationRearRightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "registrationPlateLightWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "sideMarkLightsWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "hazardLightsWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                },
                "reverseLightsWarning": {
                "value": "NO_WARNING",
                "timestamp": timestamp
                }
            }
            }
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)


#internal endpoints 

#TODO: add authentication func for internal endpoints API key and VIN without in future bearer token
@app.get("/internal")
def Internal():
   return internal.Internal() # here will be displayed any options like authetication using tokens and so on.


@app.get("/internal/terminal")
def Terminal():
    return internal.Terminal() #file response

#site section
@app.get("/internal/dashboard/dashboardWS.css")
def DashboardCSS():
    return internal.DashboardCSS() #file response


@app.get("/internal/dashboard/car")
def DashboardCar(key: str,VIN: str, request: Request):
    return internal.DashboardCar(key, VIN, request)
    
@app.get("/internal/dashboard/redirect")
def DashboardRedirect(key: str,VIN: str, request: Request):
    return internal.DashboardRedirect(key, VIN, request)
    
@app.websocket("/internal/dashboard/ws")
async def DashboardWS(websocket: WebSocket):
    return await internal.DashboardWS(websocket)
    
@app.post("/internal/dashboard/update") # html request here for dashboard
def DashboardUpdate(key: str,VIN: str, request: Request, attribute: str = Body(...), value: str = Body(...)):
    return internal.DashboardUpdate(key, VIN, request, attribute, value)
    
    
@app.get("/internal/dashboardCarSel.css")
def DashboardCarCSS():
    return internal.DashboardCarCSS() #file response

@app.get("/internal/dashboard")
def Dashboard(key: str, request: Request):
    return internal.Dashboard(key, request)

@app.get("/internal/welcome.css")
def WelcomeCSS():
    return internal.WelcomeCSS() #file response

@app.get("/internal/welcome")
def Welcome():
    return internal.Welcome() #file response

@app.get("/internal/welcome/Check")
def WelcomeCheck(vcc_api_key: str):
    return internal.WelcomeCheck(vcc_api_key)

@app.get("/internal/welcome/APIKey") 
def WelcomeAPIKey(request: Request):
    return internal.WelcomeAPIKey(request)

@app.post("/internal/dashboard/NewCar") 
def WelcomeNewCar(key: str, VIN: str):
    return internal.WelcomeNewCar(key, VIN)

#internal endpoints for testing and development. Not part of the official API.

@app.get("/internal/status") 
def getStatus(VIN: str = Header(...),vcc_api_key: str = Header(...)): 
    return internal.getStatus(VIN, vcc_api_key)
        
@app.websocket("/internal/status/ws") #todo: test this version
async def statusWS(websocket: WebSocket):
    return await internal.statusWS(websocket)

@app.post("/internal/update") # internal endpoint for updating car status without using commands (for testing purposes and dashboard) #TODO: implement this to html
def internal_update(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: str = Body(...), value: str = Body(...)):
    return internal.internal_update(VIN, vcc_api_key, attribute, value)


@app.post("/internal/updates") # to redo
def internal_updates(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: list = Body(...), value: list = Body(...)):
    return internal.internal_updates(VIN, vcc_api_key, attribute, value)


@app.get("/internal/APIKey")
def genAPIKey():                    
    return internal.genAPIKey()

@app.post("/internal/addCar")
def addCar(vcc_api_key: str = Header(...), VIN: str = Body(...), attributes: list = Body(...), values: list = Body(...)):
    return internal.addCar(vcc_api_key, VIN, attributes, values)

uvicorn.run(app)