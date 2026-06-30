from fastapi import Body, FastAPI, Header ,Request ,Query, Response, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import JSONResponse, FileResponse ,HTMLResponse 
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

import json
import secrets



from notifier import notifier
from classCar import Car, options, AuthHeader, startUp, timestampGenerator
from database import database
from readyResponses import BadRequestResponseInternal, UnauthorizedResponseInternal

#internal endpoints 

#TODO: add authentication func for internal endpoints API key and VIN without in future bearer token

def Internal():
    return JSONResponse(content={"message": "Welcome to the internal API", "description": startUp}, status_code=200) # here will be displayed any options like authetication using tokens and so on.


def Terminal(VIN: str, key: str, request: Request):
    return templates.TemplateResponse(name="terminal.html", request=request, context={"vin": VIN, "key": key})
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
        template = templates.get_template("dashboardUpdate.html")
        html=template.render(car_data)
        await websocket.send_text(html)
        
        while True:
            packet = await queue.get()
    
            packet["key"] = api_key
            
            data={"data": packet["attribute_name"],"value": packet["current_value"],"options":options[packet["attribute_name"]],"VIN": packet["VIN"],"key": api_key}
            template = templates.get_template("dashboardTemplate.html")
            html = template.render(data)
            
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
        response=update(VIN, attribute, value, key)
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
        return templates.TemplateResponse(name="dashboardCarSel.html", request=request, context={"VINs": VINs,"key": key})
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


def WelcomeNewCar(key: str, VIN: str):
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

#internal endpoints for testing and dashboard purposes. Not part of the official API.


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
    
def update(VIN:str, attribute: str, value: str, vcc_api_key: str):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        if startUp["statusNofication"] == "SET" or startUp["statusNofication"] == "ALL":
            notifier.trigger_update(VIN, car, attribute)
        return car.update(attribute, value)
    except ValueError as e:
        raise ValueError(str(e))



def getStatus(VIN: str = Header(...),vcc_api_key: str = Header(...)):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        data = car.model_dump()
        return JSONResponse(content=data, status_code=200)

    except ValueError as e:
        if str(e) == "Invalid API key":
            return UnauthorizedResponseInternal()
        elif str(e) == "Invalid VIN":
            return BadRequestResponseInternal(VIN)
        

async def statusWS(websocket: WebSocket):
    if startUp["Websocket"] == False:
        return
    
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
        await websocket.send_text(json.dumps(car_data))
        
        while True:
            packet = await queue.get()
    
            packet["key"] = api_key
            
            
            await websocket.send_text(json.dumps(packet))
            
    except WebSocketDisconnect:
        print("Dashboard disconnected")
    except ValueError as e:
        await websocket.send_text("Invalid API key or VIN")
        await websocket.close()
        return
    finally:
        notifier.unsubscribe(vin, queue)
        print(f"Disconnected car: {vin} with key: {api_key}")


def internal_update(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: str = Body(...), value: str = Body(...)):
    try:
        response=update(VIN, attribute, value, vcc_api_key)
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


# to redo
def internal_updates(VIN: str = Header(...),vcc_api_key: str = Header(...),attribute: list = Body(...), value: list = Body(...)):
    try:
        car = VINHandlingInternal(VIN, vcc_api_key)
        for i in range(len(attribute)):
            if hasattr(car, attribute[i]):
                setattr(car, attribute[i], value[i])
            else:
                return JSONResponse(content={"error": {"message": "BAD_REQUEST","description": f"THIS IS INTERNAL API/invalid attribute value. field:{attribute[i]}"}}, status_code=400)
        return JSONResponse(content={"message": f"THIS IS INTERNAL API/attributes updated successfully"}, status_code=200)

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



def genAPIKey():                    
    api_key=secrets.token_hex(16)
    database[api_key] = []
    return JSONResponse(content={"message": api_key,"description": f"THIS IS INTERNAL API/API key generated successfully"}, status_code=200)


def addCar(vcc_api_key: str = Header(...), VIN: str = Body(...), attributes: list = Body(...), values: list = Body(...)):
    try:
        cars =database[vcc_api_key]
        if any(car.VIN == VIN for car in cars):
            return BadRequestResponseInternal(VIN)
        
        new_car = Car(VIN=VIN)
        for attribute in attributes:
            if hasattr(new_car, attribute):
                setattr(new_car, attribute, values[attributes.index(attribute)])
            else:
                return BadRequestResponseInternal(VIN)
        cars.append(new_car)
        return JSONResponse(content={"message": f"THIS IS INTERNAL API/Car added successfully: {VIN}"}, status_code=200)

    except KeyError:
        return UnauthorizedResponseInternal()
