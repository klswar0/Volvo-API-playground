from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

class AuthHeader(BaseModel):
    content_type: str = Field(..., alias="Content-Type")
    authorization: str = Field(...)
    vcc_api_key: str =Field(...,alias="vcc-api-key")

class Car(BaseModel):
    VIN: str = Field(...)
    climate: int =Field(default=0) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts?)
    commands:list
    availabilityStatus_value: str = Field(default="AVAILABLE") # AVAILABLE, UNAVAILABLE, UNSPECIFIED
    availabilityStatus_unavailableReason: str = Field(default="") # Description of why the vehicle is unavailable UNSPECIFIED, NO_INTERNET, POWER_SAVING_MODE, CAR_IN_USE
    
    
database = {
    "vcc_api_key": [Car(VIN="VIN123", climate=0, commands=["CLIMATIZATION_START", "CLIMATIZATION_STOP"])]
}

app = FastAPI()

def authenticate(auth_header: AuthHeader):
    if auth_header.vcc_api_key not in database:
        return False
    return True

# https://api.volvocars.com/connected-vehicle/v2/ section

#climetization commands
def climate(VIN:str, auth_header: AuthHeader = Header(...), command:str = "CLIMATIZATION_START"):
    if not authenticate(auth_header):
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
    else:
        for car in database[auth_header.vcc_api_key]:
            if car.VIN == VIN:
                if command not in car.commands:
                    return JSONResponse(content={"error": {"message": "NOT_FOUND","description": f"{command} is not supported by this vehicle"}}, status_code=404)
                elif command == "CLIMATIZATION_START" and car.climate == 0: # need to check if the climate is then the api throws an error or not ther same in stop verison
                    car.climate = 1
                    return JSONResponse(content={"vin": VIN ,"invokeStatus": "COMPLETED","message": "Extra information from the response."}, status_code=200)
                elif command == "CLIMATIZATION_STOP" and car.climate > 0:
                    car.climate = 0
                    return JSONResponse(content={"vin": VIN ,"invokeStatus": "COMPLETED","message": "Extra information from the response."}, status_code=200)
                
    return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400)


@app.get("/vehicles/{VIN}/commands/climatization-start")
def climateStart(VIN:str, auth_header: AuthHeader = Header(...)):
    return climate(VIN, auth_header, command="CLIMATIZATION_START")


@app.get("/vehicles/{VIN}/commands/climatization-stop")
def climateStop(VIN:str, auth_header: AuthHeader = Header(...)):
    return climate(VIN, auth_header, command="CLIMATIZATION_STOP")


#commands 
@app.get("/vehicles/{VIN}/commands")
def commands(VIN:str, auth_header: AuthHeader = Header(...)):
    href="https://api.volvocars.com/connected-vehicle/v2/vehicles/{vin}/commands/" # vin check if vin should be replaced with its value or not
    data=""
    if not authenticate(auth_header):
        return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
    else:
        for car in database[auth_header.vcc_api_key]:
            if car.VIN == VIN:
                for command in car.commands:
                    data +="{command: "+command+", href: "+href+command.lower().replace("_", "-")+"},"
                data = data[:-1]
                break
       
    data = "["+data+"]"
    return JSONResponse(content={"data": data}, status_code=200)
    # return JSONResponse(content={ "error": {"message": "BAD_REQUEST","description": "invalid VIN value. field:{VIN}"}}, status_code=400) # if vin is not found in database exception

# @app.get("/vehicles/{VIN}/commands/command-accessibility")
# def commandAccessibility(VIN:str, auth_header: AuthHeader = Header(...)):
#     data=""
#     if not authenticate(auth_header):
#         return JSONResponse(content={ "error": {"message": "UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)
#     else:
#         for car in database[auth_header.vcc_api_key]:
#             if car.VIN == VIN:
                
#     return JSONResponse(content={"placeholder": "PLACDHOLDER"}, status_code=200)

#

uvicorn.run(app)