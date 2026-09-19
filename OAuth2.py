
import base64
import hashlib
import json
from time import time
import uuid
import secrets
from fastapi import Request, Form, Query, Header, Response, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates



from database import AdditionalDatabase
from classCar import Oauth2, readConfig



templates = Jinja2Templates(directory="templates")

def PKCE(code_challenge:str, code_challenge_method:str, oauth2: Oauth2):
    if code_challenge_method == "S256":
        oauth2.code_challenge = code_challenge
        oauth2.code_challenge_method = code_challenge_method
        return True
    elif code_challenge_method == "plain":
        oauth2.code_challenge = code_challenge
        oauth2.code_challenge_method = code_challenge_method
        return True
    return False

def PKCECheck(code_verifier: str, oauth2: Oauth2):
    method = oauth2.code_challenge_method
    code_challenge = oauth2.code_challenge

    if method == "S256":
        expected = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).rstrip(b"=").decode() #NOTE: when aproved need to check this 
        ok = expected == code_challenge
    elif method == "plain":
        ok = code_verifier == code_challenge
    else:
        ok = False

    if ok:
        oauth2.code_challenge_method = ""
        oauth2.code_challenge = ""

    return ok


def tokenGenerator(api_key:str,timeGen:int,scopes:list=None):
    header={"alg": "HS256", "kid": api_key}# api key is used here bc i dont use this data

    if scopes is None:
        scopes=scopesList
    payload={"scope":scopes,"authorization_details": [],"client_id": api_key,"sub":"user", "iss": "https://playground.kls.hackclub.app","aud": "https://playground.kls.hackclub.app","exp": int(timeGen + 3599),"iat": int(timeGen)}
    # TODO
    # if multi user change sub
    # while doing that rewrtie Oauth2 logic (kid)
    #
    if readConfig("DEFAULT","ShortKeys",True)==True:
        signature = secrets.token_urlsafe(2).rstrip("=") 
    signature = secrets.token_urlsafe(16).rstrip("=") # testing secret is used here bc i dont use this data
    return f"{base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')}.{base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')}.{signature}"


def oauth2Generator(api_key:str,oauth2:Oauth2):
    additonal=AdditionalDatabase[api_key]
    scopes=None
    if additonal.ScopesData is not None:
        scopes=list(additonal.ScopesData.scopes)
    
    timeGeneration=time()
    if readConfig("DEFAULT","ShortKeys",True)==True:
        oauth2.access_token = "access_token_"+tokenGenerator(api_key, timeGeneration, scopes=scopes) #generate
        oauth2.refresh_token = "refresh_token_"+base64.urlsafe_b64encode(uuid.uuid4().bytes).decode() #generate
        
    oauth2.access_token = tokenGenerator(api_key, timeGeneration, scopes=scopes) #generate
    oauth2.refresh_token = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode().rstrip('=') #generate
    oauth2.code = "" #invalidate code
    if oauth2.expires_in != -1:
        oauth2.expires_in = int(time()) + 3599 

    return oauth2


#client id == api key for this playground
#scopes are not checked and dont work HERE TODO
def oauth2(request: Request, response_type:str=Query(...),client_id:str=Query(...),redirect_uri:str=Query(...),scope:str=Query(default=""),state:str=Query(default=""),code_challenge:str=Query(default=""),code_challenge_method:str=Query(default="")):
    if response_type != "code":
        return HTMLResponse(content="<h1>BAD_REQUEST</h1><p>response_type must be 'code'</p>", status_code=400)
    if client_id not in AdditionalDatabase:
        return HTMLResponse(content="<h1>BAD_REQUEST</h1><p>Invalid client_id</p>", status_code=400)
    oauth2 = AdditionalDatabase[client_id].Oauth2Data
    if oauth2.redirect_uri != "":
        if redirect_uri != AdditionalDatabase[client_id].Oauth2Data.redirect_uri:
            return HTMLResponse(content="<h1>BAD_REQUEST</h1><p>Invalid redirect_uri</p>", status_code=400)
    # site needed for "login"
    return templates.TemplateResponse(name="oauth2login.html", request=request, context={"client_id": client_id, "redirect_uri": redirect_uri, "scope": scope, "state": state, "code_challenge": code_challenge, "code_challenge_method": code_challenge_method})
    
 


def oauth2_post(client_id: str = Form(...), redirect_uri: str = Form(...), state: str = Form(default=""), login: str = Form(...), code_challenge: str = Form(default=""), code_challenge_method: str = Form(default="")):
    if client_id != login:
        return HTMLResponse(content="<p style='color: red;'>Wrong client_id or login</p>", status_code=200)
    oauth2 = AdditionalDatabase[client_id].Oauth2Data

    if oauth2.PKCE == True :
        if PKCE(code_challenge, code_challenge_method, oauth2) == False:
            return HTMLResponse(content="<p style='color: red;'>ERROR with PKCE code_challenge_method</p>", status_code=200)
    oauth2.code = "code_"+secrets.token_urlsafe(32) #generate 
    url=f"{redirect_uri}?code={oauth2.code}"
    if state != "":
        url += f"&state={state}"
    response = Response()
    response.headers["HX-Redirect"] = url
    return response


def test(code:str=Query(...),state:str=Query(default="")):
    # testing first step of oauth2
    return HTMLResponse(content=f"<h1>Code: {code}</h1><p>State: {state}</p>", status_code=200)


#scopes are not checked and dont work
def OAuthToken(content_type:str=Header(...,alias="content-type"),authorization:str=Header(...),grant_type:str=Form(...),refresh_token:str=Form(default=""),code:str=Form(default=""),redirect_uri:str=Form(default=""),code_verifier:str=Form(default=""),):
    if content_type != "application/x-www-form-urlencoded":
        raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "content-type must be 'application/x-www-form-urlencoded'"}})
    
    try:
        auth_parts = authorization.split(" ")
        if len(auth_parts) != 2 or auth_parts[0].lower() != "basic":
            raise ValueError()
        
        decoded_bytes = base64.b64decode(auth_parts[1])
        decoded_str = decoded_bytes.decode("utf-8")
        client_id, client_secret = decoded_str.split(":", 1)
    except Exception:
        raise HTTPException(status_code=401, detail={"error": "invalid_client", "error_description": "Malformed Authorization header"})
    
    if client_id not in AdditionalDatabase or AdditionalDatabase[client_id].Oauth2Data is None:
            raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "Invalid client_id"}})
    oauth2 = AdditionalDatabase[client_id].Oauth2Data
    if oauth2.client_secret != client_secret:
        raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "Invalid client_secret"}})
    
    if grant_type == "authorization_code":
        if oauth2.PKCE == True:
            if PKCECheck(code_verifier,oauth2) == False:
                raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "Invalid code_verifier"}})

        if oauth2.code != code or oauth2.code == "": # forgot to check if there is any code available FIXED
            raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "No code available. Please request a new code"}})
        else:
            if oauth2.redirect_uri != "":
                if redirect_uri != oauth2.redirect_uri:
                 raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "Invalid redirect_uri"}})
    elif grant_type == "refresh_token":
        if oauth2.refresh_token != refresh_token:
            raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "Invalid refresh_token"}})
    else:
        raise HTTPException(status_code=400, detail={"error": {"message": "BAD_REQUEST","description": "grant_type must be 'authorization_code' or 'refresh_token'"}})
    
    oauth2Generator(client_id,oauth2)

    data={"access_token": oauth2.access_token, "refresh_token": oauth2.refresh_token, "token_type": "Bearer", "expires_in": 3599}
    return JSONResponse(content=data, status_code=200)