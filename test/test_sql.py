import database
import main
from config import config
from fastapi.testclient import TestClient
import databaseSQL

def database_config():
    config['DATABASE']['TYPE'] = 'SQL'
    config['DATABASE']['SQL_TYPE'] = 'sqlite'
def purge():
    databaseSQL.regenerateDatabase(full=True)   
database_config()
client = TestClient(main.app)
dataInstance = databaseSQL.databaseSQL()

def test_database_contains():
    purge()
    assert ("vcc_api_key" in dataInstance)  == True
    assert (("vcc_api_secret" not in dataInstance) == True)

def test_database_getitem():
    purge()
    assert dataInstance["vcc_api_key"] == database.database["vcc_api_key"]
    assert dataInstance["all_values"] == database.database["all_values"]
    
def test_database_addCar():
    purge()
    start=database.database["vcc_api_key"]
    dataInstance.addCar(VIN="VIN321", vcc_api_key="vcc_api_key",car=database.Car(VIN="VIN321"))
    end=dataInstance["vcc_api_key"]
    assert start != end
    assert end[-1].VIN == "VIN321"

def test_database_findCar():
    purge()
    data=dataInstance.carFind(VIN="VIN123", vcc_api_key="vcc_api_key")
    assert data == database.database["vcc_api_key"][0]
    
def test_database_remove():
    purge()
    start=database.database["vcc_api_key"]
    dataInstance.remove(VIN="VIN123", api_key="vcc_api_key")
    end=dataInstance["vcc_api_key"]
    assert start != end
    assert end == []
    
    
def test_carInstance_keys():
    purge()
    car_instance = databaseSQL.carInstanceSQL(api_key="vcc_api_key", VIN="VIN123")
    keys = car_instance.keys()
    assert keys == database.database["vcc_api_key"][0].__dict__.keys() 

def test_carInstance_getitem():
    purge()
    car_instance = databaseSQL.carInstanceSQL(api_key="vcc_api_key", VIN="VIN123")
    assert car_instance["VIN"] == database.database["vcc_api_key"][0].VIN

def test_carInstance_setitem():
    purge()
    car_instance = databaseSQL.carInstanceSQL(api_key="vcc_api_key", VIN="VIN123")
    copy=car_instance.car.__dict__.copy()
    car_instance["VIN"] = "NEWVIN"
    assert car_instance["VIN"] == "NEWVIN"
    assert car_instance.car.__dict__ != copy

def test_carInstance_getattr():
    purge()
    car_instance = databaseSQL.carInstanceSQL(api_key="vcc_api_key", VIN="VIN123")
    assert car_instance.VIN == database.database["vcc_api_key"][0].VIN

def test_carInstance_setattr():
    purge()
    car_instance = databaseSQL.carInstanceSQL(api_key="vcc_api_key", VIN="VIN123")
    copy=car_instance.car.__dict__.copy()
    car_instance.VIN = "NEWVIN"
    assert car_instance.VIN == "NEWVIN"
    assert car_instance.car.__dict__ != copy

# def test_additionalData_contains():
#     assert "vcc_api_k"
