


from fastapi import HTTPException
from fastapi.responses import JSONResponse




def autoErrorResponse(e:str, VIN:str=None, headers:dict=None):
    if str(e) == "Missing API key":
        return MissingAPIKeyResponse(headers)
    elif str(e) == "Invalid API key":
        return InvalidAPIKeyResponse(headers)
    elif str(e) == "Invalid access token":
        return UnauthorizedResponse(headers)
    elif str(e) == "Invalid VIN":
        return BadRequestResponse(VIN, headers)
    elif str(e) == "Invalid Content-Type":
        return ErrorResponse("BAD_REQUEST", "Invalid Content-Type. Only 'application/json' is accepted.", 415, headers=headers)
    elif str(e) == "Invalid Accept header":
            return ErrorResponse("BAD_REQUEST", "Invalid Accept header. Only 'application/json' is accepted.", 406, headers=headers)
    else:
        return ErrorResponse("INTERNAL_SERVER_ERROR", f"An unexpected error occurred.", 500, headers=headers,additional_info=f"INFO: {str(e)}")


def ErrorResponse(message:str, description:str, status_code:int, headers:dict=None,additional_info:str=None):
    if additional_info is not None:
        raise HTTPException(status_code=status_code, detail={"error": {"message": message, "description": description, "detail": additional_info}}, headers=headers)
    raise HTTPException(status_code=status_code, detail={"error": {"message": message, "description": description}}, headers=headers)

def MissingAPIKeyResponse(headers:dict=None):
    return ErrorResponse("ERROR", "Access denied due to missing header VCC-API-KEY. Make sure to provide a valid key for an active application.", 401, headers=headers)
def InvalidAPIKeyResponse(headers:dict=None):
    return ErrorResponse("ERROR", "Access denied due to invalid header VCC-API-KEY. Make sure to provide a valid key for an active application.", 401, headers=headers)

def UnauthorizedResponse(headers:dict=None):
    return ErrorResponse("UNAUTHORIZED","Full authentication is required to access this resource.",status_code=401, headers=headers)


def BadRequestResponse(VIN:str, headers:dict=None):
    return ErrorResponse("FORBIDDEN", f"No relationship to UUID.", 403, headers=headers, additional_info=f" INFO:{VIN} not found.")
    # return ErrorResponse("BAD_REQUEST", f"invalid VIN value. field:{VIN}", 400, headers=headers)

def NotSupportedResponse(command:str, headers:dict=None):
    return ErrorResponse("NOT_FOUND", f"{command} is not supported by this vehicle", 403, headers=headers)

def NormalResponse(VINL:str, invoiceStatus:str, message:str=None, status_code:int=200, headers:dict=None):
    return JSONResponse(content={ "data": {"vin": VINL ,"invokeStatus": invoiceStatus,"message": message}}, status_code=status_code, headers=headers)



def UnauthorizedResponseInternal():
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/UNAUTHORIZED","description": "invalid API key value."}}, status_code=401)

def BadRequestResponseInternal(VIN:str):
    return JSONResponse(content={ "error": {"message": "THIS IS INTERNAL API/BAD_REQUEST","description": f"invalid VIN value. field:{VIN}"}}, status_code=400)

