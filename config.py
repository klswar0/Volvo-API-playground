
import configparser
import os


def readConfig(section, option, boolean=False):
    if boolean:
        return config.getboolean(section, option)
    return config.get(section, option)

config = configparser.ConfigParser()
config['DEFAULT'] = {
    'fastAPIdocs': 'True',
    'ShortKeys': 'True',
    'Validation': 'True',
    'expirity': 'True',
    'Websocket': 'True',
    'scopeWarning': 'True',
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
config['DATABASE'] = {
    'TYPE': 'DICT',
    'SQL_TYPE': '',
    'HOST': 'localhost',
    'PORT': '3306',
    'USER': 'test',
    'PASSWORD': '1234',
    'NAME': 'api',
    'DEBUG': 'True',
    'Purge': 'True',
    'ALWAYS_REFRESH': 'False'
    
}
if os.path.exists("config.ini"):
    config.read('config.ini')

all_options=['DEFAULT']+config.sections()
for section in all_options:
    for option in config[section].keys():
        envName=f"{section}_{option}".upper()
        if envName in os.environ:
            config.set(section, option, os.environ[envName])
            

# startUp={
#     "Public": True,
#     "Validation": True,
#     "Dashboard": True,
#     "Websocket": True,
#     "statusNotification": "ALL" # possible values: SET-data is change, ALL- all debug info, VOLVO-only volvo api changes (chaning this  to VOLVO could breake the dashboard and websocket)
# }
