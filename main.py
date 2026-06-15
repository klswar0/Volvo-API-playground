from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field
import uvicorn


# WARNING: this code is made for eu cars only (dev site states only km and liters are valid so there needs to be a USA developer site.(for sure there is a diffrent server for them) )
# API states USA region support maybe just for simplicity they use km and liters and so on.

class AuthHeader(BaseModel):
    content_type: str = Field(default="application/json", alias="Content-Type")
    authorization: str =Field(default="") #= Field(...) # NOT IMPLEMENTED
    vcc_api_key: str =Field(...,alias="vcc-api-key")

class Car(BaseModel):
    VIN: str = Field(...)
    fuelType: str = Field(...) #possible values: PETROL, DIESEL, ELECTRIC, HYBRID
    fuelICE:int = Field(default=0) # fuel level for petrol and diesel cars
    fuelElectric:int = Field(default=0) # fuel level for electric and hybrid cars
    Odometer: int = Field(default=0) 
    climate: int =Field(default=0) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts? OR only engine has a timer)
    commands:list
    availabilityStatus_value: str = Field(default="AVAILABLE") # AVAILABLE, UNAVAILABLE, UNSPECIFIED # AVAILABLE is needed for any command TO IMPLEMENT
    availabilityStatus_unavailableReason: str = Field(default="") # Description of why the vehicle is unavailable UNSPECIFIED, NO_INTERNET, POWER_SAVING_MODE, CAR_IN_USE
    engineStatus:str = Field(default="STOPPED") # possible values: STOPPED, RUNNING
    engineTime:int = Field(default=0) # TODO:how long should engine run in future time based (one variable that is time when engine will be turned off not (enginestatus and enginetime))
    
    #diagnostic parameters
    engineCoolantLever:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    oillevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, SERVICE_REQUIRED, TOO_LOW, TOO_HIGH.
    
    serviceWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, UNKNOWN_WARNING, REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE, ENGINE_HOURS_ALMOST_TIME_FOR_SERVICE, DISTANCE_DRIVEN_ALMOST_TIME_FOR_SERVICE, REGULAR_MAINTENANCE_TIME_FOR_SERVICE, ENGINE_HOURS_TIME_FOR_SERVICE, DISTANCE_DRIVEN_TIME_FOR_SERVICE, REGULAR_MAINTENANCE_OVERDUE_FOR_SERVICE, ENGINE_HOURS_OVERDUE_FOR_SERVICE, DISTANCE_DRIVEN_OVERDUE_FOR_SERVICE.
    serviceTrigger:str #Values: CALENDAR_TIME, DISTANCE, ENGINE_HOURS, UNSPECIFIED, UNKNOWN.
    engineHoursToService:int = Field(default=0) # in hours
    distanceToService:int = Field(default=0) # in km
    timeToService:int = Field(default=0) # in days (or months. need to check when they change to months. stored in days sent in both?)
    
    washerFluidLevelWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW. # not sure no infornation about it in official docs but sent thru real API response

    brakeFluidLevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    
    #additional parameters for error like if you want fail engine start nextInvoice status, last timestamp
    
database = {
    "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID", climate=0, commands=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP"])]
}

app = FastAPI()

def authenticate(auth_header: AuthHeader):
    if auth_header.vcc_api_key not in database:
        raise ValueError("Invalid API key")
    

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
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:
        invoiceStatus = "COMPLETED" # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
        if command not in car.commands:
            return JSONResponse(content={"error": {"message": "NOT_FOUND","description": f"{command} is not supported by this vehicle"}}, status_code=404)
        elif command == "CLIMATIZATION_START" and car.climate == 0: # need to check if the climate is then the api throws an error or not ther same in stop verison
            car.climate = 1
            return JSONResponse(content={"vin": VIN ,"invokeStatus": invoiceStatus,"message": "Extra information from the response."}, status_code=200)
        elif command == "CLIMATIZATION_STOP" and car.climate > 0:
            car.climate = 0
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
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:
        invoiceStatus = "COMPLETED" # possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
        if command not in car.commands:
            return JSONResponse(content={"error": {"message": "NOT_FOUND","description": f"{command} is not supported by this vehicle"}}, status_code=404)
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
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
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

#commands 
@app.get("/vehicles/{VIN}/commands")
def commands(VIN:str, auth_header: AuthHeader = Header(...)):
    href=f"/v2/vehicles/{VIN}/commands/" 
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
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
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:
        if car.availabilityStatus_value == "AVAILABLE" or car.availabilityStatus_value == "UNSPECIFIED": 
            data = {"availabilityStatus": {"value": car.availabilityStatus_value,"timestamp":"placeholder"}}
        else:
            data = {"availabilityStatus": {"value": car.availabilityStatus_value, "unavailableReason": car.availabilityStatus_unavailableReason,"timestamp":"placeholder"}}     
                
        return JSONResponse(content={"data": data}, status_code=200)  
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

                     
#Fuel section
@app.get("/vehicles/{VIN}/fuel")
def getFuel(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:   #TODO: unit and timestamp . docs says  thath only liters and % are  valid?
        FuelType = car.fuelType
        FuelLevel = str(car.fuelICE)
        FuelLevelElectric = str(car.fuelElectric)
        if FuelType == "PETROL" or FuelType == "DIESEL":
            data = {"data":{"fuelAmount":{"value" : FuelLevel, "unit":"l","timestamp":"placeholder"}}} 
        elif FuelType == "ELECTRIC":
            data = {"data":{"batteryChargeLevel":{"value" : FuelLevelElectric, "unit":"%","timestamp":"placeholder"}}} 
        elif FuelType == "HYBRID":
            data = {"data":{"fuelAmount":{"value" : FuelLevel, "unit":"l","timestamp":"placeholder"}, "batteryChargeLevel":{"value" : FuelLevelElectric, "unit":"%","timestamp":"placeholder"}}} 
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
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:   #Units and timestamp here again only km is valid Why volvo Why?
        Odometer =str(car.Odometer)
        data = {"data":{"odometer" : { "value": Odometer, "unit" : "km","timestamp" : "placeholder"}}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

    
#diagnostic section
@app.get("/vehicles/{VIN}/engine")
def engineDiagnostics(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:
        data={"data":{"engineCoolantLevelWarning":{"value":car.engineCoolantLever,"timestamp":"placeholder"},"oilLevelWarning":{"value":car.oillevel,"timestamp":"placeholder"}}}
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)

@app.get("/vehicles/{VIN}/diagnostics")  # there is additional washer fluid data sent by the api but docs dont talk about it there ? and units?
def diagnostics(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:
        toService = car.timeToService
        
        unit=""
        if toService < 62:
            unit="days"
        else:
            unit="months"
            toService = toService//31
            
        if car.serviceWarning != "NO_WARNING" and car.serviceTrigger != "UNSPECIFIED":
            data={"data":{"serviceWarning":{"value":car.serviceWarning,"timestamp":"placeholder"},"serviceTrigger":{"value":car.serviceTrigger,"timestamp":"placholder"},"engineHoursToService":{"value":car.engineHoursToService,"unit":"h","timestamp":"placeholder"},"distanceToService":{"value":car.distanceToService,"unit":"km","timestamp":"placeholder"},"washerFluidLevelWarning":{"value":car.washerFluidLevelWarning,"timestamp":"placeholder"},"timeToService":{"value":toService,"unit":unit,"timestamp":"placeholder"}}}
        else:
            data={"data":{"serviceWarning":{"value":car.serviceWarning,"timestamp":"placeholder"},"engineHoursToService":{"value":car.engineHoursToService,"unit":"h","timestamp":"placeholder"},"distanceToService":{"value":car.distanceToService,"unit":"km","timestamp":"placeholder"},"washerFluidLevelWarning":{"value":car.washerFluidLevelWarning,"timestamp":"placeholder"},"timeToService":{"value":toService,"unit":unit,"timestamp":"placeholder"}}}
        
        return JSONResponse(content=data, status_code=200)
    return JSONResponse(content={"error": {"message": "INTERNAL_SERVER_ERROR", "description": "An internal server error occurred"}}, status_code=500)





@app.get("/vehicles/{VIN}/brakes")
def Brakes(VIN:str, auth_header: AuthHeader = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
        elif str(e) == "Invalid VIN":
            return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)
    else:
        data={"data":{"brakFluidLevelWarning":{"value":car.brakeFluidLevel,"timestamp":"placeholder"}}}
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
                data = {
                    "VIN": car.VIN,
                    "fuelType": car.fuelType,
                    "fuelICE": car.fuelICE,
                    "fuelElectric": car.fuelElectric,
                    "Odometer": car.Odometer,
                    "climate": car.climate,
                    "commands": car.commands,
                    "availabilityStatus_value": car.availabilityStatus_value,
                    "availabilityStatus_unavailableReason": car.availabilityStatus_unavailableReason,
                    "engineStatus": car.engineStatus,
                    "engineTime": car.engineTime
                }
                return JSONResponse(content=data, status_code=200)
        return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": "THIS IS INTERNAL API/invalid VIN value. field:{VIN}"}}, status_code=400)
    except KeyError:
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "THIS IS INTERNAL API/invalid API key value."}}, status_code=401)
    
@app.post("/internal/update") # internal endpoint for updating car status without using commands (for testing purposes and dashboard) #TODO: implement this to html
def update(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: str = Body(...), value: str = Body(...)):
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
                    
    
    
uvicorn.run(app)