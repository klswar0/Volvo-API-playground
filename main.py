from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn
import secrets
from datetime import datetime, timezone

options = {
    "fuelType": ["PETROL", "DIESEL", "ELECTRIC", "HYBRID"],
    "fuelICE": "int",
    "fuelElectric": "int",
    "odometer": "int",

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
    "rearRight": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"]
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
    Odometer: int = Field(default=0) 
    climate: bool =Field(default=False) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts? OR only engine has a timer)
    commands:list =Field(default=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP"])
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
    
    
    #additional parameters for error like if you want fail engine start nextInvoice status, last timestamp
    def timestamp(self):
        if self.availabilityStatus_value == "AVAILABLE":
            self.lastTimestamp = timestampGenerator()
        return self.lastTimestamp
            
    
    
    def checkValidity(self,attribute,value):
        if attribute in options:
            valid = options[attribute]
            if valid == "int":
                return isinstance(value, int)
            if value not in valid:
                return False
        return True

    def update(self,values,attribute):
        for i in range(len(attribute)):
            if self.checkValidity(attribute[i],values[i]):
                setattr(self, attribute[i], values[i])
                # additional coditions for last timestamp and next invoice status if needed
            else:
                return False
        return True
    
database = {
    "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID", commands=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP"])]
}

app = FastAPI()

def timestampGenerator():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

def authenticate(auth_header: AuthHeader):
    if auth_header.vcc_api_key not in database:
        raise ValueError("Invalid API key")

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
        invoiceStatus = "COMPLETED" # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
        if command not in car.commands:
            return NotSupportedResponse(command)
        elif command == "CLIMATIZATION_START": # need to check if the climate is then the api throws an error or not ther same in stop verison
            car.climate = True
            return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus,"message": "Extra information from the response."}, status_code=200)
        elif command == "CLIMATIZATION_STOP":
            car.climate = False
            return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus,"message": "Extra information from the response."}, status_code=200) 
    return JSONResponse(
    content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)
    # what if climate is already started? Need to check docs or a real car (not in mine doesnt have that option)


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
        invoiceStatus = "COMPLETED" # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
        if command not in car.commands:
            return NotSupportedResponse(command)
        elif command == "ENGINE_START":
            car.engineStatus = "RUNNING"
            car.engineTime = runtimeMinutes
            return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus,"message": "Extra information from the response."}, status_code=200)
        elif command == "ENGINE_STOP":
            car.engineStatus = "STOPPED"
            car.engineTime = 0
            return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus,"message": "Extra information from the response."}, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)
    # what if engine is already started? Need to check docs or a real car (not in mine doesnt have that option)



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
        invoiceStatus = "COMPLETED" # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        car.centralLock = "LOCKED"
        data = {{"data": {"vin": VIN,"invokeStatus": invoiceStatus,"message": ""}}}
        return JSONResponse(content=data, status_code=200)
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
#         car.centralLock = "LOCKED"
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
        invoiceStatus = "COMPLETED" # possible values: COMPLETED,DELIVERED, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, UNABLE_TO_LOCK_DOOR_OPEN, REJECTED, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE, UNKNOWN
        car.centralLock = "UNLOCKED" 
        data = {"data": {"vin": VIN,"invokeStatus": invoiceStatus,"message": ""}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

#ligts and horn

@app.post("/vehicles/{VIN}/commands/flash")
    #def flash 
    
@app.post("/vehicles/{VIN}/commands/honk")
    #def honk
@app.post("/vehicles/{VIN}/commands/honk-and-flash")
    #def honkAndFlash

#statistics

@app.get("/vehicles/{VIN}/statistics")
    #def statistics
    
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
        Odometer =str(car.Odometer)
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

#internal endpoints 

#TODO: add authentication func for internal endpoints API key and VIN without in future bearer token
@app.get("/internal")
def Internal():
    return JSONResponse(content={"message": "Welcome to the internal API"}, status_code=200) # here will be displayed any options like authetication using tokens and so on.


@app.get("/internal/dashboard")
def Dashbard():
    return FileResponse("dashboard.html")

@app.get("/internal/status") #todo: websocket version
def getStatus(VIN: str = Header(...),vcc_api_key: str = Header(...)):
    try:
        cars = database[vcc_api_key]
        for car in cars:
            if car.VIN == VIN:
                data = car.model_dump()
                return JSONResponse(content=data, status_code=200)
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "THIS IS INTERNAL API/invalid VIN value. field:{VIN}"}}, status_code=400)
    except KeyError:
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "THIS IS INTERNAL API/invalid API key value."}}, status_code=401)
    
@app.post("/internal/update") # internal endpoint for updating car status without using commands (for testing purposes and dashboard) #TODO: implement this to html
def internal_update(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: str = Body(...), value: str = Body(...)):
    try:
        cars = database[vcc_api_key]
        for car in cars:
            if car.VIN == VIN:
                if hasattr(car,attribute):
                    setattr(car,attribute, value)
                    return JSONResponse(content={"message": f"{attribute} updated successfully"}, status_code=200)    
                else:
                    return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute}"}}, status_code=400)
                
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "THIS IS INTERNAL API/invalid VIN value. field:{VIN}"}}, status_code=400)
                
    except KeyError:
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "THIS IS INTERNAL API/invalid API key value."}}, status_code=401)


@app.post("/internal/updates")
def internal_updates(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: list = Body(...), value: list = Body(...)):
    try:
        cars = database[vcc_api_key]
        for car in cars:
            if car.VIN == VIN:
                for i in range(len(attribute)):
                    if hasattr(car, attribute[i]):
                        setattr(car, attribute[i], value[i])
                    else:
                        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute[i]}"}}, status_code=400)
                return JSONResponse(content={"message": f"THIS IS INTERNAL API/attributes updated successfully"}, status_code=200)
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "THIS IS INTERNAL API/invalid VIN value. field:{VIN}"}}, status_code=400)
    except KeyError:
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "THIS IS INTERNAL API/invalid API key value."}}, status_code=401)

@app.get("/internal/APIKey")
def genAPIKey():                    
    api_key=secrets.token_hex(16)
    database[api_key] = []
    return JSONResponse(content={"message": f"THIS IS INTERNAL API/API key generated successfully: {api_key}"}, status_code=200)

@app.post("/internal/addCar")
def addCar(vcc_api_key: str = Header(...), VIN: str = Body(...), attributes: list = Body(...), values: list = Body(...)):
    try:
        cars =database[vcc_api_key]
        if any(car.VIN == VIN for car in cars):
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/Car with VIN {VIN} already exists."}}, status_code=400)
        
        new_car = Car(VIN=VIN)
        for attribute in attributes:
            if hasattr(new_car, attribute):
                setattr(new_car, attribute, values[attributes.index(attribute)])
            else:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute}"}}, status_code=400)
        cars.append(new_car)
        return JSONResponse(content={"message": f"THIS IS INTERNAL API/Car added successfully: {VIN}"}, status_code=200)

    except KeyError:
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "THIS IS INTERNAL API/invalid API key value."}}, status_code=401)

uvicorn.run(app)