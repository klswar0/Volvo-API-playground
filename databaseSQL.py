

import database 
from sqlmodel import Column, JSON, Field, SQLModel, Session, create_engine, delete, select
from classCar import Car, AdditionalData, Oauth2, Scopes

def dictCar(car:Car):
    return car.__dict__

class ApiKey(SQLModel, table=True):
    api_key: str = Field(primary_key=True)

class CarRow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    api_key: str = Field(foreign_key="apikey.api_key", index=True)
    vin: str = Field(index=True)
    data: dict = Field(sa_column=Column(JSON))

class AdditionalRow(SQLModel, table=True):
    api_key: str = Field(primary_key=True)
    data: dict = Field(sa_column=Column(JSON))
    


# Format: mysql+pymysql://<user>:<password>@<host>:<port>/<database_name>
engine = create_engine("mysql+pymysql://test:1234@127.0.0.1:3306/api")


SQLModel.metadata.create_all(engine)

    
class databaseSQL:
    def __contains__(self, key):
        print(f"Checking if key exists: {key}")
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            print(f"Key exists: {api_key is not None}")
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
            return data
    def __setattr__(self, key, value):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            if api_key is None:
                api_key=ApiKey(api_key=key)
                session.add(api_key)
                session.commit()
            for car in value:
                car_row=CarRow(api_key=key, vin=car.VIN, data=car.__dict__)
                session.add(car_row)
            session.commit()
    def __setitem__(self, key, value):
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==key)
            api_key=session.exec(statment).first()
            if api_key is None:
                api_key=ApiKey(api_key=key)
                session.add(api_key)
                session.commit()
            for car in value:
                car_row=CarRow(api_key=key, vin=car.VIN, data=car.__dict__)
                session.add(car_row)
            session.commit()
    def carFind(self, VIN:str, vcc_api_key: str):
        with Session(engine) as session:
            statment=select(CarRow).where(CarRow.api_key==vcc_api_key, CarRow.vin==VIN)
            car=session.exec(statment).first()
            if car is None:
                raise ValueError("Invalid VIN")
            return dictCar(**car.data)
        
class carInstanceSQL:
    def __init__(self, api_key: str, VIN: str):
        object.__setattr__(self, "api_key", api_key)
        object.__setattr__(
            self,
            "car",
            databaseSQL().carFind(VIN=VIN, vcc_api_key=api_key),
        )

    
    def refresh(self):    
        with Session(engine) as session:
            statment=select(ApiKey).where(ApiKey.api_key==self.api_key,CarRow.vin==self.car.VIN)
            car=session.exec(statment).first()
            if car is None:
                raise ValueError("Invalid VIN")
            object.__setattr__(
                    self,
                    "car",
                    databaseSQL().carFind(VIN=self.VIN, vcc_api_key=self.api_key),
                    )
    def keys(self):
        object.refresh(self)
        return self.car.__dict__.keys()
    def __getitem__(self, key):
        object.refresh(self)
        return self.car.__dict__[key]
    def __setitem__(self, key, value):
        return self.car.__dict__.__setitem__(key, value)
    
    def __getattr__(self, key):
        object.refresh(self)
        return self.car.__getattribute__(key)
    
    def __setattr__(self, key, value):
        return self.car.__setattr__(self.car, key, value)

    def update(self,attribute,value,internal=False):
        self.car.update(attribute,value,internal=internal)
        
        
        
def regenerateDatabase():
    api_key=ApiKey(api_key="vcc_api_key")
    car1=CarRow(api_key="vcc_api_key", vin="WBA5A7C50ED607123", data=dictCar(Car(VIN="VIN123")))
    with Session(engine) as session:
        session.exec(delete(CarRow))
        session.exec(delete(ApiKey))
        session.add(api_key)
        session.add(car1)
        session.commit()