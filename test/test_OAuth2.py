import database
import main
import hashlib
import base64

from fastapi.testclient import TestClient


def change_data(attribute,value):
    database.Oauth2Data["TEST_OAUTH"].__setattr__(attribute,value)
    
    

client = TestClient(main.app)

def test_func_PKCECheck_Plain():
    data=database.Oauth2Data["TEST_OAUTH"]
    func=main.PKCECheck(code_verifier="bad_code_verifier",oauth2=data)
    assert func == False
    func=main.PKCECheck(code_verifier="code_challenge",oauth2=data)
    assert func == True
    assert data.code_challenge_method == ""
    assert data.code_challenge == ""
    
    

def test_func_PKCECheck_S256():
    change_data("code_challenge_method","S256")
    change_data("code_challenge",base64.urlsafe_b64encode(hashlib.sha256("code_challenge".encode()).digest()).decode().rstrip("="))
    
    data=database.Oauth2Data["TEST_OAUTH"]
    print(data.code_challenge)
    func=main.PKCECheck(code_verifier="bad_code_verifier",oauth2=data)
    assert func == False
    func=main.PKCECheck(code_verifier="code_challenge",oauth2=data)
    assert func == True
    assert data.code_challenge_method == ""
    assert data.code_challenge == ""
    
    
    