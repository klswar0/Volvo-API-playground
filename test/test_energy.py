import database
import main


from fastapi.testclient import TestClient

def change_data(attribute,value):
    database.database["TEST_NO_OAUTH"][0].__setattr__(attribute,value)
    

client = TestClient(main.app)

def test_capabilities_endpoint():
    change_data("electricRange", False)
    
    headers={"vcc-api-key": "TEST_NO_OAUTH"}
    response = client.get("/energy/v2/vehicles/12345678901234567/capabilities", headers=headers)
    assert response.status_code == 200
    

    assert response.json()["getEnergyState"]["isSupported"] == True
    assert response.json()["getEnergyState"]["batteryChargeLevel"]["isSupported"] == True
    assert response.json()["getEnergyState"]["electricRange"]["isSupported"] == False
    
    change_data("getEnergyState", False)
    response = client.get("/energy/v2/vehicles/12345678901234567/capabilities", headers=headers)
    assert response.status_code == 200
    assert response.json()["getEnergyState"]["isSupported"] == False
    

def test_energy_state_endpoint():
    change_data("electricRange", False)
    headers={"vcc-api-key": "TEST_NO_OAUTH"}
    response = client.get("/energy/v2/vehicles/12345678901234567/state", headers=headers)
    assert response.status_code == 200
    
    assert response.json()["batteryChargeLevel"]["status"] == "OK"
    assert response.json()["batteryChargeLevel"]["value"] == 0
    assert response.json()["batteryChargeLevel"]["unit"] == "percentage"
    assert response.json()["chargingStatus"]["status"] == "OK" 
    assert response.json()["chargingStatus"]["value"] == "IDLE"
    assert response.json()["electricRange"]["status"] == "ERROR"
    assert response.json()["electricRange"]["code"] == "PROPERTY_NOT_FOUND"
    assert response.json()["electricRange"]["message"] == "No valid value could be found for the requested property"
    
    change_data("getEnergyState", False)
    
    headers={"vcc-api-key": "TEST_NO_OAUTH"}
    response = client.get("/energy/v2/vehicles/12345678901234567/state", headers=headers)
    assert response.status_code == 404
    
    assert response.json()["code"] == "RESOURCE_NOT_SUPPORTED"
    assert response.json()["message"] == "Energy state not supported"

    