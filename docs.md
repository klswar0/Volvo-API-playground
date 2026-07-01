# Volvo playground docs
You can use official docs for every endpoint that isnt /internal/* but you can use this docs to learn how volvo apis work (CONNECTED VEHICLE API other APIs are in works)
## official endpoints:
### Reused terms
#### auth header
- ***Content-Type*** always application/json
- ***authorization*** token generated thru Oauth NOT IMPLEMENTED yet in playground
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