# Volvo-API-playground
This projects aims to provide dynamic alternative to official volvo API sandbox giving developers ways to test every possibility.

>[!WARNING]
>This project is still a work in progress, but it is already in a good state. If you don’t rely on comprehensive documentation, you should find it useful for developing applications for Volvo Connected Vehicles.

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
- Only one api and Oauth endpoints. More comming in future

# Contributions
When contributing to this project, please keep in mind that it was created for the Hack Club YSWS Stardance event. Contributions that align with the project’s goals and maintain its quality are greatly appreciated even if you don't take part in that event.