# Volvo playground docs
You can use official docs for every endpoint that isnt /internal/* but you can use this docs to learn how volvo apis work (CONNECTED VEHICLE API other APIs are in works)
## Playground APIs

### /internal/APIKey
This GET endpoint creates a new API key 

### /internal/addCar
This POST endpoint creates a new Car.
Header:
- ***vcc-api-key*** the api key created or the ready scenario key
Body:
- ***VIN*** string (it should't be a real vin for privacy reasons)
- ***attributes*** a list of attributes (door status, engine status...) to be change. Can be empty
- ***values*** a list if values of changed attibutes (it is not validated so your values could be not correct)

info: attribute and values lenght should be the same

### /internal/update
This POST endpoint updates a specific car attributes.
Header:
- ***vcc-api-key*** the api key created or the ready scenario key
Body:
- ***VIN*** string (it should't be a real vin for privacy reasons)
- ***attributes*** a list of attributes (door status, engine status...) to be change. 
- ***values*** a list if values of changed attibutes (it is validated. It means that only valid values for that attributes are updated)

info:need to fix updates and this enpoints so doesnt call notifier 2 times

### /internal/ws
Websocket on start sends all data about the car then sends data only of changed attributes.
Query:
- ***VIN*** VIN of virtual vehicle you want to monitor
- ***key*** api key

### /internal/status
This GET endpoint  all data about the car.
Header:
- ***VIN*** VIN of virtual vehicle you want to monitor
- ***key*** api key

### /internal/oauth2
This GET endpoint sends all information about Oauth2 settings
header:
- ***vcc_api_key*** api key with enabled Oauth2
```
{
  "client_secret": <str>,
  "code": <str>,
  "access_token": <str>,
  "refresh_token": <str>,
  "token_type": <str>,
  "expires_in": 3599, # doesn't change and doesnt work
  "redirect_uri": <str> # if nothing then all redirects are alowed. This examptions is made for testing and doesnt exist in volvo api
}
```

### /internal/oauth2/deactivate
This POST endpoint disable Oauth2 flow for provided API key
header:
- ***vcc_api_key*** api key with enabled Oauth2
```
{
  "message": "OAuth2 deactivated successfully"
}
```

### /internal/oauth2/regenerate
This POST endpoint creates new access and refresh tokens
header:
- ***vcc_api_key*** api key with enabled Oauth2
```
{
  "access_token": <str>,
  "refresh_token": <str>,
  "token_type": "Bearer", #static
  "expires_in": 3599 #static
}
```

### /internal/oauth2/activate
This POST endpoint activate Oauth2 flow for provided API key
header:
- ***vcc_api_key*** api key with enabled Oauth2
body:
```
{
  "client_secret": <str>,
  "PCKE": <bool>,
  "redirect_uri": <str/optional>
}
```
```
{
    "message": "OAuth2 activated successfully"
}
```

### Errors
If an error is returned and it is not caused by missing data, the response will have the following format:
```
{ "error": {"message": "THIS IS INTERNAL API/<Error text>","description": <error description>"}}
```


## Playground sites:

### '/internal/terminal'
Shows what the websocket sends.
Query:
- ***VIN*** VIN of virtual vehicle you want to monitor
- ***key*** api key

### '/internal/welcome'
This site give you away to generate or login with api key.
Then give away to select a car and modifier data.
It redirects to the rest of the pages.




## official endpoints:

Errors catched in official docs and specification.
docs are outdated (more than one diffrences between specification)
specification dont says responses are in {data: <what specification says>} 

### Error responses
Error responses could not be the same as in official API. Could be more informative or less informative. This project is WORK IN PROGRESS in the future it could change.
### Reused terms
### Timestamp
Timestamp in ISO-8601 format ~~when the value has been last retrieved from the vehicle~~ in this plaground the current time or if car is unavailble then the time when car is set to that.

### invoke Status
Possible values:
RUNNING, WAITING, COMPLETED, REJECTED, UNKNOWN, TIMEOUT, CONNECTION_FAILURE, VEHICLE_IN_SLEEP, DELIVERED, CAR_ERROR, NOT_ALLOWED_PRIVACY_ENABLED, NOT_ALLOWED_WRONG_USAGE_MODE.

Exception: RUNNING for sure can only go to engine and climate endpoints


#### auth header
- ***Content-Type*** always application/json
- ***authorization*** access token generated thru Oauth. Not checked in this playground if disabled Oauth2
- ***vcc-api-key*** your api key (dont use your official api key in this playground for safety)

### INFO:
 ~~The official Volvo Connected Vehicle API rejects requests with Content-Type: application/json;charset=UTF-8 for some endpoints and only accepts Content-Type: application/json. This behavior will be  replicated by the playground for compatibility.~~ More diging needed

### List vehicles
/vehicles
This endpoints sends all cars VINs.
It only needs ***auth header***
```
{
  "data": [
    {
      "vin": "VIN123"
    },
    {
      "vin": "VIN321"
    }
  ]
}
```

### Get vehicle information
/vehicles/{VIN}
This endpoints send information about the car.
It needs ***auth header*** and VIN
```
{
  "data": {
    "vin": <str>,
    "modelYear": <int>,
    "gearbox": "AUTOMATIC", #static data
    "fuelType": <str>,
    "externalColour": "SAVILE GREY STATIC", #static data
    "batteryCapacityKWH": 78, #static data
    "images": {
      "exteriorImageUrl": "link-to-exterior-image", #static data
      "internalImageUrl": "link-to-internal-image" #static data
    },
    "descriptions": {
      "model": "V60 II STATIC", #static data
      "upholstery": "CHARCOAL/LEAC/CHARC STATIC", #static data
      "steering": "LEFT STATIC" #static data
    }
  }
}
```
legend:
- fuelType: HYBRID, ELECTRIC, DIESEL, PETROL

info: mostly static in playground but in future you will be able to change the static data

### engine status
/vehicles/{VIN}/engine-status
Vehicle's latest engine status value.
It needs ***auth header*** and VIN (PATH)
TODO: check with volvo specification why there is unit????
```
{
  "data": {
    "engineStatus": {
      "value": <str>,
      "timestamp": "2026-07-06T20:32:17.170Z"
    }
  }
}
```
legend:
- value: RUNNING or STOPPED

### engine start
/vehicles/{VIN}/commands/engine-start
Starts the engine.
It needs ***auth header*** and VIN (PATH)
Body: {runtimeMinutes: <int>} (range from 1-15)

```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": "" # realy dont know what to put here
  }
}
```
legend:
- invokeStatus read reused terms

### engine stop
/vehicles/{VIN}/commands/engine-stop
Stops the engine.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": "" # realy dont know what to put here
  }
}
```



## Climate start
/vehicles/{VIN}/commands/climate-start
Starts the climate.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": "" # realy dont know what to put here
  }
}
```


## Climate stop
/vehicles/{VIN}/commands/climate-stop
Stops the climate.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": "" # realy dont know what to put here
  }
}
```

## Windows Status
/vehicles/{VIN}/windows-status
Status of the windows.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "windowsStatus": {
      "value": <str>,
      "timestamp": "2026-07-06T20:32:17.170Z"
    }
  }
}
```
## Doors Status
/vehicles/{VIN}/doors-status
Status of the doors and locks.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "centralLock": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "frontLeftDoor": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "frontRightDoor": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "hood": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "rearLeftDoor": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "rearRightDoor": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "tailGate": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    },
    "tankLid": {
      "value": <str>,
      "timestamp": "2026-07-21T12:48:31.896Z"
    }
  }
}
```
legend:
- value (cental lock): LOCKED, UNLOCKED, UNSPECIFIED
- value (doors): CLOSED, OPEN, AJAR, UNSPECIFIED






## locking the car
/vehicles/{VIN}/commands/lock
Locks the car.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": <str> 
  }
}
```



## locking the car (reduced)
**DISABLED** Manual support can be enabled (work like lock) 
/vehicles/{VIN}/commands/lock-reduced-guard
Locks the car.
It needs ***auth header*** and VIN (PATH)
```
PLACEHOLDER
```

## Unlocking the car
/vehicles/{VIN}/commands/unlock
Unlocks the car.
It needs ***auth header*** and VIN (PATH)
```
{
  "vin": <str>,
  "invokeStatus": <str>,
  "message": <str>,
  "readyToUnlock": True,
  "readyToUnlockUntil": 5,
  "details": "Not fully implemented manual button press needed in real life" #added as warning
}
```

## flashing the lights
/vehicles/{VIN}/commands/flash-lights
Flashes the lights.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": <str>
  }
}
```

## horn
/vehicles/{VIN}/commands/horn
Sounds the horn.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": <str>
  }
}
```

## horn and flash lights
/vehicles/{VIN}/commands/horn-and-flash
Sounds the horn and flashes the lights.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "vin": <str>,
    "invokeStatus": <str>,
    "message": <str>
  }
}
```

## statistics
**STATIC**
/vehicles/{VIN}/statistics
Statistics of the car.
It needs ***auth header*** and VIN (PATH)
```{
  "data": {
    "averageFuelConsumption": {
      "value": 7.2374,
      "unit": "l/100km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "averageEnergyConsumption": {
      "value": 7.2374,
      "unit": "kWh/100km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "averageFuelConsumptionAutomatic": {
      "value": 7.4732,
      "unit": "l/100km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "averageEnergyConsumptionAutomatic": {
      "value": 7.4732,
      "unit": "kWh/100km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "averageEnergyConsumptionSinceCharge": {
      "value": 7.4732,
      "unit": "kWh/100km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "averageSpeed": {
      "value": 50,
      "unit": "km/h",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "averageSpeedAutomatic": {
      "value": 66,
      "unit": "km/h",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "tripMeterManual": {
      "value": 500,
      "unit": "km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "tripMeterAutomatic": {
      "value": 420,
      "unit": "km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "distanceToEmptyTank": {
      "value": 1312,
      "unit": "km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    },
    "distanceToEmptyBattery": {
      "value": 312,
      "unit": "km",
      "timestamp": "2026-07-21T12:58:33.226Z"
    }
  }
}
```

## tyres
/vehicles/{VIN}/tyres
Status of tyres.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "frontLeft": {
      "value":  <str>,
      "timestamp": "2026-07-22T11:34:06.553Z"
    },
    "frontRight": {
      "value": <str>,
      "timestamp": "2026-07-22T11:34:06.553Z"
    },
    "rearLeft": {
      "value": <str>,
      "timestamp": "2026-07-22T11:34:06.553Z"
    },
    "rearRight": {
      "value": <str>,
      "timestamp": "2026-07-22T11:34:06.553Z"
    }
  }
}
```
legend:
- value: UNSPECIFIED, NO_WARNING, VERY_LOW_PRESSURE, LOW_PRESSURE, HIGH_PRESSURE.

## fuel
/vehicles/{VIN}/fuel
Status of fuel.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "fuelAmount": {
      "value": <int>, # 0-inf
      "unit": "l",
      "timestamp": "2026-07-22T11:35:44.174Z"
    },
    "batteryChargeLevel": {
      "value": <int>, # 0-100
      "unit": "%",
      "timestamp": "2026-07-22T11:35:44.174Z"
    }
  }
}
```
INFO: if car is electric then the fuel Amount isnt sent and if the car is petrol/diesel then the batteryChargeLevel isnt sent. If the car is hybrid then both are sent.



## odometer
/vehicles/{VIN}/odometer
Status of odometer.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "odometer": {
      "value": 0, # 0-inf
      "unit": "km",
      "timestamp": "2026-07-22T11:37:42.485Z"
    }
  }
}
```

## engine
/vehicles/{VIN}/engine
diagnostics of engine.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "engineCoolantLevelWarning": {
      "value": <str>,
      "timestamp": "2026-07-22T11:38:59.340Z"
    },
    "oilLevelWarning": {
      "value": <str>,
      "timestamp": "2026-07-22T11:38:59.340Z"
    }
  }
}
```
values: UNSPECIFIED, NO_WARNING, TOO_LOW

## diagnostics
/vehicles/{VIN}/diagnostics
diagnostics of the car.
It needs ***auth header*** and VIN (PATH) 
**checks needed**

## brakes
/vehicles/{VIN}/brakes
diagnostics of brake fluid.
It needs ***auth header*** and VIN (PATH)
```
{
  "data": {
    "brakeFluidLevelWarning": {
      "value": "<str>",
      "timestamp": "2026-07-22T11:43:11.924Z"
    }
  }
}
```
legend:
values: UNSPECIFIED, NO_WARNING, TOO_LOW

## warnings
/vehicles/{VIN}/warnings
Shows a lot of warnings for the lights
It needs ***auth header*** and VIN (PATH)
**classic cars different from new cars. Need to check with volvo specification**
Some data will diffrent from car to car.

## commands
/vehicles/{VIN}/commands
List of commands available for the car.
It needs ***auth header*** and VIN (PATH)

## command accessability
/vehicles/{VIN}/commands-accessibility
Returns if the car is able to execute commands.
It needs ***auth header*** and VIN (PATH)