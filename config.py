
import configparser


def readConfig(section, option, boolean=False):
    if boolean:
        return config.getboolean(section, option)
    return config.get(section, option)

config = configparser.ConfigParser()
config['DEFAULT'] = {
    'ShortKeys': 'True',
    'Validation': 'True',
    'expirity': 'True',
    'Websocket': 'True',
    'statusNotification': 'ALL' # FIX planned when new error logger+notification system /possible values: SET-data is change, ALL- all debug info, VOLVO-only volvo api changes (chaning this  to VOLVO could breake the dashboard and websocket)
}
config['SITE'] = {
    'Public': 'True',
    'Dashboard': 'True',
    'Note': ''
}
config['ERROR_LOGGING'] = {
    'STATUS': 'True',
    'Write': 'True'
}
config.read('config.ini')

# startUp={
#     "Public": True,
#     "Validation": True,
#     "Dashboard": True,
#     "Websocket": True,
#     "statusNotification": "ALL" # possible values: SET-data is change, ALL- all debug info, VOLVO-only volvo api changes (chaning this  to VOLVO could breake the dashboard and websocket)
# }
