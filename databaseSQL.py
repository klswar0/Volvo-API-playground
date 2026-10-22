

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
    data: dict = Field(sa_column=Column(JSON))
    # could we change from data json to columns for attributes

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
    car1=CarRow(api_key="vcc_api_key", vin=database.database["vcc_api_key"][0].VIN, data=dictCar(database.database["vcc_api_key"][0]))
    car2=CarRow(api_key="vcc_api_key_Oauth2", vin=database.database["vcc_api_key_Oauth2"][0].VIN, data=dictCar(database.database["vcc_api_key_Oauth2"][0]))
        
    all_values =ApiKey(api_key="all_values")
    car3=CarRow(api_key="all_values", vin=database.database["all_values"][0].VIN, data=dictCar(database.database["all_values"][0]))
    car4=CarRow(api_key="all_values", vin=database.database["all_values"][1].VIN, data=dictCar(database.database["all_values"][1]))
    car5=CarRow(api_key="all_values", vin=database.database["all_values"][2].VIN, data=dictCar(database.database["all_values"][2]))
    
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
    engine = create_engine(f"mysql+pymysql://{readConfig('DATABASE', 'USER')}:{readConfig('DATABASE', 'PASSWORD')}@{readConfig('DATABASE', 'HOST')}:{readConfig('DATABASE', 'PORT')}/{readConfig('DATABASE', 'NAME')}")
    
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
    def __getitem__(self, key):
        with Session(engine) as session:
            statment=select(CarRow).where(CarRow.api_key==key)
            cars=session.exec(statment).all()
            data=[]
            for car in cars:
                data.append(Car(**car.data))
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
                car_row=CarRow(api_key=key, vin=car.VIN, data=car.__dict__)
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
                car_row=CarRow(api_key=key, vin=car.VIN, data=car.__dict__)
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
            return Car(**car.data)
    def addCar(self, VIN:str, vcc_api_key: str, car:Car):
        with Session(engine) as session:
            car_row=CarRow(api_key=vcc_api_key, vin=VIN, data=car.__dict__)
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
            for car in value:
                car_row=AdditionalData(api_key=key, vin=car.VIN, data=car.__dict__)
                session.add(car_row)
            session.commit()
            self.log(f"Added additional data for VIN: {car.VIN} under API key: {key}")
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
                car_row=AdditionalData(api_key=key, vin=car.VIN, data=car.__dict__)
                session.add(car_row)
                
            session.commit()
            self.log(f"Added additional data for VIN: {car.VIN} under API key: {key}")

    
    

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
        self.refresh()
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

        
        
