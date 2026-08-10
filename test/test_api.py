import database
import main
from fastapi.testclient import TestClient


def change_data(attribute,value):
    database.database["TEST_NO_OAUTH"][0].__setattr__(attribute,value)
    

client = TestClient(main.app)

def test_list_cars():
    headers = {"vcc-api-key": "TEST_NO_OAUTH"}
    vehicles = client.get("/vehicles", headers=headers)
    assert vehicles.status_code == 200
    assert vehicles.json()["data"][0]["vin"] == "12345678901234567"
    assert vehicles.json()["data"][1]["vin"] == "09876543210987654"
    
def test_list_car_info():
    headers = {"vcc-api-key": "TEST_NO_OAUTH"}
    vehicle_info = client.get("/vehicles/12345678901234567", headers=headers)
    assert vehicle_info.status_code == 200
    assert vehicle_info.json()["data"]["vin"] == "12345678901234567"
    assert vehicle_info.json()["data"]["modelYear"] == 2019
    assert vehicle_info.json()["data"]["fuelType"] == "HYBRID"
    
    
    #only testing dynamic data
    
def test_engine_data():
    headers = {"vcc-api-key": "TEST_NO_OAUTH"}
    engine_data = client.get("/vehicles/12345678901234567/engine-status", headers=headers)
    assert engine_data.status_code == 200
    assert engine_data.json()["data"]["engineStatus"]["value"] == "STOPPED"
    
    
    change_data("engineStatus","RUNNING")
    
    engine_data = client.get("/vehicles/12345678901234567/engine-status", headers=headers)
    assert engine_data.status_code == 200
    assert engine_data.json()["data"]["engineStatus"]["value"] == "RUNNING"


def test_engine_start():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    body =  {"runtimeMinutes": 10}
    
    engine_start = client.post("/vehicles/12345678901234567/commands/engine-start", headers=headers, json=body)

    assert engine_start.status_code == 200
    assert engine_start.json()["data"]["invokeStatus"] == "COMPLETED"


    #check this test
    change_data("engineStatus","RUNNING")
    
    engine_start = client.post("/vehicles/12345678901234567/commands/engine-start", headers=headers, json=body)
    assert engine_start.status_code == 200
    assert engine_start.json()["data"]["invokeStatus"] == "RUNNING"
    
def test_engine_stop():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    #check this test
    engine_stop = client.post("/vehicles/12345678901234567/commands/engine-stop", headers=headers)
    print(engine_stop.json())
    assert engine_stop.status_code == 200
    assert engine_stop.json()["data"]["invokeStatus"] == "COMPLETED"

    change_data("engineStatus","RUNNING")
    
    engine_stop = client.post("/vehicles/12345678901234567/commands/engine-stop", headers=headers)
    assert engine_stop.status_code == 200
    assert engine_stop.json()["data"]["invokeStatus"] == "COMPLETED"

def test_climate_start():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    climate_start = client.post("/vehicles/12345678901234567/commands/climatization-start", headers=headers)

    assert climate_start.status_code == 200
    assert climate_start.json()["data"]["invokeStatus"] == "COMPLETED"
    
    
    change_data("climate",True)
    
    engine_stop = client.post("/vehicles/12345678901234567/commands/climatization-start", headers=headers)
    assert engine_stop.status_code == 200
    assert engine_stop.json()["data"]["invokeStatus"] == "RUNNING"


def test_climate_stop():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    climate_stop = client.post("/vehicles/12345678901234567/commands/climatization-stop", headers=headers)

    assert climate_stop.status_code == 200
    assert climate_stop.json()["data"]["invokeStatus"] == "COMPLETED"
    
    
    change_data("climate",True)
    
    engine_stop = client.post("/vehicles/12345678901234567/commands/climatization-stop", headers=headers)
    assert engine_stop.status_code == 200
    assert engine_stop.json()["data"]["invokeStatus"] == "COMPLETED"
    
def test_windows():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    lock = client.get("/vehicles/12345678901234567/windows", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["frontLeftWindow"]["value"] == "CLOSED"
    
    change_data("frontLeftWindow","OPEN")
    
    lock = client.get("/vehicles/12345678901234567/windows", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["frontLeftWindow"]["value"] == "OPEN"
    