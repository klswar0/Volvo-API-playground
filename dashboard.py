

from fastapi import Body, Query ,Request , Response, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse ,HTMLResponse 
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")

import json
import secrets



from notifier import notifier
from classCar import Car, options, config, timestampGenerator, Oauth2
from database import createCar, database, AdditionalDatabase
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal
from internal import VINHandlingInternal, authenticateInternal, update, genAPIKey
from scenarios import SCENARIO_TEMPLATES,SCENARIO_USER,scenariosFunc
from snapshots import loadSnapshots, saveSnapshots,snapshotsData

error_headers = {
    "HX-Retarget": "#error-response",
    "HX-Reswap": "innerHTML"
    }



#site section

def style():
    return FileResponse("templates/style.css")





def DashboardCar(key: str,VIN: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        car = VINHandlingInternal(VIN, key)
        data={"VIN":VIN,"key":key,"note": config["SITE"]["Note"]}
        return templates.TemplateResponse(name="dashboard.html", request=request, context=data)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    

def DashboardRedirect(key: str,VIN: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        response = Response()
        response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
        return response
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    

async def DashboardWS(websocket: WebSocket):
    await websocket.accept()
    if config["DEFAULT"]["Websocket"] == "False":
            await websocket.send_text("<div id=\"car-info\"><p style=\"color:red\">Websocket is disabled in the configuration</p></div>")
            await websocket.close()
            return
    params = websocket.query_params
    vin = params.get("VIN")
    api_key = params.get("key")
    queue = notifier.subscribe(vin)
    
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
            if packet["current_value"] == "":
                packet["current_value"] = "NOT SET"
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
                html=f"<p class=\"text-base md:text-lg animate-fade-in\" id=\"{packet['attribute_name']}\">{packet['current_value']}</p>"
            
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
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
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
    
    




def Dashboard(key: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        cars = database[key]
        VINs = []
        for car in cars:
            VINs.append(car.VIN)
        return templates.TemplateResponse(name="dashboardCarSel.html", request=request, context={"VINs": VINs,"key": key,"note": config["SITE"]["Note"]})
    # why there where here Oauth2 status check?
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>") 

def OAuth2Settings(key: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        if key not in AdditionalDatabase or AdditionalDatabase[key].Oauth2Data is None:
            oauth2_status = "Not activated"
            return templates.TemplateResponse(name="oauth2settings.html", request=request, context={"key": key, "oauth2_status": oauth2_status, "note": config["SITE"]["Note"]})
        else:
            oauth2_status = "Activated"
        data=AdditionalDatabase[key].Oauth2Data.model_dump()
        data["oauth2_status"] = oauth2_status
        data["key"]=key
        data["note"] = config["SITE"]["Note"]
        return templates.TemplateResponse(name="oauth2settings.html", request=request, context=data)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    


def OAuth2Change(key: str, attribute: str, value: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)

        if key not in AdditionalDatabase or AdditionalDatabase[key].Oauth2Data is None:

            if attribute == "OAuth2":
                if value.lower() == "true":
                    oauth2 = Oauth2(client_secret="client_secret_"+secrets.token_urlsafe(12), PKCE=False,redirect_uri="")
                    AdditionalDatabase[key].Oauth2Data = oauth2
                    # response=Response()
                    # response.headers["HX-Redirect"] = f"/internal/dashboard/OAuth2settings?key={key}"
                    # return response
                    return OAuth2Settings(key, request)

            return HTMLResponse(content="<p style=\"color:red\">OAuth2 not activated for this API key</p>")
        print(f"Changing OAuth2 attribute {attribute} to {value} for key {key}")
        if attribute == "client_secret":
            AdditionalDatabase[key].Oauth2Data.client_secret = value
        elif attribute == "redirect_uri":   
            AdditionalDatabase[key].Oauth2Data.redirect_uri = value
        elif attribute == "PKCE":
            if value.lower() == "true":
                AdditionalDatabase[key].Oauth2Data.PKCE = True
            elif value.lower() == "false":
                AdditionalDatabase[key].Oauth2Data.PKCE = False
        elif attribute == "access_token":
            AdditionalDatabase[key].Oauth2Data.access_token = value
        elif attribute == "refresh_token":
            AdditionalDatabase[key].Oauth2Data.refresh_token = value
        elif attribute == "OAuth2":
            if value.lower() == "false":
                AdditionalDatabase[key].Oauth2Data = None
        else:
            return HTMLResponse(content="<p style=\"color:red\">Invalid attribute</p>")
        # response=Response()
        # response.headers["HX-Redirect"] = f"/internal/dashboard/OAuth2settings?key={key}"
        # return response
        return OAuth2Settings(key, request)
    except ValueError as e:
        return HTMLResponse(content="<p style=\"color:red\">Invalid API key</p>")
    
    
    
def scenarios(key: str,VIN: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        car = VINHandlingInternal(VIN, key)
        scenarios = list(set(list(SCENARIO_TEMPLATES.keys()) + list(SCENARIO_USER.keys())))
        data={"vin":VIN,"key":key,"scenarios":scenarios,"note": config["SITE"]["Note"]}
        return templates.TemplateResponse(name="loading.html", request=request, context=data)
    except ValueError as e:
        return HTMLResponse(content=f"<p style=\"color:red\">internal error occurred. details: {e}</p>",headers=error_headers)

def scenarioLoad(key: str,VIN: str,name: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        car = VINHandlingInternal(VIN, key)
        response = scenariosFunc(vcc_api_key=key, VIN=VIN, scenario=name)
        if response.status_code == 200:
            response = Response()
            response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
            return response
        else:
            return HTMLResponse(content="<p style=\"color:red\">Error occurred while loading scenario. Is the json file corrupted?</p>",headers=error_headers)
    except ValueError as e:
        return HTMLResponse(content=f"<p style=\"color:red\">internal error occurred. Details: {e}</p>",headers=error_headers)

def snapshotsSave(key: str,name: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        response = saveSnapshots(vcc_api_key=key, name=name)
        if response[0] == True:
            return templates.TemplateResponse(name="snapshots.html", request=request, context={"key": key,"snapshots": list(snapshotsData.keys()),"response": f"Snapshot '{response[1]}' saved successfully.","note": config["SITE"]["Note"]})
        else:
            return HTMLResponse(content=f"<p style=\"color:red\">Error occurred while saving snapshot. Internal error.</p>",headers=error_headers)
    except ValueError as e:
        return HTMLResponse(content=f"<p style=\"color:red\">internal error occurred. Details: {e}</p>",headers=error_headers)


def snapshotsLoad(key: str,name: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        response = loadSnapshots(vcc_api_key=key, name=name)
        if response[0] == True:
            response = Response()
            response.headers["HX-Redirect"] = f"/internal/dashboard?key={key}"
            return response
        else:
            return HTMLResponse(content=f"<p style=\"color:red\">Error occurred while loading snapshot. The snapshot name {response[1]} may be invalid.</p>",headers=error_headers)
    except ValueError as e:
        return HTMLResponse(content=f"<p style=\"color:red\">internal error occurred. Details: {e}</p>",headers=error_headers)

def snapshots(key: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        authenticateInternal(key)
        return templates.TemplateResponse(name="snapshots.html", request=request, context={"key": key,"snapshots": list(snapshotsData.keys()),"note": config["SITE"]["Note"]})
    except ValueError as e:
        return HTMLResponse(content=f"<p style=\"color:red\">internal error occurred. Details: {e}</p>",headers=error_headers)

def Welcome(request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    return templates.TemplateResponse(name="welcome.html", request=request, context={"note": config["SITE"]["Note"]})


def WelcomeCheck(vcc_api_key: str):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
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


def WelcomeNewCar(request: Request, key: str, VIN: str):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        if key not in database:
            raise ValueError("Invalid API key")
        try:
           car = VINHandlingInternal(VIN, key)
           
           return HTMLResponse(content="<div id=\"Error-response\"><p style=\"color:red\">Car already exists</p></div>", headers=error_headers)
        except ValueError:
            new_car = Car(VIN=VIN)
            createCar(key, new_car)
            # response = Response()
            # response.headers["HX-Redirect"] = f"/internal/dashboard/car?key={key}&VIN={VIN}"
            
            # return response
            return Dashboard(key, request)
       
    except ValueError as e:

        return HTMLResponse(content=f"<div id=\"Error-response\"><p style=\"color:red\">Car already exists/internal error {e}</p></div>", headers=error_headers)
    
    
def deleteCar(key: str, VIN: str, request: Request):
    if config["SITE"]["Dashboard"] == "False":
            return HTMLResponse(content="<p style=\"color:red\">Dashboard is disabled in the configuration</p>")
    try:
        if key not in database:
            raise ValueError("Invalid API key")
        try:
            car = VINHandlingInternal(VIN, key)
            database[key].remove(car)

            return Dashboard(key, request)
        except ValueError:
            return HTMLResponse(content="<div id=\"Error-response\"><p style=\"color:red\">Car does not exist</p></div>", headers=error_headers)
    except ValueError as e:
        return HTMLResponse(content=f"<div id=\"Error-response\"><p style=\"color:red\">internal error {e}</p></div>", headers=error_headers)
