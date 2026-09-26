


import uuid
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
            return ErrorResponse("BAD_REQUEST", "Invalid Accept header.", 406, headers=headers)
    elif str(e).startswith("The API key does not have access to the requested scope"):
        return ErrorResponse("FORBIDDEN", f"{str(e)}", 403, headers=headers)
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

def energyErrorResponseGen(code: str, message: str,headers: dict, status_code: int = 500,details: list=None):
    data={
        "code": code,
        "message": message,
        "details": details
    }

    return JSONResponse(content=data, status_code=status_code, headers=headers) #check what headers are sent
def energyAutoErrorResponse(e: ValueError, VIN: str, headers: dict):
    if str(e) == "Missing API key":
        return energyErrorResponseGen("UNAUTHORIZED", "Access denied due to missing header VCC-API-KEY. Make sure to provide a valid key for an active application.", headers, status_code=401)
    elif str(e) == "Invalid API key":
        return energyErrorResponseGen("UNAUTHORIZED", "Access denied due to invalid header VCC-API-KEY. Make sure to provide a valid key for an active application.", headers, status_code=401)
    elif str(e) == "Invalid access token":
        return energyErrorResponseGen("UNAUTHORIZED", "Full authentication is required to access this resource.", headers, status_code=401)
    elif str(e) == "Invalid VIN":
        return energyErrorResponseGen("VEHICLE_NOT_FOUND", f"Vehicle with VIN {VIN} could not be found", headers, status_code=404)
    elif str(e) == "Invalid Accept header":
        return energyErrorResponseGen("BAD_REQUEST", "Invalid Accept header.", headers, status_code=406)
    elif str(e).startswith("The API key does not have access to the requested scope"):
        return energyErrorResponseGen("FORBIDDEN", str(e), headers, status_code=403)
    else:
        return energyErrorResponseGen("INTERNAL_SERVER_ERROR", "An internal server error occurred.", headers, status_code=500)
    # """{  
    #             "status": 401,
    #             "error": {  
    #             "message": "Access denied due to invalid VCC-API-KEY. Make sure to provide a valid key for an active application."
    #         }
    # }"""

def OLD_errorResponse(e: ValueError, VIN: str, headers: dict):
    detail=None
    
    if str(e) == "Missing API key":
        status_code = 401
        message = "UNAUTHORIZED"
        description = "Access denied due to missing header VCC-API-KEY. Make sure to provide a valid key for an active application."

        
    elif str(e) == "Invalid API key":
        status_code = 401
        message = "UNAUTHORIZED"
        description = "Access denied due to invalid header VCC-API-KEY. Make sure to provide a valid key for an active application."
   
        
    elif str(e) == "Invalid access token":
        status_code = 401
        message = "UNAUTHORIZED"
        description = "Full authentication is required to access this resource."
        detail= "INFO: The access token is not valid"
    elif str(e) == "Invalid VIN":
        status_code = 404
        message = "FORBIDDEN"
        description = f"No relationship to UUID."
        detail= "INFO:{VIN} not found"
        
    elif str(e) == "Invalid Content-Type":
        status_code = 415
        message = "BAD_REQUEST"
        description = "Invalid Content-Type. Only 'application/json' is accepted."

    elif str(e) == "Invalid Accept header":
        status_code = 406
        message = "BAD_REQUEST"
        description = "Invalid Accept header."
    elif str(e).startswith("The API key does not have access to the requested scope"):
        status_code = 403
        message = "FORBIDDEN"
        description = str(e)
    else:
        status_code = 500
        message = "INTERNAL_SERVER_ERROR"
        description = "An internal server error occurred."
        detail= str(e)
    if detail is None:
         data = {
                "status": status_code,
                "operationId": str(uuid.uuid4()),
                "error": {
                    "message": message,
                    "description": description,
                }
            }
    else:
        data = {
            "status": status_code,
            "operationId": str(uuid.uuid4()),
            "error": {
                "message": message,
                "description": description,
                "detail": detail
            }
        }

    return JSONResponse(content=data, status_code=status_code, headers=headers) # TODO: check what headers are sent
