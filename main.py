from fastapi import Body, FastAPI, Header ,Request ,Query, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse ,HTMLResponse 
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field 
import uvicorn
import json
import secrets
import asyncio
from datetime import datetime, timezone
from typing import Dict, Set

#TODO: redo internal responses
templates = Jinja2Templates(directory="templates")

startUp={
    "Validation": True,
    "Dashboard": True,# not implemented yet
    "Websocket": True,# not implemented yet
    "TOKENcheck": False # not implemented yet
}


options = {
    "fuelType": ["PETROL", "DIESEL", "ELECTRIC", "HYBRID"],
    "fuelICE": "int", # in liters
    "fuelElectric": "int", # in % so 0-100
    "odometer": "int", # 0-infinity in km

    "climate": [True, False],
    "engine": ["ENGINE_START", "ENGINE_STOP"],
    "availabilityStatus_value": ["AVAILABLE", "UNAVAILABLE", "UNSPECIFIED"],
    "availabilityStatus_unavailableReason": ["UNSPECIFIED", "NO_INTERNET", "POWER_SAVING_MODE", "CAR_IN_USE"],
    "engineStatus": ["STOPPED", "RUNNING"],
    "engineCoolantLever": ["UNSPECIFIED", "NO_WARNING", "TOO_LOW"],
    "oillevel": ["UNSPECIFIED", "NO_WARNING", "SERVICE_REQUIRED", "TOO_LOW", "TOO_HIGH"],
    "serviceWarning": ["UNSPECIFIED", "NO_WARNING", "UNKNOWN_WARNING", "REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE", "ENGINE_HOURS_ALMOST_TIME_FOR_SERVICE", "DISTANCE_DRIVEN_ALMOST_TIME_FOR_SERVICE", "REGULAR_MAINTENANCE_TIME_FOR_SERVICE", "ENGINE_HOURS_TIME_FOR_SERVICE", "DISTANCE_DRIVEN_TIME_FOR_SERVICE", "REGULAR_MAINTENANCE_OVERDUE_FOR_SERVICE", "ENGINE_HOURS_OVERDUE_FOR_SERVICE", "DISTANCE_DRIVEN_OVERDUE_FOR_SERVICE"],
    "serviceTrigger": ["CALENDAR_TIME", "DISTANCE", "ENGINE_HOURS", "UNSPECIFIED", "UNKNOWN"],
    "washerFluidLevelWarning": ["UNSPECIFIED", "NO_WARNING", "TOO_LOW"],
    "brakeFluidLevel": ["UNSPECIFIED", "NO_WARNING", "TOO_LOW"],
    "frontLeftWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "frontRightWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearLeftWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearRightWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "sunroof": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "centralLock": ["UNSPECIFIED", "UNLOCKED", "LOCKED"],
    "frontLeftDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "frontRightDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearLeftDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearRightDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "tailGate": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "hood": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "tankLid": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "frontLeft": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "frontRight": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "rearLeft": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "rearRight": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "nextInvoiceStatus": ["RUNNING", "WAITING", "COMPLETED", "REJECTED", "UNKNOWN", "TIMEOUT", "CONNECTION_FAILURE", "VEHICLE_IN_SLEEP", "DELIVERED", "CAR_ERROR", "NOT_ALLOWED_PRIVACY_ENABLED", "NOT_ALLOWED_WRONG_USAGE_MODE"],
    "lightTimestamp": "", 
}

class AuthHeader(BaseModel):
    content_type: str = Field(default="application/json", alias="Content-Type")
    authorization: str =Field(default="") #= Field(...) # NOT IMPLEMENTED
    vcc_api_key: str =Field(...,alias="vcc-api-key")

class Car(BaseModel):
    VIN: str = Field(...)
    fuelType: str = Field(default="HYBRID") #possible values: PETROL, DIESEL, ELECTRIC, HYBRID
    fuelICE:int = Field(default=0) # fuel level for petrol and diesel cars
    fuelElectric:int = Field(default=0) # fuel level for electric and hybrid cars
    odometer: int = Field(default=0) 
    climate: bool =Field(default=False) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts? OR only engine has a timer)
    commands:list =Field(default=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP","FLASH","HONK", "HONK_AND_FLASH","LOCK","UNLOCK"]) # and reduced guard lock but not implemented yet. TO IMPLEMENT
    availabilityStatus_value: str = Field(default="AVAILABLE") # AVAILABLE, UNAVAILABLE, UNSPECIFIED # AVAILABLE is needed for any command TO IMPLEMENT
    availabilityStatus_unavailableReason: str = Field(default="") # Description of why the vehicle is unavailable UNSPECIFIED, NO_INTERNET, POWER_SAVING_MODE, CAR_IN_USE
    engineStatus:str = Field(default="STOPPED") # possible values: STOPPED, RUNNING
    engineTime:int = Field(default=0) # TODO:how long should engine run in future time based (one variable that is time when engine will be turned off not (enginestatus and enginetime))
    
    #diagnostic parameters
    engineCoolantLever:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    oillevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, SERVICE_REQUIRED, TOO_LOW, TOO_HIGH.
    
    serviceWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, UNKNOWN_WARNING, REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE, ENGINE_HOURS_ALMOST_TIME_FOR_SERVICE, DISTANCE_DRIVEN_ALMOST_TIME_FOR_SERVICE, REGULAR_MAINTENANCE_TIME_FOR_SERVICE, ENGINE_HOURS_TIME_FOR_SERVICE, DISTANCE_DRIVEN_TIME_FOR_SERVICE, REGULAR_MAINTENANCE_OVERDUE_FOR_SERVICE, ENGINE_HOURS_OVERDUE_FOR_SERVICE, DISTANCE_DRIVEN_OVERDUE_FOR_SERVICE.
    serviceTrigger:str =Field(default="UNSPECIFIED") #Values: CALENDAR_TIME, DISTANCE, ENGINE_HOURS, UNSPECIFIED, UNKNOWN.
    engineHoursToService:int = Field(default=0) # in hours
    distanceToService:int = Field(default=0) # in km
    timeToService:int = Field(default=0) # in days (or months. need to check when they change to months. stored in days sent in both?)
    
    washerFluidLevelWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW. # not sure no infornation about it in official docs but sent thru real API response

    brakeFluidLevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    
    
    
    #windows
    #Values: UNSPECIFIED, OPEN, CLOSED, AJAR- not fully open? Mostly for sunroof .
    frontLeftWindow:str = Field(default="CLOSED")  
    frontRightWindow:str = Field(default="CLOSED") 
    rearRightWindow:str = Field(default="CLOSED")
    rearLeftWindow:str = Field(default="CLOSED")
    sunroof:str = Field(default="CLOSED") # UNSPECIFIED means mostly that car doesnt have sunroof
    
    #doors and locks
    
    centralLock:str = Field(default="UNLOCKED") #Possible values: UNSPECIFIED, UNLOCKED, LOCKED.
    
    #Values: UNSPECIFIED, OPEN, CLOSED, AJAR.
    frontLeftDoor:str = Field(default="CLOSED") 
    frontRightDoor:str = Field(default="CLOSED") 
    rearLeftDoor:str = Field(default="CLOSED")
    rearRightDoor:str = Field(default="CLOSED") 
    tailGate:str = Field(default="CLOSED") 
    hood:str = Field(default="CLOSED") 
    tankLid:str = Field(default="CLOSED") # UNSPECIFIED means mostly that car doesnt have sensors
    
    #tires value UNSPECIFIED, NO_WARNING, VERY_LOW_PRESSURE, LOW_PRESSURE, HIGH_PRESSURE.
    frontLeft:str = Field(default="NO_WARNING")
    frontRight:str = Field(default="NO_WARNING")
    rearLeft:str = Field(default="NO_WARNING")
    rearRight:str = Field(default="NO_WARNING")
    
    lastTimestamp:str = Field(default="") #set if not available
    
    
    lightTimestamp:str = Field(default="")#set if light commands is sent
    
    hornTimestamp:str = Field(default="") # set if horn commands is sent

    nextInvoiceStatus:str = Field(default="") # Possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
    # running available for climate or engine commands
    
    #additional parameters for error like if you want fail engine start nextInvoice status, last timestamp
    def timestamp(self):
        if self.availabilityStatus_value == "AVAILABLE":
            self.lastTimestamp = timestampGenerator()
        return self.lastTimestamp
            
    
    
    def checkValidity(self,attribute,value):
        if startUp["Validation"] == False:
            return True
        
        if attribute in options:
            valid = options[attribute]
            if valid == "":
                return True
            if valid == "int":
                value=int(value) #check if value is int todo
                return True
            if value not in valid:
                return False
        return True
    
    #TODO: invoices are difrent for locks 
    def InvoiceStatus(self, command, status=None): #status true turning ON false turning off TODO update climate and engine becouse know its not working for climate stop and engine stop
        if self.nextInvoiceStatus == "":
            if command == "climate":
                if self.climate == True and status == True:
                    return ["RUNNING",True]
            elif command == "engine":
                if self.engineStatus == "RUNNING" and status == True:
                    return ["RUNNING",True]
                
            return ["COMPLETED",True]
        if self.nextInvoiceStatus == "RUNNING":
            if command == "locks":
                return ["COMPLETED",True]
            elif command == "lights":
                return ["COMPLETED",True]
            
        if self.nextInvoiceStatus == "REJECTED" or self.nextInvoiceStatus == "UNKNOWN" or self.nextInvoiceStatus == "TIMEOUT" or self.nextInvoiceStatus == "CONNECTION_FAILURE" or self.nextInvoiceStatus == "VEHICLE_IN_SLEEP" or self.nextInvoiceStatus == "CAR_ERROR" or self.nextInvoiceStatus == "NOT_ALLOWED_PRIVACY_ENABLED" or self.nextInvoiceStatus == "NOT_ALLOWED_WRONG_USAGE_MODE":
            return [self.nextInvoiceStatus,False]
        return [self.nextInvoiceStatus,True]

    def update(self,attribute,value):
        if self.checkValidity(attribute,value):
                setattr(self, attribute, value)
                notifier.trigger_update(self.VIN, self, changed_attribute=attribute)
                # additional coditions for last timestamp and next invoice status if needed
        else:
            return False
        return True
    
database = {
    "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID", commands=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP","FLASH","HONK", "HONK_AND_FLASH","LOCK","UNLOCK"])] #TODO more commands checks
}

app = FastAPI()

class websocketNotifier:
    def __init__(self):
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
    def subscribe(self, vin: str) -> asyncio.Queue:
        queue = asyncio.Queue()
        self._subscribers.setdefault(vin, set()).add(queue)
        return queue

    def unsubscribe(self, vin: str, queue: asyncio.Queue):
        if vin in self._subscribers:
            self._subscribers[vin].discard(queue)
            if not self._subscribers[vin]:
                del self._subscribers[vin]

    def trigger_update(self, vin: str, car_instance, changed_attribute: str):
        """Call this function whenever a car's data changes in your database."""
        if vin in self._subscribers:    
            update_packet = {
                "VIN": vin,
                "attribute_name": changed_attribute,
                "current_value": getattr(car_instance, changed_attribute),
            }
            for queue in self._subscribers[vin]:
                queue.put_nowait(update_packet)
        
notifier = websocketNotifier()

def timestampGenerator():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def authenticate(auth_header: AuthHeader):
    if auth_header.vcc_api_key not in database:
        raise ValueError("Invalid API key")
    if startUp["TOKENcheck"] == True:
        if auth_header.authorization != "Bearer valid_token": # real token endpoints needed
            raise ValueError("Invalid token")

def UnauthorizedResponse():
    return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)

def BadRequestResponse(VIN:str):
    return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": f"invalid VIN value. field:{VIN}"}}, status_code=400)

def NotSupportedResponse(command:str):
    return JSONResponse(content={"error": {"message": "NOT_FOUND","description": f"{command} is not supported by this vehicle"}}, status_code=404)
    

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

#TODO Vehicle details


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
                    return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus[0],"message": "Extra information from the response."}, status_code=200)
            elif command == "CLIMATIZATION_STOP":
                invoiceStatus = car.InvoiceStatus("climate",False) # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
                if invoiceStatus[1]:
                    car.update("climate",False)
                    return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus[0],"message": "Extra information from the response."}, status_code=200)
            
            if invoiceStatus[1] == False:
                return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus[0],"message": "Extra information from the response."}, status_code=500) # what if rejected what status code should be sent 
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
                    return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus[0],"message": "Extra information from the response."}, status_code=200)
            elif command == "ENGINE_STOP":
                invoiceStatus = car.InvoiceStatus("engine",False)
                if invoiceStatus[1]:
                    car.update("engineStatus", "STOPPED")
                    car.update("engineTime", 0)
                return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus[0],"message": "Extra information from the response."}, status_code=200)
            
            if invoiceStatus[1] == False:
                return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus[0],"message": "Extra information from the response."}, status_code=500) # what if rejected what status code should be sent and all of the other BAD invoices
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
        invoiceStatus = car.InvoiceStatus("locks") # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        if invoiceStatus[1] == True:
            car.update("centralLock","UNLOCKED")
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=200)
        else:
            data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
            return JSONResponse(content=data, status_code=500) # what if rejected what status code should be sent and all of the other BAD invoices
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
                data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
                return JSONResponse(content=data, status_code=200)
            else:
                data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus[0],"message": ""}}
                return JSONResponse(content=data, status_code=500) # what if rejected what status code should be sent and all of the other BAD invoices
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
    return JSONResponse(content={"message": "Welcome to the internal API", "description": startUp}, status_code=200) # here will be displayed any options like authetication using tokens and so on.


@app.get("/internal/terminal")
def Terminal():
    return FileResponse("templates/terminal.html")
#site section
@app.get("/internal/dashboard/dashboardWS.css")
def DashbardCSS():
    return FileResponse("templates/dashboardWS.css")


@app.get("/internal/dashboard/car")
def Dashbard(key: str,VIN: str, request: Request):
    try:
        car = VINHandlingInternal(VIN, key)
        data={"VIN":VIN,"key":key}
        return templates.TemplateResponse(name="dashboard.html", request=request, context=data)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    
@app.get("/internal/dashboard/redirect")
def Dashbard(key: str,VIN: str, request: Request):
    try:
        response = Response()
        response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
        return response
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    
@app.websocket("/internal/dashboard/ws")
async def Dashbard(websocket: WebSocket):
    await websocket.accept()
    params = websocket.query_params
    vin = params.get("VIN")
    api_key = params.get("key")
    queue = notifier.subscribe(vin)
    print(f"Connected car: {vin} with key: {api_key}")
    try:
        car = VINHandlingInternal(vin, api_key)
        if not car:
            raise ValueError("Car not found or invalid API key")
        car_data = car.model_dump()
        
        car_data["key"] = api_key
        template = templates.get_template("dashboardUpdate.html")
        html=template.render(car_data)
        await websocket.send_text(html)
        
        while True:
            packet = await queue.get()
    
            packet["key"] = api_key
            
            data={"data": packet["attribute_name"],"value": packet["current_value"],"options":options[packet["attribute_name"]],"VIN": packet["VIN"],"key": api_key}
            template = templates.get_template("dashboardTemplate.html")
            html = template.render(data)
            
            await websocket.send_text(html)
            
    except WebSocketDisconnect:
        print("Dashboard disconnected")
    except ValueError as e:
        await websocket.send_text("Invalid API key or VIN")
        await websocket.close()
        return
    finally:
        notifier.unsubscribe(vin, queue)
        print(f"Disconnected car: {vin} with key: {api_key}")
    
@app.post("/internal/dashboard/update") # html request here for dashboard
def DashbardUpdate(key: str,VIN: str, request: Request, attribute: str = Body(...), value: str = Body(...)):
    try:
        response=update(VIN, attribute, value, key)
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
    
    
@app.get("/internal/dashboardCarSel.css")
def DashbardCSS():
    return FileResponse("templates/dashboardCarSel.css")

@app.get("/internal/dashboard")
def Dashbard(key: str, request: Request):
    try:
        authenticateInternal(key)
        cars = database[key]
        VINs = []
        for car in cars:
            VINs.append(car.VIN)
        return templates.TemplateResponse(name="dashboardCarSel.html", request=request, context={"VINs": VINs})
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")   
    
@app.get("/internal/welcome.css")
def DashbardCSS():
    return FileResponse("templates/welcome.css")

@app.get("/internal/welcome")
def Welcome():
    return FileResponse("templates/welcome.html")

@app.get("/internal/welcome/Check")
def WelcomeCheck(vcc_api_key: str):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    
    response = Response()
    response.headers["HX-Redirect"] = f"/internal/dashboard?key={vcc_api_key}"
    return response

@app.get("/internal/welcome/APIKey") 
def WelcomeAPIKey(request: Request):
    data=genAPIKey().body.decode("utf-8")
    data = json.loads(data)
    data = data["message"]
    return templates.TemplateResponse(request=request,name="welcomeAPI.html",context={"api_key": data})

@app.post("/internal/dashboard/NewCar") 
def WelcomeNewCar(key: str, VIN: str):
    try:
        if key not in database:
            raise ValueError("Invalid API key")
        try:
           car = VINHandlingInternal(VIN, key)
           return HTMLResponse(content="<p style=\"color:red\">Car already exists</p>")
        except ValueError:
            new_car = Car(VIN)
            database[key].append(new_car)
            response = Response()
            response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
            return response
       
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Car already exists/internal error {e}</p>")

#internal endpoints for testing and dashboard purposes. Not part of the official API.

def UnauthorizedResponseInternal():
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)

def BadRequestResponseInternal(VIN:str):
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/BAD_REQUEST","description": f"invalid VIN value. field:{VIN}"}}, status_code=400)

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
        return car.update(attribute, value)
    except ValueError as e:
        raise ValueError(str(e))


@app.get("/internal/status") 
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
        
@app.websocket("/internal/status/ws") #todo: test this version
async def Dashbard(websocket: WebSocket):
    if startUp["Websocket"] == False:
        return
    
    await websocket.accept()
    params = websocket.query_params
    vin = params.get("VIN")
    api_key = params.get("key")
    queue = notifier.subscribe(vin)
    print(f"Connected car: {vin} with key: {api_key}")
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

@app.post("/internal/update") # internal endpoint for updating car status without using commands (for testing purposes and dashboard) #TODO: implement this to html
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


@app.post("/internal/updates") # to redo
def internal_updates(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: list = Body(...), value: list = Body(...)):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        for i in range(len(attribute)):
            if hasattr(car, attribute[i]):
                setattr(car, attribute[i], value[i])
            else:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute[i]}"}}, status_code=400)
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


@app.get("/internal/APIKey")
def genAPIKey():                    
    api_key=secrets.token_hex(16)
    database[api_key] = []
    return JSONResponse(content={"message": api_key,"description": f"THIS IS INTERNAL API/API key generated successfully"}, status_code=200)

@app.post("/internal/addCar")
def addCar(vcc_api_key: str = Header(...), VIN: str = Body(...), attributes: list = Body(...), values: list = Body(...)):
    try:
        cars =database[vcc_api_key]
        if any(car.VIN == VIN for car in cars):
            return BadRequestResponseInternal(VIN)
        
        new_car = Car(VIN=VIN)
        for attribute in attributes:
            if hasattr(new_car, attribute):
                setattr(new_car, attribute, values[attributes.index(attribute)])
            else:
                return BadRequestResponseInternal(VIN)
        cars.append(new_car)
        return JSONResponse(content={"message": f"THIS IS INTERNAL API/Car added successfully: {VIN}"}, status_code=200)

    except KeyError:
        return UnauthorizedResponseInternal()

uvicorn.run(app)