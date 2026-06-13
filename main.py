from fastapi import Body, FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

class AuthHeader(BaseModel):
    content_type: str = Field(..., alias="Content-Type")
    authorization: str = Field(...)
    vcc_api_key: str =Field(...,alias="vcc-api-key")

class Car(BaseModel):
    VIN: str = Field(...)
    fuelType: str = Field(...) #possible values: PETROL, DIESEL, ELECTRIC, HYBRID
    fuelICE:int = Field(default=0) # fuel level for petrol and diesel cars
    fuelElectric:int = Field(default=0) # fuel level for electric and hybrid cars
    climate: int =Field(default=0) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts? OR only engine has a timer)
    commands:list
    availabilityStatus_value: str = Field(default="AVAILABLE") # AVAILABLE, UNAVAILABLE, UNSPECIFIED
    availabilityStatus_unavailableReason: str = Field(default="") # Description of why the vehicle is unavailable UNSPECIFIED, NO_INTERNET, POWER_SAVING_MODE, CAR_IN_USE
    engineStatus:str = Field(default="STOPPED") # possible values: STOPPED, RUNNING
    engineTime:int = Field(default=0) # TODO:how long should engine run in future time based (one variable that is time when engine will be turned off not (enginestatus and enginetime))
    
    
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
    else:   #TODO: unit and timestamp
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
    
    
#




uvicorn.run(app)