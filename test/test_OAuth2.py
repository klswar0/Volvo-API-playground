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
    


def test_code_exchange_PKCE():
    # need to make PKCE versions with/without and all possible errors
    change_data("redirect_uri","test/url")
    change_data("PKCE",True)
    
    data=database.Oauth2Data["TEST_OAUTH"]
    
    authorization = "Basic " + base64.b64encode(f"TEST_OAUTH:{data.client_secret}".encode("utf-8")).decode("utf-8") 
    
    exchange=client.post("/as/token.oauth2",data={"code": data.code,"code_verifier":"code_challenge","grant_type":"authorization_code","redirect_uri": data.redirect_uri},headers={"Authorization": authorization})
    
    assert exchange.status_code == 200
    assert exchange.json()["access_token"] == data.access_token
    assert exchange.json()["refresh_token"] == data.refresh_token
    assert exchange.json()["token_type"] == "Bearer"
    
def test_code_exchange():
    # need to make PKCE versions with/without and all possible errors
    change_data("redirect_uri","test/url")
    change_data("PKCE",False)
    
    data=database.Oauth2Data["TEST_OAUTH"]
    
    authorization = "Basic " + base64.b64encode(f"TEST_OAUTH:{data.client_secret}".encode("utf-8")).decode("utf-8") 
    
    exchange=client.post("/as/token.oauth2",data={"code": data.code,"grant_type":"authorization_code","redirect_uri": data.redirect_uri},headers={"Authorization": authorization})
    
    assert exchange.status_code == 200
    assert exchange.json()["access_token"] != ""
    assert exchange.json()["refresh_token"] != ""
    assert exchange.json()["access_token"] == data.access_token
    assert exchange.json()["refresh_token"] == data.refresh_token
    assert exchange.json()["token_type"] == "Bearer"
    
def test_code_exchange_possibilities():
    # no url set (not real world scenario but possible in this test environment)
    change_data("redirect_uri","")
    
    data=database.Oauth2Data["TEST_OAUTH"]

    
    authorization = "Basic " + base64.b64encode(f"TEST_OAUTH:{data.client_secret}".encode("utf-8")).decode("utf-8") 
    
    exchange=client.post("/as/token.oauth2",data={"code": data.code,"grant_type":"authorization_code"},headers={"Authorization": authorization})
    
    assert exchange.status_code == 200
    assert exchange.json()["access_token"] == data.access_token
    assert exchange.json()["refresh_token"] == data.refresh_token
    assert exchange.json()["token_type"] == "Bearer"
    
    # url bad
    change_data("redirect_uri","test/url")
    
    exchange=client.post("/as/token.oauth2",data={"code": data.code,"grant_type":"authorization_code","redirect_uri": data.redirect_uri},headers={"Authorization": authorization})
    
    assert exchange.status_code == 400
    
    # code bad
    exchange=client.post("/as/token.oauth2",data={"code": "bad_code","grant_type":"authorization_code","redirect_uri": data.redirect_uri},headers={"Authorization": authorization})
    
    assert exchange.status_code == 400
    
    # authorization bad
    exchange=client.post("/as/token.oauth2",data={"code": data.code,"grant_type":"authorization_code","redirect_uri": data.redirect_uri},headers={"Authorization": "Basic bad_authorization"})
    
    assert exchange.status_code == 401

def test_refresh_token():
    data=database.Oauth2Data["TEST_OAUTH"]
    
    authorization = "Basic " + base64.b64encode(f"TEST_OAUTH:{data.client_secret}".encode("utf-8")).decode("utf-8")
    
    refresh=client.post("/as/token.oauth2",data={"grant_type":"refresh_token","refresh_token": data.refresh_token},headers={"Authorization": authorization})
    
    assert refresh.status_code == 200
    assert refresh.json()["access_token"] != ""
    assert refresh.json()["refresh_token"] != ""
    assert refresh.json()["access_token"] == data.access_token
    assert refresh.json()["refresh_token"] == data.refresh_token
    
def test_refresh_token_PKCE():
    change_data("PKCE",False)
    
    data=database.Oauth2Data["TEST_OAUTH"]
    
    authorization = "Basic " + base64.b64encode(f"TEST_OAUTH:{data.client_secret}".encode("utf-8")).decode("utf-8")
    
    refresh=client.post("/as/token.oauth2",data={"grant_type":"refresh_token","refresh_token": data.refresh_token},headers={"Authorization": authorization})
    
    assert refresh.status_code == 200
    assert refresh.json()["access_token"] != ""
    assert refresh.json()["refresh_token"] != ""
    assert refresh.json()["access_token"] == data.access_token
    assert refresh.json()["refresh_token"] == data.refresh_token
    
def test_refresh_token_possibilities():
    data=database.Oauth2Data["TEST_OAUTH"]
    
    authorization = "Basic " + base64.b64encode(f"TEST_OAUTH:{data.client_secret}".encode("utf-8")).decode("utf-8")
    
    # refresh token bad
    refresh=client.post("/as/token.oauth2",data={"grant_type":"refresh_token","refresh_token": "bad_refresh_token"},headers={"Authorization": authorization})
    
    assert refresh.status_code == 400
    
    # authorization bad
    refresh=client.post("/as/token.oauth2",data={"grant_type":"refresh_token","refresh_token": data.refresh_token},headers={"Authorization": "Basic bad_authorization"})
    
    assert refresh.status_code == 401


def test_OAuth_post_PKCE():
    change_data("PKCE",True)
    
    data=database.Oauth2Data["TEST_OAUTH"]
    
    func=client.post("/as/authorization.internal",data={"client_id": "TEST_OAUTH", "redirect_uri": "url/test","state": "test123","code_challenge": "code_challenge","code_challenge_method": "S256","login":"TEST_OAUTH"})

    assert func.status_code == 200
    headers=func.headers["HX-Redirect"]
    headers=headers.split("?")
    assert headers[0] == "url/test"
    assert headers[1].split("&")[0] == "code=" + data.code
    assert headers[1].split("&")[1] == "state=test123"
    
    
def test_OAuth_post():
    data=database.Oauth2Data["TEST_OAUTH"]
    
    func=client.post("/as/authorization.internal",data={"client_id": "TEST_OAUTH", "redirect_uri": "url/test","state": "test123","login":"TEST_OAUTH"})


    assert func.status_code == 200
    headers=func.headers["HX-Redirect"]
    headers=headers.split("?")
    assert headers[0] == "url/test"
    assert headers[1].split("&")[0] == "code=" + data.code
    assert headers[1].split("&")[1] == "state=test123"
    
def test_OAuth_post_possibilities():
    change_data("PKCE",True)
    
    data=database.Oauth2Data["TEST_OAUTH"]
    
    func=client.post("/as/authorization.internal",data={"client_id": "TEST_OAUTH", "redirect_uri": "url/test","state": "test123","code_challenge": "code_challenge","code_challenge_method": "l","login":"TEST_OAUTH"})

    assert func.status_code == 200
    assert func.text == "<p style='color: red;'>ERROR with PKCE code_challenge_method</p>"
    
