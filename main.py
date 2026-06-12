from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

class AuthHeader(BaseModel):
    content_type: str = Field(..., alias="Content-Type")
    authorization: str = Field(...)
    vcc_api_key: str =Field(...,alias="vcc-api-key")

app = FastAPI()

# https://api.volvocars.com/connected-vehicle/v2/ section

#climetization commands
@app.get("/vehicles/{VIN}/commands/climatization-start")
def climateStart(VIN:str, auth_header: AuthHeader = Header(...)):
    # PLACEHODLER for code for interaction with dynamic backend
    return JSONResponse(content={"vin": VIN ,"invokeStatus": "WAITING","message": "Extra information from the response."}, status_code=200)

@app.get("/vehicles/{VIN}/commands/climatization-stop")
def climateStop(VIN:str, auth_header: AuthHeader = Header(...)):
    # PLACEHODLER for code for interaction with dynamic backend
    return JSONResponse(content={"vin": VIN ,"invokeStatus": "WAITING","message": "Extra information from the response."}, status_code=200)


#commands 
@app.get("/vehicles/{VIN}/commands")
def commands(VIN:str, auth_header: AuthHeader = Header(...)):
    # PLACEHODLER for code for interaction with dynamic backend
    return JSONResponse(content={"placeholder": "PLACDHOLDER"}, status_code=200)

@app.get("/vehicles/{VIN}/commands/command-accessibility")
def commandAccessibility(VIN:str, auth_header: AuthHeader = Header(...)):
    # PLACEHODLER for code for interaction with dynamic backend
    return JSONResponse(content={"placeholder": "PLACDHOLDER"}, status_code=200)

#

uvicorn.run(app)