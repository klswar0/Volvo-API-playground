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

def test_doors_and_lock():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    lock = client.get("/vehicles/12345678901234567/doors", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["centralLock"]["value"] == "UNLOCKED"
    assert lock.json()["data"]["frontLeftDoor"]["value"] == "CLOSED"
    
    change_data("frontLeftDoor","OPEN")
    change_data("centralLock","LOCKED")
    
    lock = client.get("/vehicles/12345678901234567/doors", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["frontLeftDoor"]["value"] == "OPEN"
    assert lock.json()["data"]["centralLock"]["value"] == "LOCKED"
    
def test_locking():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    lock = client.post("/vehicles/12345678901234567/commands/lock", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["invokeStatus"] == "COMPLETED"
    
    lock = client.post("/vehicles/12345678901234567/commands/lock", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["invokeStatus"] == "COMPLETED"


def test_unlocking():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    lock = client.post("/vehicles/12345678901234567/commands/unlock", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["invokeStatus"] == "WAITING"
    
    lock = client.post("/vehicles/12345678901234567/commands/unlock", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["invokeStatus"] == "WAITING"
    
def test_lock_reduced_guard():
    change_data("commands","LOCK_REDUCED_GUARD")
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    lock = client.post("/vehicles/12345678901234567/commands/lock-reduced-guard", headers=headers)
    assert lock.status_code == 200
    assert lock.json()["data"]["invokeStatus"] == "COMPLETED"

def test_flash():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    flash = client.post("/vehicles/12345678901234567/commands/flash", headers=headers)
    assert flash.status_code == 200
    assert flash.json()["data"]["invokeStatus"] == "COMPLETED"
    
def test_horn():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    horn = client.post("/vehicles/12345678901234567/commands/honk", headers=headers)
    assert horn.status_code == 200
    assert horn.json()["data"]["invokeStatus"] == "COMPLETED"

def test_horn_and_flash():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    horn_and_flash = client.post("/vehicles/12345678901234567/commands/honk-and-flash", headers=headers)
    assert horn_and_flash.status_code == 200
    assert horn_and_flash.json()["data"]["invokeStatus"] == "COMPLETED"

def test_statistic():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    statistic = client.get("/vehicles/12345678901234567/statistics", headers=headers)
    assert statistic.status_code == 200


def test_tyres():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    
    tyres = client.get("/vehicles/12345678901234567/tyres", headers=headers)
    assert tyres.status_code == 200
    assert tyres.json()["data"]["frontLeft"]["value"] == "NO_WARNING"
    
    change_data("frontLeft","VERY_LOW_PRESSURE")
    
    tyres = client.get("/vehicles/12345678901234567/tyres", headers=headers)
    assert tyres.status_code == 200
    assert tyres.json()["data"]["frontLeft"]["value"] == "VERY_LOW_PRESSURE"
    
def test_fuel():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    change_data("fuelICE",50)
    change_data("fuelElectric",60)
    fuel = client.get("/vehicles/12345678901234567/fuel", headers=headers)
    assert fuel.status_code == 200
    assert fuel.json()["data"]["fuelAmount"]["value"] == 50
    assert fuel.json()["data"]["batteryChargeLevel"]["value"] == 60
    
    change_data("fuelType","ELECTRIC")
    fuel = client.get("/vehicles/12345678901234567/fuel", headers=headers)
    assert fuel.status_code == 200
    assert fuel.json()["data"]["batteryChargeLevel"]["value"] == 60
    assert "fuelAmount" not in fuel.json()["data"]
    
    
    change_data("fuelType","PETROL")
    fuel = client.get("/vehicles/12345678901234567/fuel", headers=headers)
    assert fuel.status_code == 200
    assert fuel.json()["data"]["fuelAmount"]["value"] == 50
    assert "batteryChargeLevel" not in fuel.json()["data"]


def test_odometer():
    headers = {"vcc-api-key": "TEST_NO_OAUTH","content-type": "application/json"}
    odometer = client.get("/vehicles/12345678901234567/odometer", headers=headers)
    assert odometer.status_code == 200
    assert odometer.json()["data"]["odometer"]["value"] == 0
    
    change_data("odometer",100)
    odometer = client.get("/vehicles/12345678901234567/odometer", headers=headers)
    assert odometer.status_code == 200
    assert odometer.json()["data"]["odometer"]["value"] == 100


