import pytest
import copy

import sys
from pathlib import Path

#AI CODE
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    
#AI CODE END

import database 
import snapshots 
from classCar import Car, config 
from notifier import notifier 



database.database["TEST_NO_OAUTH"] = [Car(VIN="12345678901234567"),Car(VIN="09876543210987654")]

database.database["TEST_OAUTH"] = [Car(VIN="12345678901234567")]
database.AdditionalDatabase["TEST_OAUTH"] = database.AdditionalData(Oauth2Data=database.Oauth2(client_secret="client_secret", code="code", access_token="access_token", refresh_token="refresh_token",code_challenge_method="plain",code_challenge="code_challenge"))

database_backup = copy.deepcopy(database.database)
additional_data_backup = copy.deepcopy(database.AdditionalDatabase)
# snapshots_backup = copy.deepcopy(snapshots.snapshotsData)
# config_backup = copy.deepcopy(config)

@pytest.fixture(autouse=True)
def Reset():
    database.database.clear()
    database.database.update(copy.deepcopy(database_backup))
    database.AdditionalDatabase.clear()
    database.AdditionalDatabase.update(copy.deepcopy(additional_data_backup))
    # snapshots.snapshotsData.clear()
    # snapshots.snapshotsData.update(copy.deepcopy(snapshots_backup))
    # config.clear()
    # config.update(copy.deepcopy(config_backup))
    
