
from pydantic import BaseModel, Field
from database import AdditionalDatabase
# location: means the location API
# energy: means the energy API
# conve: means the connectivity API
scopesList=["openid","conve:battery_charge_level","conve:brake_status","conve:climatization_start_stop","conve:command_accessibility","conve:commands","conve:connectivity_status","conve:diagnostics_engine_status","conve:diagnostics_workshop","conve:doors_status","conve:engine_start_stop","conve:engine_status","conve:environment","conve:fuel_status","conve:honk_flash","conve:lock","conve:lock_status","conve:navigation","conve:odometer_status","conve:trip_statistics","conve:tyre_status","conve:unlock","conve:vehicle_relation","conve:warnings","conve:windows_status"]



class Scopes(BaseModel):
    scopes: list = Field(default=["openid"])
    
    def checkAccess(self, scopes: list):
        for scope in scopes:
            if scope not in self.scopes:
                return scope
        return True
    

def checkScope(api_key: str, scopes: list):
    data = AdditionalDatabase[api_key].ScopesData
    if data is None:
        return True
    check = data.checkAccess(scopes)
    if check == True:
        return True
    raise ValueError(f"The API key does not have access to the requested scope: {check}")





# print(checkAccess("api_key_example", "openid"))  