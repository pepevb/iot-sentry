"""
IoT Sentry - Identificador COMPLETO de Dispositivos

Detecta TODOS los tipos posibles de dispositivos conectados a red
"""

import os
import re
from typing import Optional, Dict


class ComprehensiveDeviceIdentifier:
    """Identificador exhaustivo de dispositivos de red"""

    def __init__(self, oui_file: Optional[str] = None):
        if oui_file is None:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            oui_file = os.path.join(project_root, 'shared', 'databases', 'oui.txt')

        self.oui_file = oui_file
        self.oui_cache = {}
        self._load_oui_database()

        # MEGA MAPA de fabricantes a tipos (EXHAUSTIVO)
        self.vendor_patterns = {
            # ========== DISPOSITIVOS PERSONALES ==========
            'smartphone': [
                'Apple', 'Samsung', 'Huawei', 'Xiaomi', 'OnePlus', 'Oppo', 'Vivo',
                'Motorola', 'Nokia', 'Sony Mobile', 'LG Electronics', 'Google',
                'HTC', 'Asus', 'ZTE', 'Lenovo', 'Realme', 'Meizu', 'BlackBerry'
            ],

            'computer': [
                'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'MSI', 'Toshiba',
                'Intel Corporate', 'ASUSTek', 'Hewlett Packard', 'Apple',
                'Microsoft', 'Razer', 'Alienware', 'System76', 'Framework'
            ],

            'tablet': [
                'Apple iPad', 'Samsung Galaxy Tab', 'Amazon', 'Microsoft Surface',
                'Lenovo Tab', 'Huawei MatePad'
            ],

            'wearable': [
                'Fitbit', 'Garmin', 'Fossil', 'Withings', 'Amazfit', 'Samsung Galaxy',
                'Apple Watch', 'Xiaomi Mi Band', 'Polar', 'Suunto', 'Casio'
            ],

            'e_reader': [
                'Amazon Kindle', 'Kobo', 'Barnes Noble', 'reMarkable', 'Onyx'
            ],

            # ========== IOT SEGURIDAD Y MONITOREO ==========
            'security_camera': [
                'Wyze', 'Ring', 'Arlo', 'Nest', 'Blink', 'Reolink', 'Amcrest',
                'Hikvision', 'Dahua', 'Axis', 'Vivotek', 'Foscam', 'Yi',
                'Eufy', 'Lorex', 'Swann', 'Annke', 'Zmodo', 'Reolink'
            ],

            'doorbell': [
                'Ring', 'Nest Hello', 'Arlo', 'Eufy', 'Wyze', 'SimpliSafe',
                'Remo+', 'SkyBell', 'August'
            ],

            'security_system': [
                'SimpliSafe', 'ADT', 'Ring Alarm', 'Abode', 'Vivint', 'Scout',
                'Cove', 'Frontpoint', 'Link Interactive'
            ],

            'baby_monitor': [
                'Nanit', 'Owlet', 'Infant Optics', 'Motorola Baby', 'VTech',
                'Arlo Baby', 'Cubo Ai'
            ],

            # ========== IOT ASISTENTES Y AUDIO ==========
            'smart_speaker': [
                'Amazon', 'Google', 'Apple', 'Sonos', 'Bose', 'Harman',
                'JBL', 'Ultimate Ears', 'Bang Olufsen', 'Denon', 'Yamaha',
                'Polk Audio', 'Marshall', 'Audio Pro'
            ],

            'smart_display': [
                'Amazon Echo Show', 'Google Nest Hub', 'Lenovo Smart Display',
                'Facebook Portal', 'JBL Link View'
            ],

            # ========== IOT ILUMINACIÓN ==========
            'smart_bulb': [
                'Philips Hue', 'LIFX', 'TP-Link', 'Sengled', 'Wyze',
                'GE Lighting', 'Yeelight', 'Nanoleaf', 'Cree', 'Sylvania',
                'Merkury', 'Feit Electric', 'Govee'
            ],

            'led_strip': [
                'Philips Hue', 'LIFX', 'Govee', 'Nanoleaf', 'Yeelight',
                'TP-Link', 'Wyze', 'Monster'
            ],

            # ========== IOT ENCHUFES Y SWITCHES ==========
            'smart_plug': [
                'TP-Link', 'Wemo', 'Kasa', 'Meross', 'Gosund', 'Teckin',
                'Wyze', 'Amazon Smart Plug', 'Eufy', 'VOCOlinc', 'Eve'
            ],

            'smart_switch': [
                'Lutron', 'Leviton', 'TP-Link', 'GE', 'Inovelli', 'Zooz',
                'Enbrighten', 'Treatlife'
            ],

            # ========== IOT CLIMA ==========
            'thermostat': [
                'Nest', 'Ecobee', 'Honeywell', 'Emerson', 'Johnson Controls',
                'Sensi', 'Lux', 'Wyze', 'Cielo', 'Mysa'
            ],

            'air_purifier': [
                'Dyson', 'Philips', 'Levoit', 'Coway', 'Winix', 'Blueair',
                'Molekule', 'Honeywell', 'IQAir'
            ],

            'humidifier': [
                'Levoit', 'Pure Enrichment', 'Honeywell', 'Vicks', 'Dyson',
                'Taotronics', 'Vornado'
            ],

            'fan': [
                'Dyson', 'Vornado', 'Hunter', 'Big Ass Fans', 'Lasko'
            ],

            'air_conditioner': [
                'GE', 'Frigidaire', 'LG', 'Whirlpool', 'Midea', 'Friedrich',
                'Haier', 'Sensibo'
            ],

            # ========== IOT ELECTRODOMÉSTICOS COCINA ==========
            'smart_refrigerator': [
                'Samsung Family Hub', 'LG ThinQ', 'GE Appliances', 'Whirlpool',
                'Bosch', 'Electrolux'
            ],

            'smart_oven': [
                'June', 'Tovala', 'Brava', 'Samsung', 'LG', 'GE',
                'Whirlpool', 'Bosch'
            ],

            'microwave': [
                'Amazon Basics', 'Toshiba', 'Samsung', 'LG', 'GE', 'Whirlpool'
            ],

            'coffee_maker': [
                'Keurig', 'Nespresso', 'Mr Coffee', 'Hamilton Beach',
                'Cuisinart', 'Smarter', 'Atomi'
            ],

            'instant_pot': [
                'Instant Pot', 'Ninja Foodi', 'Crock-Pot'
            ],

            'air_fryer': [
                'Ninja', 'Cosori', 'Philips', 'Instant Pot', 'Nuwave'
            ],

            'dishwasher': [
                'Bosch', 'Miele', 'Samsung', 'LG', 'Whirlpool', 'GE',
                'KitchenAid'
            ],

            # ========== IOT ELECTRODOMÉSTICOS LAVANDERÍA ==========
            'washing_machine': [
                'Samsung', 'LG', 'Whirlpool', 'GE', 'Bosch', 'Electrolux',
                'Maytag', 'Miele', 'Speed Queen'
            ],

            'dryer': [
                'Samsung', 'LG', 'Whirlpool', 'GE', 'Bosch', 'Electrolux',
                'Maytag', 'Miele'
            ],

            # ========== IOT LIMPIEZA ==========
            'robot_vacuum': [
                'iRobot Roomba', 'Roborock', 'Ecovacs', 'Shark', 'Eufy',
                'Neato', 'Wyze', '360', 'Dreame', 'Xiaomi', 'Lefant'
            ],

            'robot_mop': [
                'iRobot Braava', 'Roborock', 'Ecovacs', 'Yeedi', 'Narwal'
            ],

            # ========== IOT JARDÍN ==========
            'sprinkler_system': [
                'Rachio', 'Rain Bird', 'Orbit B-hyve', 'Hunter', 'Netro',
                'RainMachine', 'Wyze'
            ],

            'lawn_mower': [
                'Husqvarna', 'Worx', 'Gardena', 'Honda', 'Robomow',
                'Landroid'
            ],

            'grill': [
                'Weber', 'Traeger', 'Green Mountain', 'Camp Chef', 'Pit Boss'
            ],

            'pool_controller': [
                'Pentair', 'Hayward', 'Zodiac', 'Jandy'
            ],

            # ========== IOT MASCOTAS ==========
            'pet_feeder': [
                'Petnet', 'PetSafe', 'Whisker', 'Cat Mate', 'WOPET'
            ],

            'pet_camera': [
                'Furbo', 'Petcube', 'Wyze', 'Petzi', 'Pawbo'
            ],

            'litter_box': [
                'Litter-Robot', 'PetSafe ScoopFree', 'CatGenie'
            ],

            # ========== ENTRETENIMIENTO ==========
            'smart_tv': [
                'Samsung', 'LG', 'Sony', 'Vizio', 'TCL', 'Hisense', 'Sharp',
                'Panasonic', 'Toshiba', 'Philips', 'Insignia'
            ],

            'streaming_device': [
                'Roku', 'Amazon Fire TV', 'Apple TV', 'Google Chromecast',
                'Nvidia Shield', 'TiVo', 'Xiaomi Mi Box'
            ],

            'game_console': [
                'Sony PlayStation', 'Microsoft Xbox', 'Nintendo', 'Valve Steam',
                'Sega', 'Atari'
            ],

            'soundbar': [
                'Sonos', 'Bose', 'Samsung', 'LG', 'Sony', 'Vizio', 'Yamaha',
                'JBL', 'Polk Audio'
            ],

            'av_receiver': [
                'Denon', 'Yamaha', 'Onkyo', 'Marantz', 'Pioneer', 'Sony',
                'Anthem', 'NAD'
            ],

            'turntable': [
                'Audio-Technica', 'Pro-Ject', 'Rega', 'Technics', 'Denon'
            ],

            # ========== SALUD Y FITNESS ==========
            'smart_scale': [
                'Withings', 'Fitbit', 'Eufy', 'Garmin', 'QardioBase',
                'Greater Goods', 'Yunmai'
            ],

            'fitness_equipment': [
                'Peloton', 'NordicTrack', 'Tonal', 'Mirror', 'Hydrow',
                'Tempo', 'Echelon', 'Bowflex', 'ProForm'
            ],

            'blood_pressure_monitor': [
                'Omron', 'Withings', 'Qardio', 'iHealth'
            ],

            'thermometer': [
                'Kinsa', 'Withings', 'iHealth', 'Braun'
            ],

            # ========== NETWORKING Y INFRAESTRUCTURA ==========
            'router': [
                'TP-Link', 'Netgear', 'Asus', 'Linksys', 'D-Link', 'Ubiquiti',
                'Cisco', 'MikroTik', 'Arris', 'Motorola', 'Google Wifi',
                'Eero', 'Orbi', 'Amplifi', 'Deco'
            ],

            'access_point': [
                'Ubiquiti', 'TP-Link', 'Netgear', 'Cisco', 'Aruba',
                'Ruckus', 'EnGenius', 'Cambium'
            ],

            'mesh_node': [
                'Google Wifi', 'Eero', 'Netgear Orbi', 'Linksys Velop',
                'TP-Link Deco', 'Asus AiMesh', 'Amazon Eero'
            ],

            'switch': [
                'Cisco', 'Netgear', 'TP-Link', 'Ubiquiti', 'D-Link',
                'HP', 'Dell', 'Juniper', 'Arista'
            ],

            'modem': [
                'Arris', 'Motorola', 'Netgear', 'Linksys', 'TP-Link',
                'Zoom', 'Asus'
            ],

            'range_extender': [
                'TP-Link', 'Netgear', 'Linksys', 'D-Link', 'Asus'
            ],

            # ========== ALMACENAMIENTO ==========
            'nas': [
                'Synology', 'QNAP', 'Western Digital', 'Seagate',
                'Asustor', 'TerraMaster', 'Netgear ReadyNAS'
            ],

            'external_drive': [
                'Western Digital', 'Seagate', 'LaCie', 'G-Technology',
                'SanDisk', 'Buffalo'
            ],

            # ========== OFICINA ==========
            'printer': [
                'HP', 'Canon', 'Epson', 'Brother', 'Lexmark', 'Xerox',
                'Ricoh', 'Kyocera', 'Dell', 'Samsung'
            ],

            'scanner': [
                'Fujitsu', 'Epson', 'Brother', 'Canon', 'HP'
            ],

            'label_printer': [
                'Dymo', 'Brother', 'Rollo', 'Zebra'
            ],

            # ========== DOMÓTICA Y HUB ==========
            'smart_hub': [
                'Samsung SmartThings', 'Hubitat', 'Wink', 'Home Assistant',
                'Homey', 'Vera', 'Insteon', 'Control4'
            ],

            'zigbee_hub': [
                'Philips Hue Bridge', 'Samsung SmartThings', 'Amazon Echo',
                'Hubitat'
            ],

            'zwave_hub': [
                'Samsung SmartThings', 'Hubitat', 'HomeSeer', 'Vera'
            ],

            # ========== CERRADURAS Y ACCESO ==========
            'smart_lock': [
                'August', 'Yale', 'Schlage', 'Kwikset', 'Level', 'Wyze',
                'Ultraloq', 'Nuki', 'Danalock', 'Lockly'
            ],

            'garage_door': [
                'Chamberlain MyQ', 'Genie Aladdin', 'Nexx', 'Tailwind',
                'Ryobi', 'ismartgate'
            ],

            # ========== CORTINAS Y PERSIANAS ==========
            'smart_blinds': [
                'Lutron', 'Somfy', 'IKEA', 'Yoolax', 'MySmartBlinds',
                'Serena', 'PowerView'
            ],

            # ========== SENSORES ==========
            'motion_sensor': [
                'Philips Hue', 'Aqara', 'Eve', 'Samsung SmartThings',
                'Ring', 'Wyze'
            ],

            'door_sensor': [
                'Ring', 'SimpliSafe', 'Wyze', 'Aqara', 'Samsung SmartThings',
                'Eve'
            ],

            'water_leak_sensor': [
                'Flo', 'Phyn', 'Moen', 'Ring', 'Wyze', 'Aqara', 'Eve'
            ],

            'smoke_detector': [
                'Nest Protect', 'First Alert', 'Kidde', 'Ring'
            ],

            'co_detector': [
                'Nest Protect', 'First Alert', 'Kidde', 'Roost'
            ],

            # ========== VEHÍCULOS ==========
            'car_system': [
                'Tesla', 'Ford Sync', 'GM OnStar', 'Toyota Entune',
                'BMW ConnectedDrive', 'Mercedes me', 'Audi Connect'
            ],

            'dash_cam': [
                'Garmin', 'Nextbase', 'Viofo', 'Thinkware', 'BlackVue',
                'Rexing', 'Vantrue'
            ],

            'obd_adapter': [
                'BlueDriver', 'Veepeak', 'FIXD', 'Carista', 'Vgate'
            ],

            # ========== OTROS ==========
            'e_ink_display': [
                'InkPlate', 'Waveshare', 'Pimoroni', 'Kobo'
            ],

            'weather_station': [
                'Netatmo', 'Ambient Weather', 'Ecowitt', 'Davis',
                'AcuRite', 'La Crosse'
            ],

            'power_monitor': [
                'Sense', 'Emporia', 'Neurio', 'Curb', 'Aeotec'
            ],

            'ups': [
                'APC', 'CyberPower', 'Tripp Lite', 'Eaton'
            ],

            'pdu': [
                'APC', 'Tripp Lite', 'CyberPower', 'Raritan'
            ],

            'server': [
                'Dell PowerEdge', 'HP ProLiant', 'Cisco UCS', 'Supermicro',
                'Lenovo ThinkSystem'
            ],

            'raspberry_pi': [
                'Raspberry Pi'
            ],

            'arduino': [
                'Arduino'
            ],

            'esp_device': [
                'Espressif', 'ESP32', 'ESP8266'
            ],
        }

        # Patrones de hostname (EXHAUSTIVOS)
        self.hostname_patterns = {
            # Personal
            'smartphone': [
                r'iphone', r'android', r'galaxy[-\s]?s\d+', r'pixel[-\s]?\d+',
                r'oneplus', r'xiaomi', r'redmi', r'mobile', r'phone', r'huawei'
            ],
            'computer': [
                r'desktop', r'laptop', r'pc[-\s]', r'workstation', r'macbook',
                r'imac', r'thinkpad', r'latitude', r'inspiron', r'pavilion'
            ],
            'tablet': [
                r'ipad', r'tablet', r'kindle[-\s]?fire', r'surface[-\s]?go'
            ],
            'wearable': [
                r'watch', r'fitbit', r'band', r'tracker', r'garmin'
            ],
            'e_reader': [
                r'kindle', r'kobo', r'nook', r'remarkable'
            ],

            # Seguridad
            'security_camera': [
                r'camera', r'cam[-\s]', r'ipcam', r'wyze[-\s]?cam', r'ring[-\s]?cam',
                r'arlo', r'nest[-\s]?cam', r'blink'
            ],
            'doorbell': [
                r'doorbell', r'ring[-\s]?door', r'bell', r'nest[-\s]?hello'
            ],
            'baby_monitor': [
                r'baby', r'monitor', r'nanit', r'owlet', r'infant'
            ],

            # Audio
            'smart_speaker': [
                r'echo', r'alexa', r'google[-\s]?home', r'nest[-\s]?(hub|audio)',
                r'homepod', r'sonos'
            ],
            'smart_display': [
                r'echo[-\s]?show', r'nest[-\s]?hub', r'portal'
            ],

            # Iluminación
            'smart_bulb': [
                r'bulb', r'light', r'lamp', r'hue[-\s]?', r'lifx'
            ],
            'led_strip': [
                r'strip', r'led[-\s]?strip', r'govee'
            ],

            # Enchufes
            'smart_plug': [
                r'plug', r'outlet', r'socket', r'kasa', r'wemo'
            ],
            'smart_switch': [
                r'switch', r'lutron', r'leviton'
            ],

            # Clima
            'thermostat': [
                r'thermostat', r'nest[-\s]?thermo', r'ecobee'
            ],
            'air_purifier': [
                r'purifier', r'air[-\s]?purif', r'dyson[-\s]?pure'
            ],
            'humidifier': [
                r'humidifier', r'humid'
            ],
            'fan': [
                r'fan', r'dyson[-\s]?fan'
            ],

            # Cocina
            'smart_refrigerator': [
                r'fridge', r'refrigerator', r'family[-\s]?hub'
            ],
            'smart_oven': [
                r'oven', r'june', r'tovala', r'brava'
            ],
            'microwave': [
                r'microwave', r'micro'
            ],
            'coffee_maker': [
                r'coffee', r'keurig', r'nespresso'
            ],
            'instant_pot': [
                r'instant[-\s]?pot', r'ninja[-\s]?foodi', r'crock[-\s]?pot'
            ],
            'dishwasher': [
                r'dishwasher', r'dish[-\s]?wash'
            ],

            # Lavandería
            'washing_machine': [
                r'washer', r'washing', r'lavadora'
            ],
            'dryer': [
                r'dryer', r'secadora'
            ],

            # Limpieza
            'robot_vacuum': [
                r'roomba', r'vacuum', r'roborock', r'robot', r'aspiradora',
                r'ecovacs', r'shark[-\s]?iq', r'eufy[-\s]?robovac'
            ],
            'robot_mop': [
                r'braava', r'mop', r'robot[-\s]?mop'
            ],

            # Jardín
            'sprinkler_system': [
                r'sprinkler', r'rachio', r'rain[-\s]?bird', r'irrigation'
            ],
            'lawn_mower': [
                r'mower', r'lawn', r'husqvarna', r'robomow'
            ],
            'grill': [
                r'grill', r'weber', r'traeger', r'bbq'
            ],

            # Mascotas
            'pet_feeder': [
                r'pet[-\s]?feed', r'feeder', r'petnet'
            ],
            'litter_box': [
                r'litter', r'litter[-\s]?robot'
            ],

            # Entretenimiento
            'smart_tv': [
                r'tv', r'television', r'samsung[-\s]?tv', r'lg[-\s]?tv'
            ],
            'streaming_device': [
                r'chromecast', r'roku', r'firetv', r'appletv', r'nvidia[-\s]?shield'
            ],
            'game_console': [
                r'playstation', r'ps[345]', r'xbox', r'nintendo', r'switch',
                r'steam[-\s]?deck'
            ],
            'soundbar': [
                r'soundbar', r'sound[-\s]?bar'
            ],

            # Salud
            'smart_scale': [
                r'scale', r'withings', r'báscula'
            ],
            'fitness_equipment': [
                r'peloton', r'tonal', r'mirror[-\s]?fit', r'hydrow', r'bike'
            ],

            # Networking
            'router': [
                r'router', r'gateway', r'modem', r'access[-\s]?point'
            ],
            'mesh_node': [
                r'eero', r'orbi', r'deco', r'mesh', r'wifi[-\s]?point'
            ],
            'switch': [
                r'switch', r'poe[-\s]?switch'
            ],

            # Almacenamiento
            'nas': [
                r'nas', r'synology', r'qnap', r'diskstation', r'storage'
            ],

            # Oficina
            'printer': [
                r'printer', r'print', r'hp[-\s]?laserjet', r'epson', r'canon'
            ],

            # Domótica
            'smart_hub': [
                r'smartthings', r'hubitat', r'homeassistant', r'hub'
            ],

            # Cerraduras
            'smart_lock': [
                r'lock', r'august', r'yale', r'schlage'
            ],
            'garage_door': [
                r'garage', r'myq', r'genie'
            ],

            # Sensores
            'motion_sensor': [
                r'motion', r'sensor[-\s]?pir'
            ],
            'water_leak_sensor': [
                r'leak', r'water[-\s]?sensor', r'flo', r'phyn'
            ],
            'smoke_detector': [
                r'smoke', r'nest[-\s]?protect', r'detector'
            ],

            # Vehículos
            'dash_cam': [
                r'dashcam', r'dash[-\s]?cam', r'blackvue'
            ],

            # Otros
            'weather_station': [
                r'weather', r'netatmo', r'ambient'
            ],
            'raspberry_pi': [
                r'raspberry', r'raspi', r'rpi'
            ],
            'arduino': [
                r'arduino'
            ],
        }

    def _load_oui_database(self):
        """Cargar OUI database"""
        if not os.path.exists(self.oui_file):
            return
        try:
            with open(self.oui_file, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    match = re.match(r'([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2})\s+\(hex\)\s+(.+)', line)
                    if match:
                        oui = match.group(1).replace('-', ':')
                        vendor = match.group(2).strip()
                        self.oui_cache[oui] = vendor
        except:
            pass

    def get_vendor(self, mac_address: str) -> str:
        """Obtener fabricante"""
        oui = ':'.join(mac_address.upper().split(':')[:3])
        return self.oui_cache.get(oui, 'Unknown')

    def identify_device_type(self, vendor: str, hostname: Optional[str] = None) -> str:
        """Identificar tipo de dispositivo"""
        vendor_lower = vendor.lower()

        # Por fabricante
        for device_type, vendors in self.vendor_patterns.items():
            for known_vendor in vendors:
                if known_vendor.lower() in vendor_lower:
                    if hostname:
                        refined = self._refine_by_hostname(hostname, device_type)
                        if refined != device_type:
                            return refined
                    return device_type

        # Por hostname
        if hostname:
            hostname_lower = hostname.lower()
            for device_type, patterns in self.hostname_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, hostname_lower):
                        return device_type

        return 'unknown'

    def _refine_by_hostname(self, hostname: str, initial_type: str) -> str:
        """Refinar por hostname"""
        hostname_lower = hostname.lower()
        for device_type, patterns in self.hostname_patterns.items():
            for pattern in patterns:
                if re.search(pattern, hostname_lower):
                    return device_type
        return initial_type

    def get_device_icon(self, device_type: str) -> str:
        """Obtener icono"""
        icons = {
            # Personal
            'smartphone': '📱', 'computer': '💻', 'tablet': '📱', 'wearable': '⌚', 'e_reader': '📖',

            # Seguridad
            'security_camera': '📷', 'doorbell': '🔔', 'security_system': '🛡️', 'baby_monitor': '👶',

            # Audio
            'smart_speaker': '🔊', 'smart_display': '📺', 'soundbar': '🔉', 'av_receiver': '📻',

            # Iluminación
            'smart_bulb': '💡', 'led_strip': '🌈',

            # Enchufes
            'smart_plug': '🔌', 'smart_switch': '⚡',

            # Clima
            'thermostat': '🌡️', 'air_purifier': '💨', 'humidifier': '💧', 'fan': '🌀', 'air_conditioner': '❄️',

            # Cocina
            'smart_refrigerator': '🧊', 'smart_oven': '🍳', 'microwave': '📦', 'coffee_maker': '☕',
            'instant_pot': '🍲', 'air_fryer': '🍟', 'dishwasher': '🍽️',

            # Lavandería
            'washing_machine': '🧺', 'dryer': '🌪️',

            # Limpieza
            'robot_vacuum': '🤖', 'robot_mop': '🧹',

            # Jardín
            'sprinkler_system': '💦', 'lawn_mower': '🌱', 'grill': '🍖', 'pool_controller': '🏊',

            # Mascotas
            'pet_feeder': '🐾', 'pet_camera': '🐕', 'litter_box': '🐈',

            # Entretenimiento
            'smart_tv': '📺', 'streaming_device': '📺', 'game_console': '🎮', 'turntable': '💿',

            # Salud
            'smart_scale': '⚖️', 'fitness_equipment': '🏋️', 'blood_pressure_monitor': '🩺',
            'thermometer': '🌡️',

            # Networking
            'router': '📡', 'access_point': '📶', 'mesh_node': '🕸️', 'switch': '🔀',
            'modem': '📞', 'range_extender': '📡',

            # Almacenamiento
            'nas': '💾', 'external_drive': '💿',

            # Oficina
            'printer': '🖨️', 'scanner': '📄', 'label_printer': '🏷️',

            # Domótica
            'smart_hub': '🏠', 'zigbee_hub': '📻', 'zwave_hub': '📻',

            # Cerraduras
            'smart_lock': '🔐', 'garage_door': '🚪',

            # Cortinas
            'smart_blinds': '🪟',

            # Sensores
            'motion_sensor': '👁️', 'door_sensor': '🚪', 'water_leak_sensor': '💧',
            'smoke_detector': '🔥', 'co_detector': '☠️',

            # Vehículos
            'car_system': '🚗', 'dash_cam': '📹', 'obd_adapter': '🔧',

            # Otros
            'weather_station': '🌤️', 'power_monitor': '⚡', 'ups': '🔋', 'server': '🖥️',
            'raspberry_pi': '🥧', 'arduino': '🔬', 'esp_device': '📟',

            'unknown': '❓'
        }
        return icons.get(device_type, '❓')

    def get_display_name(self, device_type: str) -> str:
        """Nombre legible"""
        names = {
            # Personal
            'smartphone': 'Teléfono Móvil', 'computer': 'Computadora', 'tablet': 'Tablet',
            'wearable': 'Smartwatch/Pulsera', 'e_reader': 'Lector eBook',

            # Seguridad
            'security_camera': 'Cámara de Seguridad', 'doorbell': 'Timbre Inteligente',
            'security_system': 'Sistema de Alarma', 'baby_monitor': 'Monitor de Bebé',

            # Audio
            'smart_speaker': 'Asistente de Voz', 'smart_display': 'Pantalla Inteligente',
            'soundbar': 'Barra de Sonido', 'av_receiver': 'Receptor AV',

            # Iluminación
            'smart_bulb': 'Bombilla Inteligente', 'led_strip': 'Tira LED',

            # Enchufes
            'smart_plug': 'Enchufe Inteligente', 'smart_switch': 'Interruptor Inteligente',

            # Clima
            'thermostat': 'Termostato', 'air_purifier': 'Purificador de Aire',
            'humidifier': 'Humidificador', 'fan': 'Ventilador', 'air_conditioner': 'Aire Acondicionado',

            # Cocina
            'smart_refrigerator': 'Refrigerador Inteligente', 'smart_oven': 'Horno Inteligente',
            'microwave': 'Microondas', 'coffee_maker': 'Cafetera', 'instant_pot': 'Olla Instantánea',
            'air_fryer': 'Freidora de Aire', 'dishwasher': 'Lavavajillas',

            # Lavandería
            'washing_machine': 'Lavadora', 'dryer': 'Secadora',

            # Limpieza
            'robot_vacuum': 'Aspiradora Robot', 'robot_mop': 'Trapeador Robot',

            # Jardín
            'sprinkler_system': 'Sistema de Riego', 'lawn_mower': 'Cortacésped Robot',
            'grill': 'Parrilla Inteligente', 'pool_controller': 'Controlador de Piscina',

            # Mascotas
            'pet_feeder': 'Alimentador de Mascotas', 'pet_camera': 'Cámara de Mascotas',
            'litter_box': 'Arenero Automático',

            # Entretenimiento
            'smart_tv': 'Smart TV', 'streaming_device': 'Dispositivo de Streaming',
            'game_console': 'Consola de Videojuegos', 'turntable': 'Tocadiscos',

            # Salud
            'smart_scale': 'Báscula Inteligente', 'fitness_equipment': 'Equipo de Ejercicio',
            'blood_pressure_monitor': 'Monitor de Presión', 'thermometer': 'Termómetro',

            # Networking
            'router': 'Router', 'access_point': 'Punto de Acceso', 'mesh_node': 'Nodo Mesh',
            'switch': 'Switch de Red', 'modem': 'Módem', 'range_extender': 'Extensor de Red',

            # Almacenamiento
            'nas': 'Almacenamiento en Red (NAS)', 'external_drive': 'Disco Externo',

            # Oficina
            'printer': 'Impresora', 'scanner': 'Escáner', 'label_printer': 'Impresora de Etiquetas',

            # Domótica
            'smart_hub': 'Hub Domótico', 'zigbee_hub': 'Hub Zigbee', 'zwave_hub': 'Hub Z-Wave',

            # Cerraduras
            'smart_lock': 'Cerradura Inteligente', 'garage_door': 'Puerta de Garaje',

            # Cortinas
            'smart_blinds': 'Persianas Inteligentes',

            # Sensores
            'motion_sensor': 'Sensor de Movimiento', 'door_sensor': 'Sensor de Puerta',
            'water_leak_sensor': 'Sensor de Fugas', 'smoke_detector': 'Detector de Humo',
            'co_detector': 'Detector de CO',

            # Vehículos
            'car_system': 'Sistema de Auto', 'dash_cam': 'Cámara de Tablero',
            'obd_adapter': 'Adaptador OBD',

            # Otros
            'weather_station': 'Estación Meteorológica', 'power_monitor': 'Monitor de Energía',
            'ups': 'Sistema UPS', 'server': 'Servidor', 'raspberry_pi': 'Raspberry Pi',
            'arduino': 'Arduino', 'esp_device': 'Dispositivo ESP',

            'unknown': 'Desconocido'
        }
        return names.get(device_type, 'Desconocido')

    def identify_device(self, mac_address: str, hostname: Optional[str] = None) -> Dict[str, str]:
        """Identificación completa"""
        vendor = self.get_vendor(mac_address)
        device_type = self.identify_device_type(vendor, hostname)
        icon = self.get_device_icon(device_type)
        display_name = self.get_display_name(device_type)

        return {
            'vendor': vendor,
            'device_type': device_type,
            'icon': icon,
            'display_name': display_name
        }
