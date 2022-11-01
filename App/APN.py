from .SQL import SQL

apn_keys_list = ['friendly_apn_mms_name', 'url_mms_center', 'ip_mms_proxy', 'port_mms_proxy', 'apn_name']

def apn_configured_check():
    for key in apn_keys_list:
        if not SQL.Get(key):
            return False
    return True


def get_apn_data():
    data = {}
    for key in apn_keys_list:
        data[key] = SQL.Get(key)
    return data
