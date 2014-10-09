import json
import os

def saveNewSetup(setup_name, setupIPaddr, pumpIPaddr, phidget_webservice_listen_port=5001, pump_channels=["01", "02"], pump_telnet_listen_port=100):
    if os.path.exists(os.path.expanduser("~/.pumpr/config.json")):

        with open(os.path.expanduser("~/.pumpr/config.json")) as configfile:
            configdict = json.load(configfile)

        configdict["setups"][setup_name] = {
            "setupIPaddr": setupIPaddr,
            "pumpIPaddr": pumpIPaddr,
            "phidget_webservice_listen_port": phidget_webservice_listen_port,
            "pump_channels": pump_channels,
            "pump_telnet_listen_port": pump_telnet_listen_port
        }
        with open(os.path.expanduser("~/.pumpr/config.json"), "w") as newconfigfile:
            json.dump(configdict, newconfigfile, sort_keys=True, indent=4, ensure_ascii=True)

    #TODO eliminate potential race conditions in else clause http://stackoverflow.com/questions/273192/check-if-a-directory-exists-and-create-it-if-necessary
    else:
        configdict = {
            "setups": {
                setup_name: {
                    "setupIPaddr": setupIPaddr,
                    "pumpIPaddr": pumpIPaddr,
                    "phidget_webservice_listen_port": phidget_webservice_listen_port,
                    "pump_channels": pump_channels,
                    "pump_telnet_listen_port": pump_telnet_listen_port
                }
            }
        }

        if os.path.isdir(os.path.expanduser("~/.pumpr")):
            with open(os.path.expanduser("~/.pumpr/config.json"), "w") as newconfigfile:
                json.dump(configdict, newconfigfile, sort_keys=True, indent=4, ensure_ascii=True)
        else:
            os.makedirs(os.path.expanduser("~/.pumpr"))
            with open(os.path.expanduser("~/.pumpr/config.json"), "w") as newconfigfile:
                json.dump(configdict, newconfigfile, sort_keys=True, indent=4, ensure_ascii=True)

def deleteSetup(setup_name):
    if os.path.exists(os.path.expanduser("~/.pumpr/config.json")):

        with open(os.path.expanduser("~/.pumpr/config.json")) as configfile:
            configdict = json.load(configfile)

        try:
            del configdict["setups"][setup_name]
        except KeyError:
            pass

        with open(os.path.expanduser("~/.pumpr/config.json"), "w") as newconfigfile:
            json.dump(configdict, newconfigfile, sort_keys=True, indent=4, ensure_ascii=True)

def updateSetupField(setup_name, field_to_update, new_value):
    if os.path.exists(os.path.expanduser("~/.pumpr/config.json")):

        with open(os.path.expanduser("~/.pumpr/config.json")) as configfile:
            configdict = json.load(configfile)

        try:
            setup_config = configdict["setups"][setup_name]
        except KeyError:
            return False, setup_name + " does not exist"
        else:
            try:
                tmp = setup_config[field_to_update]
            except KeyError:
                return False, field_to_update + " does not exist"
            else:
                configdict["setups"][setup_name][field_to_update] = new_value
                with open(os.path.expanduser("~/.pumpr/config.json"), "w") as newconfigfile:
                    json.dump(configdict, newconfigfile, sort_keys=True, indent=4, ensure_ascii=True)
                return True, None

def getSetupInfoFromConfig():
    if os.path.exists(os.path.expanduser("~/.pumpr/config.json")):
        with open(os.path.expanduser("~/.pumpr/config.json")) as configfile:
            configdict = json.load(configfile)
            return configdict

if __name__ == "__main__":
    '''
    saveNewSetup("travis", "10.251.103.11", "10.0.254.254")

    saveNewSetup("joe", "10.251.103.12", "10.0.254.254")
    deleteSetup("joe") #shouldnt see Joe in config, he was deleted

    ok, error = updateSetupField("travis", "setupIPaddr", "10.251.103.12")
    if not ok:
        print error
    ok, error = updateSetupField("ben", "setupIPaddr", "10.251.103.12")
    if ok:
        print "Houston, we have an error"
    ok, error = updateSetupField("travis", "doesnotexist", "cool string")
    if ok:
        print "Something is srsly wrong"
    '''
