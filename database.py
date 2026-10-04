
from classCar import Car, AdditionalData, Oauth2, Scopes
from config import readConfig


database = {
        "vcc_api_key": [Car(VIN="VIN123", fuelType="HYBRID")],
        "all_values": [
            Car(
                VIN="VIN321",
                fuelType="HYBRID",
                frontLeftWindow="OPEN",
                frontRightWindow="CLOSED",
                rearLeftWindow="AJAR",
                rearRightWindow="UNSPECIFIED",
                sunroof="OPEN",
                centralLock="LOCKED",
                frontLeftDoor="OPEN",
                frontRightDoor="CLOSED",
                rearLeftDoor="AJAR",
                rearRightDoor="UNSPECIFIED",
            ),
            Car(
                VIN="VIN322",
                fuelType="ELECTRIC",
                fuelElectric=100,
                engineStatus="RUNNING",
                availabilityStatus_value="AVAILABLE",
                frontLeft="NO_WARNING",
                frontRight="VERY_LOW_PRESSURE",
                rearLeft="LOW_PRESSURE",
                rearRight="HIGH_PRESSURE",
            ),
            Car(
                VIN="VIN323",
                fuelType="PETROL",
                fuelICE=55,
                odometer=12345,
                serviceWarning="REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE",
                serviceTrigger="DISTANCE",
                tankLid="OPEN",
                hood="CLOSED",
                tailGate="AJAR",
            ),
        ],
        "vcc_api_key_Oauth2": [Car(VIN="VIN123", fuelType="HYBRID")]
    }

    #client id == api key for this playground
    # could we changes this to additonal data for scopes?
AdditionalDatabase={
        "vcc_api_key_Oauth2": AdditionalData(Oauth2Data=Oauth2(client_secret="client_secret", code="code", access_token="access_token", refresh_token="refresh_token")),
        "vcc_api_key": AdditionalData(ScopesData=Scopes(scopes=["openid","conve:vehicle_relation","location:read"])),
        "all_values": AdditionalData()
    }


            

class databaseInterface:
    def keys(self):
        return database.keys()
    def __getitem__(self, key):
        return database[key]
    
    def __contains__(self, key):
        return key in database
    def __setattr__(self, key, value):
        database[key] = value
    def __setitem__(self, key, value):
        database[key] = value
        
    def carFind(self, VIN:str, vcc_api_key: str):
        for car in database[vcc_api_key]:
            if car.VIN == VIN:
                return car
        raise ValueError("Invalid VIN")
databaseInterface = databaseInterface()

if True:
    class carInstance:
        def __init__(self,api_key:str,VIN:str):
            self.api_key = api_key
            self.car = databaseInterface.carFind(VIN,api_key)
        def keys(self):
            return self.car.__dict__.keys()
        def __getitem__(self, key):
            return self.car.__dict__[key]
        def __setitem__(self, key, value):
            databaseInterface[self.api_key][0].__dict__[key] = value

        def update(self,attribute,value,internal=False):
            self.car.update(attribute,value,internal=internal)
else:
    class carInstance:
        pass


def createCar(api_key: str, car: Car):
    if api_key in databaseInterface:
        databaseInterface[api_key].append(car)
    else:
        databaseInterface[api_key] = [car]
            
    if api_key not in AdditionalDatabase:
        AdditionalDatabase[api_key] = AdditionalData()
            