# What is done:

legend:
- fully working 1:1 volvo API: ✅
- working:🆗
- doesnt work:❎
- static:⏸️
- not implemented:❌
- real life testing needed:🌍
- rework needed:🛑

## before first ship:

| endpoints  | status | comments |
|:----------:|:------------:|:-----------:|
| climatization-start | 🆗  | 🌍   |
| climatization-stop | 🆗    | 🌍   |
| commands  | 🆗   |    |
| commands accesability | 🆗   |    |
| engine diagnostic  | 🆗   |  🌍  |
| diagnostics  | 🆗   | 🌍   |
| brake fluid  | 🆗   |  🌍  |
| windows   | 🆗   | 🌍   |
| doors  | 🆗   |  🌍  |
| lock  | 🆗   | 🌍   |
| locks with reduced |  ❌ |    |
| unlock  | 🆗   | 🌍   |
| engine status  | 🆗   | 🌍   |
| engine start  | 🆗   | 🌍   |
| engine stop  | 🆗   | 🌍   |
| fuel  | 🆗   | 🌍   |
| flash  | 🆗   | 🌍   |
| honk  | 🆗  | 🌍   |
| honk and flash  | 🆗   | 🌍   |
| odometer  |  🆗  | 🌍   |
| statistics  |  ⏸️  | 🌍   |
| tyres  | 🆗   | 🌍   |
| vehicles  | ⏸️    | 🌍   |
| get vehicle  | 🆗    | 🌍   |
| get warnigns  | 🆗    | 🌍   |



| additional  | status | comments |
|:----------:|:------------:|:-----------:|
| dashboard | 🆗 | 🌍   |
| Oauth2 | 🆗   | 🌍   |
| example app |   🆗    | 🌍   | companion/compare app
| internal endpoints for testing errors |     | 🌍   |
| scenarios |     | 🌍   |
| snapshots |     | 🌍   |
| docs |     |    |

## after 2 ship...
- Notification system improvements for better real-time updates (more than one updated attribute at the same time).
- update the updates endpoint
- logging solution for error and debug information
- 2 response modes (1:1 volvo API and helpful error messages)
- the rest API (wihout energy device api)