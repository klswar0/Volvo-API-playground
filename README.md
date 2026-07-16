![VOLVO API Playgroound baner](Baner.png)

# Volvo-API-playground
This projects aims to provide dynamic alternative to official volvo API sandbox giving developers ways to test every possibility.

> [!WARNING]
> This project is still a work in progress, but it is already in a good state. If you don’t rely on comprehensive documentation, you should find it useful for developing applications for Volvo Connected Vehicles.

## Key features:
- Car that reacts to commands
- Interactive Dashboard
- Additional APIs endpoints for faster manipulating states and forcing errors
- Simplified Oauth 2.0 with PKCE to test your app if it is ready for real API

## Roadmap
- Scenarios and snapshots system (WIP)
- More error testing
- Persistent storage
- Energy and location API



## How to run:
Download the repository.
Packages: fastapi uvicorn pydantic jinja2 websockets:
`uv add fastapi uvicorn pydantic jinja2 websockets`
then:
`uv run main.py`

### Want to try it out?
You can explore the public instance here:
[Public instance](https://playground.kls.hackclub.app/internal/welcome)

> [!TIP]
> Are you not sure?
> You can check the diffrences in the companion app: PLACEHOLDER


## Limitations:
- One API key per user. This means one refresh token, one access token, and so on. Because of this, the project cannot accurately reproduce real-world scenarios involving multiple users.(Could be comming in future but it would require using real database)
- No expiration of access token (TODO)
- Only one api and Oauth endpoints. More coming in future

# Contributions
When contributing to this project, please keep in mind that it was created for the Hack Club YSWS Stardance event. Contributions that align with the project’s goals and maintain its quality are greatly appreciated even if you don't take part in that event.