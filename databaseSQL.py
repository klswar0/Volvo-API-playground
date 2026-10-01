

import database 
from sqlmodel import Column, JSON, Field, SQLModel, Session, create_engine, select
from classCar import Car as dictCar, AdditionalData, Oauth2, Scopes

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
    
engine = create_engine("sqlite:///database.db")


SQLModel.metadata.create_all(engine)

    
class databaseSQL:
    def keys(self):
        with Session(engine) as session:
            statment=select(ApiKey)
            return session.exec(statment).all()
    def __getitem__(self, key):
        