from time import time

from classCar import AuthHeaderGET, AuthHeaderPOST
from database import database, AdditionalDatabase



def authenticate(auth_header: AuthHeaderPOST | AuthHeaderGET):
    if auth_header.vcc_api_key not in database:
        if auth_header.vcc_api_key == "":
            raise ValueError("Missing API key")
        raise ValueError("Invalid API key")
    if   AdditionalDatabase[auth_header.vcc_api_key].Oauth2Data is not None:
        if auth_header.authorization != f"Bearer {AdditionalDatabase[auth_header.vcc_api_key].access_token}":
            raise ValueError("Invalid access token")
        if AdditionalDatabase[auth_header.vcc_api_key].Oauth2Data.expires_in != -1 and AdditionalDatabase[auth_header.vcc_api_key].Oauth2Data.expires_in < int(time()):
            raise ValueError("Invalid access token")
    if isinstance(auth_header, AuthHeaderPOST):
        if auth_header.content_type.split(";")[0].lower() != "application/json": #NOTE: lower case to avoid case sensitivity issues checks needed
            raise ValueError("Invalid Content-Type")
    elif isinstance(auth_header, AuthHeaderGET):
        output = auth_header.accept.split(";")[0].lower()
        if output != "application/json" and output != "*/*" and output != "application/*": 
            raise ValueError("Invalid Accept header")
    else:
        raise ValueError("Invalid auth header type")
        
    return True


def VINHandling(VIN:str, auth_header:  AuthHeaderPOST | AuthHeaderGET):
    try:
        authenticate(auth_header)
    except Exception as e:
        raise ValueError(str(e))
    
    for car in database[auth_header.vcc_api_key]:
        if car.VIN == VIN:
            return car
    raise ValueError("Invalid VIN")

def authenticateInternal(vcc_api_key: str):
    if vcc_api_key not in database:
        raise ValueError("Invalid API key")
    
def VINHandlingInternal(VIN:str, vcc_api_key: str):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError:
        raise ValueError("Invalid API key")
    for car in database[vcc_api_key]:
        if car.VIN == VIN:
            return car
    raise ValueError("Invalid VIN")
    