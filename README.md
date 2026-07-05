# Volvo-API-playground
This projects aims to provide dynamic alternative to official volvo API sandbox giving developers ways to test every possibility.

> [!WARNING]
> This projects is at very early state that is worse than the official sandbox come back later


## Roadmap
- Virtual car reacts to commands send to API
- Dashboard to see how car reacts to commands
- additional APIs to force errors and state change 
- Working Authorisation code flow with oauth2

check ROADMAP.md file in this repositorium for more info about status of this project


## How to run:
packages: uvicorn, fastapi
then:
`uv run main.py`


## Limitions:
- One API key per user. This means one refresh token, one access token, and so on. Because of this, the project cannot accurately reproduce real-world scenarios involving multiple users.(Could be comming in future but it would require using real database)
- No expiration of access token (TODO)
- Only one api and Oauth endpoints