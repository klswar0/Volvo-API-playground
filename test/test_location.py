import database
import main


from fastapi.testclient import TestClient

def change_data(attribute,value):
    database.database["TEST_NO_OAUTH"][0].__setattr__(attribute,value)
    

client = TestClient(main.app)

def test_list_cars():
    headers = {"vcc-api-key": "TEST_NO_OAUTH"}
    vehicles = client.get("/location/v1/vehicles/12345678901234567/location", headers=headers)
    assert vehicles.status_code == 200
    assert vehicles.json()["data"]["geometry"]["coordinates"] == [11.968307501897431,57.68877357281511,0]
    assert vehicles.json()["data"]["properties"]["heading"] == "0"

    
    change_data("latitude", 59.3293)
    change_data("longitude", 18.0686)
    change_data("heading", 90)
    change_data("altitude", 10)
    vehicles = client.get("/location/v1/vehicles/12345678901234567/location", headers=headers)
    assert vehicles.status_code == 200
    assert vehicles.json()["data"]["geometry"]["coordinates"] == [18.0686,59.3293,10]
    assert vehicles.json()["data"]["properties"]["heading"] == "90"
