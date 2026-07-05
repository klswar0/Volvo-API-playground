# Volvo playground docs
You can use official docs for every endpoint that isnt /internal/* but you can use this docs to learn how volvo apis work (CONNECTED VEHICLE API other APIs are in works)
## Playground APIs
### '/internal/APIKey'
This GET endpoint creates a new API key 
### '/internal/addCar'
This GET endpoint creates a new Car.
Header:
- ***vcc-api-key*** the api key created or the ready scenario key
Body:
- ***VIN*** string (it should't be a real vin for privacy reasons)
- ***attributes*** a list of attributes (door status, engine status...) to be change. Can be empty
- ***values*** a list if values of changed attibutes (it is not validated so your values could be not corect)

info: attribute and values lenght should be the same

## official endpoints:
### Reused terms
#### auth header
- ***Content-Type*** always application/json
- ***authorization*** access token generated thru Oauth. Not checked in this playground if disabled Oauth2
- ***vcc-api-key*** your api key (dont use your official api key in this playground for safety)
### List vehicles
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