
from turtle import st # why here? auto imported?

from fastapi.responses import JSONResponse



def autoErrorResponse(e:str, VIN:str=None, headers:dict=None):
    if str(e) == "Invalid API key" or str(e) == "Invalid access token":
        return UnauthorizedResponse(str(e), headers)
    elif str(e) == "Invalid VIN":
        return BadRequestResponse(VIN, headers)
    elif str(e) == "Invalid Content-Type":
        return ErrorResponse("BAD_REQUEST", "Invalid Content-Type. Only 'application/json' is accepted.", 400, headers=headers)
    elif str(e) == "Invalid Accept header":
            return ErrorResponse("BAD_REQUEST", "Invalid Accept header. Only 'application/json' is accepted.", 406, headers=headers)
    else:
        return ErrorResponse("INTERNAL_SERVER_ERROR", f"An unexpected error occurred. INFO:{e}", 500, headers=headers)


def ErrorResponse(message:str, description:str, status_code:int, headers:dict=None):
    return JSONResponse(content={ "error": {"message": message,"description": description}}, status_code=status_code, headers=headers)

def UnauthorizedResponse(e:str, headers:dict=None):
    return ErrorResponse("UNAUTHORIZED","Full authentication is required to access this resource. INFO:"+e,status_code=401, headers=headers)


def BadRequestResponse(VIN:str, headers:dict=None):
    return ErrorResponse("BAD_REQUEST", f"invalid VIN value. field:{VIN}", 400, headers=headers)

def NotSupportedResponse(command:str, headers:dict=None):
    return ErrorResponse("NOT_FOUND", f"{command} is not supported by this vehicle", 403, headers=headers)

def NormalResponse(VINL:str, invoiceStatus:str, message:str=None, status_code:int=200, headers:dict=None):
    return JSONResponse(content={ "data": {"vin": VINL ,"invokeStatus": invoiceStatus,"message": message}}, status_code=status_code, headers=headers)



def UnauthorizedResponseInternal():
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)

def BadRequestResponseInternal(VIN:str):
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/BAD_REQUEST","description": f"invalid VIN value. field:{VIN}"}}, status_code=400)

