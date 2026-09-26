from fastapi.responses import JSONResponse
from fastapi import Header

from classCar import AuthHeaderGET, ResponseHeaderGenerator
from readyResponses import energyAutoErrorResponse, energyErrorResponseGen
from auth import VINHandling
from scopes import checkScope



def capabilities(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
        checkScope(auth_header.vcc_api_key, ["openid", "energy:capability:read"])
    except ValueError as e:
        return energyAutoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        data = {
            "getEnergyState": {
                "isSupported": car.getEnergyState,
                "batteryChargeLevel": {
                    "isSupported": car.batteryChargeLevel
                },
                "electricRange": {
                    "isSupported": car.electricRange
                },
                "chargerConnectionStatus": {
                    "isSupported": car.chargerConnectionStatus
                },
                "chargingSystemStatus": {
                    "isSupported": car.chargingSystemStatus
                },
                "chargingType": {
                    "isSupported": car.chargingType
                },
                "chargerPowerStatus": {
                    "isSupported": car.chargerPowerStatus
                },
                "estimatedChargingTimeToTargetBatteryChargeLevel": {
                    "isSupported": car.estimatedChargingTimeToTargetBatteryChargeLevel
                },
                "targetBatteryChargeLevel": {
                    "isSupported": car.targetBatteryChargeLevel
                },
                "chargingCurrentLimit": {
                    "isSupported": car.chargingCurrentLimit
                },
                "chargingPower": {
                    "isSupported": car.chargingPower
                }
            }
        }
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))
    
def batterySectionGen(capability, value, timestamp, unit=None):
    if capability is False:
        return {
                "status": "ERROR",
                "code": "PROPERTY_NOT_FOUND",
                "message": "No valid value could be found for the requested property"
            }
    if unit is None:
        return {
            "status": "OK",
            "value": value,
            "updatedAt": timestamp
        }
    return {
        "status": "OK",
        "value": value,
        "unit": unit,
        "updatedAt": timestamp
    }
    

def energyState(VIN:str, auth_header: AuthHeaderGET = Header(...)):
    try:
        car = VINHandling(VIN, auth_header)
        checkScope(auth_header.vcc_api_key, ["openid", "energy:state:read"])
        if not car.getEnergyState:
            return energyErrorResponseGen("RESOURCE_NOT_SUPPORTED", "Energy state not supported", ResponseHeaderGenerator(auth_header), status_code=404)
    except ValueError as e:
        return energyAutoErrorResponse(e, VIN,ResponseHeaderGenerator(auth_header))
    else:
        timeStamp = car.timestamp()
        data = {}
        # check if the car doesnt have capabilitie its removed from the response . there IS a error response for property not found
        data["batteryChargeLevel"] = batterySectionGen(car.batteryChargeLevel,car.fuelElectric, timeStamp, "percentage")
        
        data["electricRange"] = batterySectionGen(car.electricRange,car.electricRangeValue, timeStamp, "km")

        data["chargerConnectionStatus"] = batterySectionGen(car.chargerConnectionStatus,car.chargerConnectionStatusValue, timeStamp)

        data["chargingStatus"] = batterySectionGen(car.chargingSystemStatus,car.chargingStatusValue, timeStamp)

        data["chargingType"] = batterySectionGen(car.chargingType,car.chargingTypeValue, timeStamp)

        data["chargerPowerStatus"] = batterySectionGen(car.chargerPowerStatus,car.chargerPowerStatusValue,  timeStamp)

        data["estimatedChargingTimeToTargetBatteryChargeLevel"] = batterySectionGen(car.estimatedChargingTimeToTargetBatteryChargeLevel,car.estimatedChargingTimeToTargetBatteryChargeLevelValue, timeStamp, "minutes")

        data["chargingCurrentLimit"] = batterySectionGen(car.chargingCurrentLimit,car.chargingCurrentLimitValue, timeStamp, "ampere")

        data["targetBatteryChargeLevel"] = batterySectionGen(car.targetBatteryChargeLevel,car.targetBatteryChargeLevelValue, timeStamp, "percentage")

        data["chargingPower"] = batterySectionGen(car.chargingPower,car.chargingPowerValue, timeStamp, "watts")
            
    
        # data = {
        #     "batteryChargeLevel": {
        #         "status": "OK",
        #         "value": car.fuelElectric,
        #         "unit": "percentage",
        #         "updatedAt": timeStamp
        #     },
        #     "electricRange": {
        #         "status": "OK",
        #         "value": 180,
        #         "unit": "km",
        #         "updatedAt": timeStamp
        #     },
        #     "chargerConnectionStatus": {
        #         "status": "OK",
        #         "value": "CONNECTED",
        #         "updatedAt": timeStamp
        #     },
        #     "chargingStatus": {
        #         "status": "OK",
        #         "value": "IDLE",
        #         "updatedAt": timeStamp
        #     },
        #     "chargingType": {
        #         "status": "OK",
        #         "value": "AC",
        #         "updatedAt": timeStamp
        #     },
        #     "chargerPowerStatus": {
        #         "status": "OK",
        #         "value": "PROVIDING_POWER",
        #         "updatedAt": timeStamp
        #     },
        #     "estimatedChargingTimeToTargetBatteryChargeLevel": {
        #         "status": "OK",
        #         "value": 120,
        #         "unit": "minutes",
        #         "updatedAt": timeStamp
        #     },
        #     "chargingCurrentLimit": {
        #         "status": "OK",
        #         "value": 32,
        #         "unit": "ampere",
        #         "updatedAt": timeStamp
        #     },
        #     "targetBatteryChargeLevel": {
        #         "status": "OK",
        #         "value": 85,
        #         "unit": "percentage",
        #         "updatedAt": timeStamp
        #     },
        #     "chargingPower": {
        #         "status": "OK",
        #         "value": 8000,
        #         "unit": "watts",
        #         "updatedAt": timeStamp
        #     }
        # }
        
        return JSONResponse(content=data, status_code=200, headers=ResponseHeaderGenerator(auth_header))

