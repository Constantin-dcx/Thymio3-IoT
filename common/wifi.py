import network

# WiFi Credentials, in order of priority
wifi_credentials = [
    {"ssid": "Constantin_AP_2.4G", "password": "mobots1234"},
    # {"ssid": "my ssid 2", "password": "my password 2"},
]

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    available_ssids = {ssid.decode('utf-8'): bssid for ssid, bssid, *_ in networks}
    
    for ssid_info in wifi_credentials:
        ssid = ssid_info["ssid"]
        if ssid in available_ssids:
            print(f'Connecting to WiFi network "{ssid}"...')
            wlan.connect(ssid, ssid_info["password"])
            while wlan.ifconfig()[0] == '0.0.0.0':
                pass
            print(f'Successfully connected to WiFi network "{ssid}".')
            return True
        else:
            print(f'WiFi network "{ssid}" is not available.')
    
    return False