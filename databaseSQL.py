

import database 
from sqlmodel import Column, JSON, Field, SQLModel, Session, create_engine, delete, select, text
from classCar import Car, AdditionalData, Oauth2, Scopes
from config import readConfig


def dictCar(car:Car):
    return car.__dict__

class ApiKey(SQLModel, table=True):
    api_key: str = Field(primary_key=True)

class CarRow(SQLModel ,table=True):
    id: int | None = Field(default=None, primary_key=True)
    api_key: str = Field(foreign_key="apikey.api_key", index=True)
    vin: str = Field(index=True)
    #data: dict = Field(sa_column=Column(JSON))
    # could we change from data json to columns for attributes
    
    def AddValues(self, car:Car):
        for key, value in car.__dict__.items():
            if key=="VIN":
                if value != self.vin:
                    #shoyldnt happen so can  be commented
                    raise ValueError("VIN mismatch between CarRow and Car object")
                continue
            setattr(self, key, value)
    
    def generateCar(self):
        car_data = {}
        for key in self.__dict__.keys():
            if key not in ['id', 'api_key']:
                if key == 'vin':
                    car_data['VIN'] = getattr(self, key)
                car_data[key] = getattr(self, key)
        return Car(**car_data)
    
    #this is a copy from classcar
    modelYear: int = Field(2019)
    gearboxType: str = Field(default="AUTOMATIC") #possible values: MANUAL, AUTOMATIC
    fuelType: str = Field(default="HYBRID") #possible values: PETROL, DIESEL, ELECTRIC, HYBRID
    fuelICE:int = Field(default=0) # fuel level for petrol and diesel cars
    fuelElectric:int = Field(default=0) # fuel level for electric and hybrid cars
    odometer: int = Field(default=0) 
    climate: bool =Field(default=False) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts? OR only engine has a timer)
    commands:list =Field(default=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP","FLASH","HONK", "HONK_AND_FLASH","LOCK","UNLOCK"],sa_column=Column(JSON)) # and reduced guard lock but not implemented yet. TO IMPLEMENT                     
    availabilityStatus_value: str = Field(default="AVAILABLE") # AVAILABLE, UNAVAILABLE, UNSPECIFIED # AVAILABLE is needed for any command TO IMPLEMENT
    availabilityStatus_unavailableReason: str = Field(default="") # Description of why the vehicle is unavailable UNSPECIFIED, NO_INTERNET, POWER_SAVING_MODE, CAR_IN_USE
    engineStatus:str = Field(default="STOPPED") # possible values: STOPPED, RUNNING
    engineTime:int = Field(default=0) # TODO:how long should engine run in future time based (one variable that is time when engine will be turned off not (enginestatus and enginetime))
    
    #diagnostic parameters
    engineCoolantLevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    oilLevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, SERVICE_REQUIRED, TOO_LOW, TOO_HIGH.
    
    serviceWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, UNKNOWN_WARNING, REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE, ENGINE_HOURS_ALMOST_TIME_FOR_SERVICE, DISTANCE_DRIVEN_ALMOST_TIME_FOR_SERVICE, REGULAR_MAINTENANCE_TIME_FOR_SERVICE, ENGINE_HOURS_TIME_FOR_SERVICE, DISTANCE_DRIVEN_TIME_FOR_SERVICE, REGULAR_MAINTENANCE_OVERDUE_FOR_SERVICE, ENGINE_HOURS_OVERDUE_FOR_SERVICE, DISTANCE_DRIVEN_OVERDUE_FOR_SERVICE.
    serviceTrigger:str =Field(default="UNSPECIFIED") #Values: CALENDAR_TIME, DISTANCE, ENGINE_HOURS, UNSPECIFIED, UNKNOWN.
    engineHoursToService:int = Field(default=0) # in hours
    distanceToService:int = Field(default=0) # in km
    timeToService:int = Field(default=0) # in days (or months. need to check when they change to months. stored in days sent in both?)
    
    washerFluidLevelWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW. # not sure no infornation about it in official docs but sent thru real API response

    brakeFluidLevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    
    
    
    #windows
    #Values: UNSPECIFIED, OPEN, CLOSED, AJAR- not fully open? Mostly for sunroof .
    frontLeftWindow:str = Field(default="CLOSED")  
    frontRightWindow:str = Field(default="CLOSED") 
    rearRightWindow:str = Field(default="CLOSED")
    rearLeftWindow:str = Field(default="CLOSED")
    sunroof:str = Field(default="CLOSED") # UNSPECIFIED means mostly that car doesnt have sunroof
    
    #doors and locks
    
    centralLock:str = Field(default="UNLOCKED") #Possible values: UNSPECIFIED, UNLOCKED, LOCKED.
    
    #Values: UNSPECIFIED, OPEN, CLOSED, AJAR.
    frontLeftDoor:str = Field(default="CLOSED") 
    frontRightDoor:str = Field(default="CLOSED") 
    rearLeftDoor:str = Field(default="CLOSED")
    rearRightDoor:str = Field(default="CLOSED") 
    tailGate:str = Field(default="CLOSED") 
    hood:str = Field(default="CLOSED") 
    tankLid:str = Field(default="CLOSED") # UNSPECIFIED means mostly that car doesnt have sensors
    
    #tires value UNSPECIFIED, NO_WARNING, VERY_LOW_PRESSURE, LOW_PRESSURE, HIGH_PRESSURE.
    frontLeft:str = Field(default="NO_WARNING")
    frontRight:str = Field(default="NO_WARNING")
    rearLeft:str = Field(default="NO_WARNING")
    rearRight:str = Field(default="NO_WARNING")

    #lights

    #brake
    brakeLightLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    brakeLightCenterWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    brakeLightRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #fog
    fogLightFrontWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    fogLightRearWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #position
    positionLightFrontLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    positionLightFrontRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    positionLightRearLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    positionLightRearRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #high beam
    highBeamLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    highBeamRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #low beam
    lowBeamLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    lowBeamRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #daytime running
    daytimeRunningLightLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    daytimeRunningLightRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #turn indication
    turnIndicationFrontLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    turnIndicationFrontRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    turnIndicationRearLeftWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    turnIndicationRearRightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #registration plate light
    registrationPlateLightWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #side mark lights
    sideMarkLightsWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #hazard lights
    hazardLightsWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.
    #reverse lights
    reverseLightsWarning:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, FAILURE.








    
    lastTimestamp:str = Field(default="") #set if not available
    
    
    lightTimestamp:str = Field(default="")#set if light commands is sent
    
    hornTimestamp:str = Field(default="") # set if horn commands is sent

    nextInvoiceStatus:str = Field(default="") # Possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
    # running available for climate or engine commands
    
    
    ###
    ### location 
    ### parameters
    ###
    
    longitude:float=Field(default=11.968307501897431)
    latitude:float=Field(default=57.68877357281511) 
    altitude:float=Field(default=0.0)
    
    heading:int=Field(default=0) # 0-360 degrees
    
    ###
    ### energy API
    ### capabilities
    ###
    
    getEnergyState:bool=Field(default=True)
    batteryChargeLevel:bool=Field(default=True)
    electricRange:bool=Field(default=True)
    chargerConnectionStatus:bool=Field(default=True)
    chargingSystemStatus:bool=Field(default=True)
    chargingType:bool=Field(default=True)
    chargerPowerStatus:bool=Field(default=True)
    estimatedChargingTimeToTargetBatteryChargeLevel:bool=Field(default=True)
    targetBatteryChargeLevel:bool=Field(default=True)
    chargingCurrentLimit:bool=Field(default=True)
    chargingPower:bool=Field(default=True)
    
    # states for energy API
    electricRangeValue:int=Field(default=0) # in km or miles
    electricRangeUnit:str=Field(default="km")
    
    chargerConnectionStatusValue:str=Field(default="DISCONNECTED") # possible values: DISCONNECTED, CONNECTED, FAULT
    
    chargingStatusValue:str=Field(default="IDLE") # possible values: IDLE, CHARGING, SCHEDULED, DISCHARGING, ERROR, DONE
    
    chargingTypeValue:str=Field(default="NONE") # possible values: AC, DC, NONE
    
    chargerPowerStatusValue:str=Field(default="") # Value provided from charger example: PROVIDING_POWER
    
    estimatedChargingTimeToTargetBatteryChargeLevelValue:int=Field(default=0) # in minutes
    
    chargingCurrentLimitValue:int=Field(default=0) # in Amperes
    
    targetBatteryChargeLevelValue:int=Field(default=0) # in % so 0-100
    
    chargingPowerValue:int=Field(default=0) # in watts

class AdditionalRow(SQLModel, table=True):
    api_key: str = Field(primary_key=True)
    scopes: dict = Field(sa_column=Column(JSON))
    Oauth2: dict = Field(sa_column=Column(JSON))
    
def regenerateDatabase(full:bool=False):
    SQLModel.metadata.create_all(engine)
    if  full:
        with Session(engine) as session:
            session.exec(delete(CarRow))
            session.exec(delete(AdditionalRow))
            session.exec(delete(ApiKey))
            session.commit()
            log("All database rows have been cleanly deleted.")
    

    api_key=ApiKey(api_key="vcc_api_key")
    api_key_Oauth2=ApiKey(api_key="vcc_api_key_Oauth2")
    car1=CarRow(api_key="vcc_api_key", vin=database.database["vcc_api_key"][0].VIN)
    car1.AddValues(database.database["vcc_api_key"][0])
    car2=CarRow(api_key="vcc_api_key_Oauth2", vin=database.database["vcc_api_key_Oauth2"][0].VIN)
    car2.AddValues(database.database["vcc_api_key_Oauth2"][0])
        
    all_values =ApiKey(api_key="all_values")
    car3=CarRow(api_key="all_values", vin=database.database["all_values"][0].VIN)
    car3.AddValues(database.database["all_values"][0])
    car4=CarRow(api_key="all_values", vin=database.database["all_values"][1].VIN)
    car4.AddValues(database.database["all_values"][1])
    car5=CarRow(api_key="all_values", vin=database.database["all_values"][2].VIN)
    car5.AddValues(database.database["all_values"][2])
    
    with Session(engine) as session:
        session.exec(delete(CarRow).where(CarRow.api_key=="vcc_api_key"))
        session.exec(delete(ApiKey).where(ApiKey.api_key=="vcc_api_key"))
        session.exec(delete(CarRow).where(CarRow.api_key=="vcc_api_key_Oauth2"))
        session.exec(delete(ApiKey).where(ApiKey.api_key=="vcc_api_key_Oauth2"))
        session.exec(delete(CarRow).where(CarRow.api_key=="all_values"))
        session.exec(delete(ApiKey).where(ApiKey.api_key=="all_values"))
        session.commit()
        
        session.add(api_key)
        session.add(car1)
        session.add(api_key_Oauth2)
        session.add(car2)
        session.add(all_values)
        session.add(car3)
        session.add(car4)
        session.add(car5)
        session.commit()
        
def log(text:str,error:bool=False):
    if error:
        print(f"\033[31m{text}\033[0m")
    else:
        print(f"\033[32m{text}\033[0m")

# Format: mysql+pymysql://<user>:<password>@<host>:<port>/<database_name>
try:
    if readConfig('DATABASE', 'SQL_TYPE') == "mysql":
        engine = create_engine(f"mysql+pymysql://{readConfig('DATABASE', 'USER')}:{readConfig('DATABASE', 'PASSWORD')}@{readConfig('DATABASE', 'HOST')}:{readConfig('DATABASE', 'PORT')}/{readConfig('DATABASE', 'NAME')}")
    else:
        engine = create_engine(f"sqlite:///{readConfig('DATABASE', 'NAME')}.db")
    regenerateDatabase(readConfig('DATABASE', 'Purge', True))
    log(f"Database connection successful.")
        
except Exception as e:
    log(f"Error creating database engine:\n{e}", error=True)
    exit(1)


    
class databaseSQL:       
    def log(self, text:str,error:bool=False):
        if readConfig('DATABASE', 'DEBUG',True):
            log(text,error=error)
    def __contains__(self, key):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            self.log(f"API key exists: {api_key is not None}")
            return api_key is not None
    def keys(self):
        with Session(engine) as session:
            statment=select(ApiKey)
            return session.exec(statment).all()
            # warning output is wierd
                
    def __getitem__(self, key):
        with Session(engine) as session:
            statment=select(CarRow).where(CarRow.api_key==key)
            cars=session.exec(statment).all()
            data=[]
            for car in cars:
                data.append(car.generateCar())
            self.log(f"Retrieved cars for API key {key}: {data}")
            return data
        # apiInstance=apiKeySQL(api_key=key)
        # return apiInstance
    def __setattr__(self, key, value):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            if api_key is None:
                api_key=ApiKey(api_key=key)
                session.add(api_key)
                session.commit()
                self.log(f"WARNING: Created new API key for additional data: {key}", error=True)
            for car in value:
                car_row=CarRow(api_key=key, vin=car.VIN)
                car_row.AddValues(car)
                session.add(car_row)
            self.log(f"Added data for VIN: {car.VIN} under API key: {key}")
            session.commit()
    # TODO check add logic dahsboard
    def __setitem__(self, key, value):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            if api_key is None:
                api_key=ApiKey(api_key=key)
                session.add(api_key)
                session.commit()
                self.log(f"WARNING: Created new API key for additional data: {key}", error=True)
            for car in value:
                car_row=CarRow(api_key=key, vin=car.VIN)
                car_row.AddValues(car)
                session.add(car_row)
            session.commit()
            self.log(f"Added data for VIN: {value} under API key: {key}")
    def carFind(self, VIN:str, vcc_api_key: str):
        with Session(engine) as session:
            statment=select(CarRow).where(CarRow.api_key==vcc_api_key, CarRow.vin==VIN)
            car=session.exec(statment).first()
            if car is None:
                self.log(f"Car not found for VIN: {VIN}", error=True)
                raise ValueError("Invalid VIN")
            return car.generateCar()
    def addCar(self, VIN:str, vcc_api_key: str, car:Car):
        with Session(engine) as session:
            car_row=CarRow(api_key=vcc_api_key, vin=VIN)
            car_row.AddValues(car)
            session.add(car_row)
            session.commit()
            self.log(f"Added car for VIN: {VIN} under API key: {vcc_api_key}")
    def remove(self,api_key: str, VIN: str):
        print("accessing remove method")
        with Session(engine) as session:
            statment=select(CarRow).where(CarRow.api_key==api_key, CarRow.vin==VIN)
            car=session.exec(statment).first()
            if car is None:
                self.log(f"Car not found for VIN: {VIN} under API key: {api_key}", error=True)
                raise ValueError("Invalid VIN")
            session.delete(car)
            session.commit()
            self.log(f"Removed car for VIN: {VIN} under API key: {api_key}")
        
         
        
class additionalDataSQL:
    def log(self, text:str,error:bool=False):
            if readConfig('DATABASE', 'DEBUG',True):
                log(text,error=error)
    def __contains__(self, key):

        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            self.log(f"API key exists for additional data: {api_key is not None}")
            return api_key is not None
    def keys(self):
        with Session(engine) as session:
            statment=select(ApiKey)
            values=session.exec(statment).all()
            self.log(f"Retrieved API keys: {[v.api_key for v in values]}")
            return values
    def __getitem__(self, key):
        with Session(engine) as session:
            self.log(f"Getting item: {key}/AdditionalData")

            statement = select(AdditionalRow).where(
                AdditionalRow.api_key == key
            )
            row = session.exec(statement).first()

            if row is None:
                return AdditionalData()

            return AdditionalData(
                Oauth2Data=Oauth2(**row.Oauth2) if row.Oauth2 else None,
                ScopesData=Scopes(**row.scopes) if row.scopes else None,
            )
    def __setattr__(self, key, value):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            if api_key is None:
                api_key=ApiKey(api_key=key)
                session.add(api_key)
                session.commit()
                self.log(f"WARNING: Created new API key for additional data: {key}", error=True)
            # for car in value:
            #     car_row=AdditionalData(api_key=key, vin=car.VIN, data=car.__dict__)
            #     session.add(car_row)
            #what this code is for ? why its wrong but never any errros came
            self.log('WARNING: check the code or contact the developer. This code is not correct and should be fixed.', error=True)
            session.commit()
            #self.log(f"Added additional data for VIN: {car.VIN} under API key: {key}")
    def __setitem__(self, key, value):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            if api_key is None:
                api_key=ApiKey(api_key=key)
                session.add(api_key)
                session.commit()
                self.log(f"WARNING: Created new API key for additional data: {key}", error=True)
            # for car in value:
            #     car_row=AdditionalData(api_key=key, vin=car.VIN, data=car.__dict__)
            #     session.add(car_row)
            self.log('WARNING: check the code or contact the developer. This code is not correct and should be fixed.', error=True)
                
            session.commit()
            #self.log(f"Added additional data for VIN: {car.VIN} under API key: {key}")

    
    

# class InstanceAdditionalDataSQL:
#     pass
        

    
class carInstanceSQL:
    def log(self, text:str,error:bool=False):
        if readConfig('DATABASE', 'DEBUG',True):
            log(text,error=error)
    
    def __init__(self, api_key: str, VIN: str):
        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(
            self,
            "car",
            databaseSQL().carFind(VIN=VIN, vcc_api_key=api_key),
        )
        self.log(f"Initialized carInstanceSQL with API key: {api_key} and VIN: {VIN}")

    
    def refresh(self):    
        # with Session(engine) as session:
        #     # statment=select(ApiKey).where(ApiKey.api_key==self.api_key,CarRow.vin==self.car.VIN)
        #     # car=session.exec(statment).first()
        #     # if car is None:
        #     #     raise ValueError("Invalid VIN")
            object.__setattr__(
                    self,
                    "car",
                    databaseSQL().carFind(VIN=self.car.VIN, vcc_api_key=self.api_key),
                    )
            self.log(f"Refreshed car data for VIN: {self.car.VIN} under API key: {self.api_key}")
    def keys(self):
        # self.refresh() doesnt need it here keys are a;ways the same
        self.log(f"Accessing keys for VIN: {self.car.VIN} under API key: {self.api_key}")
        return self.car.__dict__.keys()
    def __getitem__(self, key):
        if readConfig("DATABASE", "ALWAYS_REFRESH",True):
            self.refresh()
        self.log(f"Accessing item {key} for VIN: {self.car.VIN} under API key: {self.api_key}")
        return self.car.__dict__[key]
    def __setitem__(self, key, value):
        self.log(f"Setting item {key} to {value} for VIN: {self.car.VIN} under API key: {self.api_key}")
        return self.car.__dict__.__setitem__(key, value)
    
    def __getattr__(self, key):
        if readConfig("DATABASE", "ALWAYS_REFRESH",True):
            self.refresh()
        self.log(f"Accessing attribute {key} for VIN: {self.car.VIN} under API key: {self.api_key}")
        return self.car.__getattribute__(key)
    
    def __setattr__(self, key, value):
        self.log(f"Setting attribute {key} to {value} for VIN: {self.car.VIN} under API key: {self.api_key}")
        return self.car.__setattr__(self.car, key, value)

    def update(self,attribute,value,internal=False):
        self.car.update(attribute,value,internal=internal)
        self.log(f"Updated car data for VIN: {self.car.VIN} under API key: {self.api_key}")

        
        
