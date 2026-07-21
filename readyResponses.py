
from fastapi.responses import JSONResponse



def autoErrorResponse(e:str, VIN:str=None):
    if str(e) == "Invalid API key" or str(e) == "Invalid access token":
        return UnauthorizedResponse(str(e))
    elif str(e) == "Invalid VIN":
        return BadRequestResponse(VIN)
    elif str(e) == "Invalid Content-Type":
        return ErrorResponse("BAD_REQUEST", "Invalid Content-Type. Only 'application/json' is accepted.", 400)
    else:
        return ErrorResponse("INTERNAL_SERVER_ERROR", f"An unexpected error occurred. INFO:{e}", 500)

        
def ErrorResponse(message:str, description:str, status_code:int):
    return JSONResponse(content={ "error": {"message": message,"description": description}}, status_code=status_code)

def UnauthorizedResponse(e:str):
    return ErrorResponse("UNAUTHORIZED","Full authentication is required to access this resource. INFO:"+e,401)


def BadRequestResponse(VIN:str):
    return ErrorResponse("BAD_REQUEST", f"invalid VIN value. field:{VIN}", 400)

def NotSupportedResponse(command:str):
    return ErrorResponse("NOT_FOUND", f"{command} is not supported by this vehicle", 403)

def NormalResponse(VINL:str, invoiceStatus:str, message:str=None, status_code:int=200):
    return JSONResponse(content={ "data": {"vin": VINL ,"invokeStatus": invoiceStatus,"message": message}}, status_code=status_code)
    



def UnauthorizedResponseInternal():
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)

def BadRequestResponseInternal(VIN:str):
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/BAD_REQUEST","description": f"invalid VIN value. field:{VIN}"}}, status_code=400)

