from datetime import datetime
import json

from fastapi import FastAPI, Request,HTTPException
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask
import asyncio

from classCar import config
# error logging V1





class req_eror:
    method: str
    headers: dict 
    client: str 
    query_params: dict 
    body: str 
    json: bool = False
    urlEncoded: bool= False
    
    
    

def write_log(req: req_eror, exc: Exception):
    # file logging
    with open("error_log.txt", "a") as f:
        f.write(f"Error occurred during request: \n")
        f.write(f"Timestamp: {datetime.now()}\n")
        f.write(f"Method: {req.method}\n")
        f.write(f"Headers: {req.headers}\n")
        f.write(f"Client: {req.client}\n")
        f.write(f"Query Params: {req.query_params}\n")
        f.write(f"Body: {req.body}\n")
        f.write(f"JSON: {req.json}\n")
        f.write(f"URL Encoded: {req.urlEncoded}\n")
        f.write(f"Exception: {exc}\n")
        f.write(f"\n")
        f.write(f"--------------------------------------------------\n")

async def log_error(req: req_eror, exc: Exception):
    RED= "\033[31m"
    RESET= "\033[0m"
    # here will be the logic for logging an error
    
    # terminal logging
    print(f"{RED}Logging error for request{RESET}")
    print(f"{RED}Exception:{RESET} {exc}")
    print(f"{RED}Method:{RESET} {req.method}")
    print(f"{RED}Headers:{RESET} {req.headers}")
    print(f"{RED}Query Params:{RESET} {req.query_params}")
    print(f"{RED}Body:{RESET} {req.body}")
    if config["ERROR_LOGGING"]["Write"] == "True":
        await asyncio.to_thread(write_log, req, exc)  # Write to file in a separate thread

        
# doesnt kog error forced by the vehicle avaibility check, because it is not a real error, but a normal response from the vehicle.
def setup_error_logging(app: FastAPI):
    @app.exception_handler(RequestValidationError)
    async def error_handler(request: Request, exc: RequestValidationError):
        if config["ERROR_LOGGING"]["STATUS"] == "False":
            return await request_validation_exception_handler(request, exc) 
        if request.url.path.startswith("/internal"):
            return await request_validation_exception_handler(request, exc)
        req = req_eror()
        req.method = request.method
        req.headers = dict(request.headers)
        req.client = str(request.client)
        req.query_params = dict(request.query_params)
        try:
            content_type = request.headers.get("content-type", "").lower()

            if "application/x-www-form-urlencoded" in content_type:
                req.urlEncoded = True

                form_data = await request.form()
                req.body = dict(form_data)

            elif "application/json" in content_type:
                body_bytes = await request.body()
                try:
                    req.json = True
                    req.body = json.loads(body_bytes.decode("utf-8", errors="ignore"))
                except Exception:
                    req.body = body_bytes.decode("utf-8", errors="ignore")

            else:
                body_bytes = await request.body()
                req.body = body_bytes.decode("utf-8", errors="ignore")

        except Exception:
            req.body = "Error reading body"

        
        



        response = await request_validation_exception_handler(request, exc)
        
        response.background = BackgroundTask(log_error, req, exc)
        
        return response
    
    
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        if config["ERROR_LOGGING"]["STATUS"] == "False":
            return await request_validation_exception_handler(request, exc) 
        if request.url.path.startswith("/internal"):
            return await request_validation_exception_handler(request, exc)
        
        req = req_eror()
        req.method = request.method
        req.headers = dict(request.headers)
        req.client = str(request.client)
        req.query_params = dict(request.query_params)
        try:
            content_type = request.headers.get("content-type", "").lower()
            if "application/x-www-form-urlencoded" in content_type:
                req.urlEncoded = True
                
                form_data = await request.form()
                req.body = dict(form_data)

            elif "application/json" in content_type:
                body_bytes = await request.body()
                try:
                    req.json = True
                    req.body = json.loads(body_bytes.decode("utf-8", errors="ignore"))
                except Exception:
                    req.body = body_bytes.decode("utf-8", errors="ignore")

            else:
                body_bytes = await request.body()
                req.body = body_bytes.decode("utf-8", errors="ignore")

        except Exception:
            req.body = "Error reading body"


        response = JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)
        
        response.background = BackgroundTask(log_error, req, exc)
        
        return response
    