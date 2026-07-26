from fastapi import Body ,Request , Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse ,HTMLResponse 
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

import json
import secrets



from notifier import notifier
from classCar import Car, options, AuthHeader, startUp, timestampGenerator, Oauth2
from database import database, Oauth2Data
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal
from internal import VINHandlingInternal, authenticateInternal, update, genAPIKey


#site section

def DashboardCSS():
    return FileResponse("templates/dashboardWS.css")



def DashboardCar(key: str,VIN: str, request: Request):
    try:
        car = VINHandlingInternal(VIN, key)
        data={"VIN":VIN,"key":key}
        return templates.TemplateResponse(name="dashboard.html", request=request, context=data)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    

def DashboardRedirect(key: str,VIN: str, request: Request):
    try:
        response = Response()
        response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
        return response
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    

async def DashboardWS(websocket: WebSocket):
    await websocket.accept()
    params = websocket.query_params
    vin = params.get("VIN")
    api_key = params.get("key")
    queue = notifier.subscribe(vin)
    print(f"Connected car: {vin} with key: {api_key}")
    try:
        car = VINHandlingInternal(vin, api_key)
        if not car:
            raise ValueError("Car not found or invalid API key")
        car_data = car.model_dump()
        
        car_data["key"] = api_key
        template = templates.get_template("dashboardSetup.html")
        html=template.render(car_data)
        await websocket.send_text(html)
        
        while True:
            packet = await queue.get()
    
            packet["key"] = api_key
            #NOTE: OLD CODE
            #data={"data": packet["attribute_name"],"value": packet["current_value"],"options":options[packet["attribute_name"]],"VIN": packet["VIN"],"key": api_key}
            #template = templates.get_template("dashboardTemplate.html")
            #html = template.render(data)
            if packet["attribute_name"] == "fuelType":
                template = templates.get_template("TempDash/fuelsection.html")
                html=template.render({"VIN": packet["VIN"],"key": api_key,"fuelType":packet["current_value"],"fuelICE":car.fuelICE,"fuelElectric": car.fuelElectric})
            # elif packet["attribute_name"] == "availabilityStatus_unavailableReason":
            #     html=""
            else:
                html=f"<p class=\"text-base md:text-lg mt-2 mb-4\" id=\"{packet['attribute_name']}\">{packet['current_value']}</p>"
            
            await websocket.send_text(html)
            
    except WebSocketDisconnect:
        print("Dashboard disconnected")
    except ValueError as e:
        await websocket.send_text("Invalid API key or VIN")
        await websocket.close()
        return
    finally:
        notifier.unsubscribe(vin, queue)
        print(f"Disconnected car: {vin} with key: {api_key}")
    

def DashboardUpdate(key: str,VIN: str, request: Request, attribute: str = Body(...), value: str = Body(...)):
    try:
        if value == "True":
            value = True
        elif value == "False":
            value = False
            
        response = update( VIN, attribute, value, key)
        if response:
            return JSONResponse(content={"message": f"THIS IS INTERNAL API/attribute {attribute} updated successfully"}, status_code=200)
        else:
            return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute}"}}, status_code=400)
    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponseInternal()
        elif str(e) == "Invalid VIN":
            return BadRequestResponseInternal(VIN)
        else:
            return JSONResponse(
            content={"error": {"message": "VALUE_ERROR", "description": str(e)}}, 
            status_code=400
            )
    
    

def DashboardCarCSS():
    return FileResponse("templates/dashboardCarSel.css")


def Dashboard(key: str, request: Request):
    try:
        authenticateInternal(key)
        cars = database[key]
        VINs = []
        for car in cars:
            VINs.append(car.VIN)
        if key not in Oauth2Data:
            oauth2_status = "Not activated"
            
        else:
            oauth2_status = "Activated"
            if Oauth2Data[key].PKCE:
                pkce_status = "Activated"
            else:
                pkce_status = "Not activated"
            return templates.TemplateResponse(name="dashboardCarSel.html", request=request, context={"VINs": VINs,"key": key, "oauth2_status": oauth2_status, "pkce_status": pkce_status, "oauth2_secret": Oauth2Data[key].client_secret, "oauth2_code": Oauth2Data[key].code, "oauth2_access_token": Oauth2Data[key].access_token, "oauth2_refresh_token": Oauth2Data[key].refresh_token, "oauth2_redirect_uri": Oauth2Data[key].redirect_uri})

        return templates.TemplateResponse(name="dashboardCarSel.html", request=request, context={"VINs": VINs,"key": key, "oauth2_status": oauth2_status,})
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>") 

def OAuth2Settings(key: str, request: Request):
    try:
        authenticateInternal(key)
        if key not in Oauth2Data:
            oauth2_status = "Not activated"
            return templates.TemplateResponse(name="oauth2settings.html", request=request, context={"key": key, "oauth2_status": oauth2_status})
        else:
            oauth2_status = "Activated"
        data=Oauth2Data[key].model_dump()
        data["oauth2_status"] = oauth2_status
        data["key"]=key
        return templates.TemplateResponse(name="oauth2settings.html", request=request, context=data)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    
def OAuth2SettingsCSS():
    return FileResponse("templates/OAuth2settings.css")

def OAuth2Change(key: str, attribute: str, value: str, request: Request):
    try:
        authenticateInternal(key)

        if key not in Oauth2Data:

            if attribute == "OAuth2":
                if value.lower() == "true":
                    oauth2 = Oauth2(client_secret="client_secret_"+secrets.token_urlsafe(12), PKCE=False,redirect_uri="")
                    Oauth2Data[key] = oauth2
                    response=Response()
                    response.headers["HX-Redirect"] = f"/internal/dashboard/OAuth2settings?key={key}"
                    return response
                

            return HTMLResponse(content="<p style=\"color:red\">OAuth2 not activated for this API key</p>")
        print(f"Changing OAuth2 attribute {attribute} to {value} for key {key}")
        if attribute == "client_secret":
            Oauth2Data[key].client_secret = value
        elif attribute == "redirect_uri":   
            Oauth2Data[key].redirect_uri = value
        elif attribute == "PKCE":
            if value.lower() == "true":
                Oauth2Data[key].PKCE = True
            elif value.lower() == "false":
                Oauth2Data[key].PKCE = False
        elif attribute == "access_token":
            Oauth2Data[key].access_token = value
        elif attribute == "refresh_token":
            Oauth2Data[key].refresh_token = value
        elif attribute == "OAuth2":
            if value.lower() == "false":
                del Oauth2Data[key]
        else:
            return HTMLResponse(content="<p style=\"color:red\">Invalid attribute</p>")
        response=Response()
        response.headers["HX-Redirect"] = f"/internal/dashboard/OAuth2settings?key={key}"
        return response
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")

def WelcomeCSS():
    return FileResponse("templates/welcome.css")

def Welcome():
    return FileResponse("templates/welcome.html")


def WelcomeCheck(vcc_api_key: str):
    try:
        authenticateInternal(vcc_api_key)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    
    response = Response()
    response.headers["HX-Redirect"] = f"/internal/dashboard?key={vcc_api_key}"
    return response


def WelcomeAPIKey(request: Request):
    data=genAPIKey().body.decode("utf-8")
    data = json.loads(data)
    data = data["message"]
    return templates.TemplateResponse(request=request,name="welcomeAPI.html",context={"api_key": data})


def WelcomeNewCar(key: str, VIN: str,scenario: str):
    try:
        if key not in database:
            raise ValueError("Invalid API key")
        try:
           car = VINHandlingInternal(VIN, key)
           return HTMLResponse(content="<p style=\"color:red\">Car already exists</p>")
        except ValueError:
            new_car = Car(VIN=VIN)
            database[key].append(new_car)
            response = Response()
            response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
            return response
       
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Car already exists/internal error {e}</p>")
