
from pydantic import BaseModel, Field



class Scopes(BaseModel):
    scopes: list = Field(default=["openid"])
    
    def checkAccess(self, scope: str):
        if scope in self.scopes:
            return True
        return False
    
scopesList=["openid","conve:climatization_start_stop"]





# print(checkAccess("api_key_example", "openid"))  