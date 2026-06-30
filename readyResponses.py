
from fastapi.responses import JSONResponse

        
def ErrorResponse(message:str, description:str, status_code:int):
    return JSONResponse(content={ "error": {"message": message,"description": description}}, status_code=status_code)

def UnauthorizedResponse():
    return ErrorResponse("UNAUTHORIZED","invalid API key value.",401)

def BadRequestResponse(VIN:str):
    return ErrorResponse("BAD_REQUEST", f"invalid VIN value. field:{VIN}", 400)

def NotSupportedResponse(command:str):
    return ErrorResponse("NOT_FOUND", f"{command} is not supported by this vehicle", 404)

def NormalResponse(VINL:str, invoiceStatus:str, message:str=None, status_code:int=200):
    return JSONResponse(content={"vin": VINL ,"invokeStatus": invoiceStatus,"message": message}, status_code=status_code)
    



def UnauthorizedResponseInternal():
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)

def BadRequestResponseInternal(VIN:str):
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/BAD_REQUEST","description": f"invalid VIN value. field:{VIN}"}}, status_code=400)

