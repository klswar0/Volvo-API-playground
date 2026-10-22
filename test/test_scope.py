import database
import main
import scopes
import pytest
from fastapi.testclient import TestClient


def change_data(attribute,value):
    database.AdditionalDatabase["TEST_SCOPE"].ScopesData.__setattr__(attribute,value)
    
    

client = TestClient(main.app)


def test_check_scope_func():
    assert scopes.checkScope("TEST_SCOPE",["openid"]) == True
    
    with pytest.raises(ValueError, match="The API key does not have access to the requested scope: conve:vehicle_relation"):
        scopes.checkScope("TEST_SCOPE", ["conve:vehicle_relation"])
    
def test_check_scope_endpoint():
    headers={"vcc-api-key": "TEST_SCOPE"}
    response = client.get("/connected-vehicle/v2/vehicles", headers=headers)
    assert response.status_code == 403
    change_data("scopes",["openid","conve:vehicle_relation"])
    response = client.get("/connected-vehicle/v2/vehicles", headers=headers)
    assert response.status_code == 200