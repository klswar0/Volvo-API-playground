from pydantic import BaseModel, Field 
from notifier import notifier
from datetime import datetime, timezone
import configparser #TODO use it


class AuthHeader(BaseModel):
    content_type: str = Field(default="application/json", alias="Content-Type")
    authorization: str =Field(default="") #= Field(...) # NOT IMPLEMENTED
    vcc_api_key: str =Field(...,alias="vcc-api-key")


startUp={
    "Validation": True,
    "Dashboard": True,# not implemented yet
    "Websocket": True,# not implemented yet
    "TOKENcheck": False, # not implemented yet
    "statusNofication": "ALL" # possible values: SET-data is change, ALL- all debug info, VOLVO-only volvo api changes
}



options = {
    "fuelType": ["PETROL", "DIESEL", "ELECTRIC", "HYBRID"],
    "fuelICE": "int", # in liters
    "fuelElectric": "int", # in % so 0-100
    "odometer": "int", # 0-infinity in km

    "climate": [True, False],
    "engine": ["ENGINE_START", "ENGINE_STOP"],
    "availabilityStatus_value": ["AVAILABLE", "UNAVAILABLE", "UNSPECIFIED"],
    "availabilityStatus_unavailableReason": ["UNSPECIFIED", "NO_INTERNET", "POWER_SAVING_MODE", "CAR_IN_USE",""],
    "engineStatus": ["STOPPED", "RUNNING"],
    "engineCoolantLever": ["UNSPECIFIED", "NO_WARNING", "TOO_LOW"],
    "oillevel": ["UNSPECIFIED", "NO_WARNING", "SERVICE_REQUIRED", "TOO_LOW", "TOO_HIGH"],
    "serviceWarning": ["UNSPECIFIED", "NO_WARNING", "UNKNOWN_WARNING", "REGULAR_MAINTENANCE_ALMOST_TIME_FOR_SERVICE", "ENGINE_HOURS_ALMOST_TIME_FOR_SERVICE", "DISTANCE_DRIVEN_ALMOST_TIME_FOR_SERVICE", "REGULAR_MAINTENANCE_TIME_FOR_SERVICE", "ENGINE_HOURS_TIME_FOR_SERVICE", "DISTANCE_DRIVEN_TIME_FOR_SERVICE", "REGULAR_MAINTENANCE_OVERDUE_FOR_SERVICE", "ENGINE_HOURS_OVERDUE_FOR_SERVICE", "DISTANCE_DRIVEN_OVERDUE_FOR_SERVICE"],
    "serviceTrigger": ["CALENDAR_TIME", "DISTANCE", "ENGINE_HOURS", "UNSPECIFIED", "UNKNOWN"],
    "washerFluidLevelWarning": ["UNSPECIFIED", "NO_WARNING", "TOO_LOW"],
    "brakeFluidLevel": ["UNSPECIFIED", "NO_WARNING", "TOO_LOW"],
    "frontLeftWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "frontRightWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearLeftWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearRightWindow": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "sunroof": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "centralLock": ["UNSPECIFIED", "UNLOCKED", "LOCKED"],
    "frontLeftDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "frontRightDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearLeftDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "rearRightDoor": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "tailGate": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "hood": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "tankLid": ["UNSPECIFIED", "OPEN", "CLOSED", "AJAR"],
    "frontLeft": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "frontRight": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "rearLeft": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "rearRight": ["UNSPECIFIED", "NO_WARNING", "VERY_LOW_PRESSURE", "LOW_PRESSURE", "HIGH_PRESSURE"],
    "nextInvoiceStatus": ["RUNNING", "WAITING", "COMPLETED", "REJECTED", "UNKNOWN", "TIMEOUT", "CONNECTION_FAILURE", "VEHICLE_IN_SLEEP", "DELIVERED", "CAR_ERROR", "NOT_ALLOWED_PRIVACY_ENABLED", "NOT_ALLOWED_WRONG_USAGE_MODE",""],
    "brakeLightLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "brakeLightCenterWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "brakeLightRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "fogLightFrontWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "fogLightRearWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "positionLightFrontLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "positionLightFrontRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "positionLightRearLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "positionLightRearRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "highBeamLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "highBeamRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "lowBeamLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "lowBeamRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "daytimeRunningLightLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "daytimeRunningLightRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "turnIndicationFrontLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "turnIndicationFrontRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "turnIndicationRearLeftWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "turnIndicationRearRightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "registrationPlateLightWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "sideMarkLightsWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "hazardLightsWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],
    "reverseLightsWarning": ["UNSPECIFIED", "NO_WARNING", "FAILURE"],

    "lightTimestamp": "", 
    "hornTimestamp": "",
}


class Car(BaseModel):
    VIN: str = Field(...)
    fuelType: str = Field(default="HYBRID") #possible values: PETROL, DIESEL, ELECTRIC, HYBRID
    fuelICE:int = Field(default=0) # fuel level for petrol and diesel cars
    fuelElectric:int = Field(default=0) # fuel level for electric and hybrid cars
    odometer: int = Field(default=0) 
    climate: bool =Field(default=False) # in future time based it can be set to time when the climate will be turned off (why you can set time thru app not thru api. how long api climate lasts? OR only engine has a timer)
    commands:list =Field(default=["CLIMATIZATION_START", "CLIMATIZATION_STOP","ENGINE_START","ENGINE_STOP","FLASH","HONK", "HONK_AND_FLASH","LOCK","UNLOCK"]) # and reduced guard lock but not implemented yet. TO IMPLEMENT
    availabilityStatus_value: str = Field(default="AVAILABLE") # AVAILABLE, UNAVAILABLE, UNSPECIFIED # AVAILABLE is needed for any command TO IMPLEMENT
    availabilityStatus_unavailableReason: str = Field(default="") # Description of why the vehicle is unavailable UNSPECIFIED, NO_INTERNET, POWER_SAVING_MODE, CAR_IN_USE
    engineStatus:str = Field(default="STOPPED") # possible values: STOPPED, RUNNING
    engineTime:int = Field(default=0) # TODO:how long should engine run in future time based (one variable that is time when engine will be turned off not (enginestatus and enginetime))
    
    #diagnostic parameters
    engineCoolantLever:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, TOO_LOW.
    oillevel:str = Field(default="NO_WARNING") #Values: UNSPECIFIED, NO_WARNING, SERVICE_REQUIRED, TOO_LOW, TOO_HIGH.
    
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
    
    lastTimestamp:str = Field(default="") #set if not available
    
    
    lightTimestamp:str = Field(default="")#set if light commands is sent
    
    hornTimestamp:str = Field(default="") # set if horn commands is sent

    nextInvoiceStatus:str = Field(default="") # Possible values: RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.
    # running available for climate or engine commands
    
    #additional parameters for error like if you want fail engine start nextInvoice status, last timestamp
    def timestamp(self):
        if self.availabilityStatus_value == "AVAILABLE":
            self.lastTimestamp = timestampGenerator()
        return self.lastTimestamp
            
    
    
    def checkValidity(self,attribute,value):
        if startUp["Validation"] == False:
            return True
        
        if attribute in options:
            valid = options[attribute]
            if valid == "":
                return True
            if valid == "int":
                value=int(value) #check if value is int todo
                return True
            if value not in valid:
                return False
        return True
    
    #TODO: invoices are difrent for locks 
    def InvoiceStatus(self, command, status=None): #status true turning ON false turning off TODO update climate and engine becouse know its not working for climate stop and engine stop
        if self.nextInvoiceStatus == "":
            if self.availabilityStatus_value == "UNAVAILABLE":
                if self.availabilityStatus_unavailableReason == "NO_INTERNET":
                    return ["CONNECTION_FAILURE",False]
                elif self.availabilityStatus_unavailableReason == "POWER_SAVING_MODE":
                    return ["VEHICLE_IN_SLEEP",False]
                elif self.availabilityStatus_unavailableReason == "CAR_IN_USE":
                    return ["NOT_ALLOWED_WRONG_USAGE_MODE",False]
                return ["UNKNOWN",False]
                
            if command == "climate":
                if self.climate == True and status == True:
                    return ["RUNNING",True]
            elif command == "engine":
                if self.engineStatus == "RUNNING" and status == True:
                    return ["RUNNING",True]
            elif command == "UNLOCK":
                return ["WAITING",True]
                    
            return ["COMPLETED",True]
        
        if self.nextInvoiceStatus == "RUNNING":
            if command == "locks":
                return ["COMPLETED",True]
            elif command == "lights":
                return ["COMPLETED",True]
            elif command == "UNLOCK":
                return ["WAITING",True]
                
        if self.nextInvoiceStatus == "REJECTED" or self.nextInvoiceStatus == "UNKNOWN" or self.nextInvoiceStatus == "TIMEOUT" or self.nextInvoiceStatus == "CONNECTION_FAILURE" or self.nextInvoiceStatus == "VEHICLE_IN_SLEEP" or self.nextInvoiceStatus == "CAR_ERROR" or self.nextInvoiceStatus == "NOT_ALLOWED_PRIVACY_ENABLED" or self.nextInvoiceStatus == "NOT_ALLOWED_WRONG_USAGE_MODE":
            return [self.nextInvoiceStatus,False]
        return [self.nextInvoiceStatus,True]

    def update(self,attribute,value):
        if self.checkValidity(attribute,value):
                if startUp["Validation"] == True:
                    if attribute=="fuelElectric":
                        value=int(value)
                        if value>100:
                            value=100
                        elif value<0:
                            value=0
                    if attribute=="fuelICE" or attribute=="odometer":
                        value=int(value)
                        if value<0:
                            value=0
                setattr(self, attribute, value)
                notifier.trigger_update(self.VIN, self, changed_attribute=attribute)
                self.updated()
                # additional coditions for last timestamp and next invoice status if needed
        else:
            return False
        return True
    
    def updated(self):
        self.lastTimestamp = timestampGenerator()

        
        

def timestampGenerator():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')

