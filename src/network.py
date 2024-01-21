## Class for handling networking. 
import os
import gc
import ssl
import time
import board
import wifi
import socketpool
import adafruit_ntp
import adafruit_ds3231

class WifiNetwork:
    def __init__(self) -> None:
        self.SSID = os.getenv('WIFI_SSID')
        self.PASS = os.getenv('WIFI_PASSWORD')

        if self.SSID is None or self.PASS is None or len(self.SSID) == 0 or len(self.PASS) == 0:
            raise Exception("WIFI_SSID & WIFI_PASSWORD are stored in settings.toml, please add them")

        # NTP specific constants
        self.TZ = os.getenv('TZ_OFFSET')
        self.DST = os.getenv('DST_ADJUST')
        
        # Offer up to 3 ntp api's.
        self.NTP_HOST = os.getenv('NTP_HOST').split('|', 2)
        self.INTERVAL = os.getenv('NTP_INTERVAL')

        if self.TZ is None or self.NTP_HOST is None or self.INTERVAL is None:
            raise Exception("NTP_HOST, NTP_INTERVAL & TZ_OFFSET are stored in settings.toml, please add them")

        self._dst_adjust = True if self.DST == "1" else False
        i2c = board.I2C()
        self.rtc = adafruit_ds3231.DS3231(i2c)
        self._last_ntp_sync = None
        # wifi.radio will reconnect by itself if disconnected.
        wifi.radio.connect(self.SSID, self.PASS)
        try:
            self.set_time()
            self._last_ntp_sync = time.time()
        except Exception as e:
            print('Unable to set rtc time from NTP server', e)


    def set_time(self):
        new_time = self.get_time()
        if new_time:
            if self._dst_adjust:
                # struct_time is read only, convert to list and then back into struct.
                new_time_writable = list(new_time)
                new_time_writable[3] = (new_time_writable[3] + 1)%24
                new_time = time.struct_time(tuple(new_time_writable))
        
            self.rtc.datetime = new_time
            print('updated RTC datetime')


    def get_time(self):
        pool = socketpool.SocketPool(wifi.radio)
        ntp_try = 0
        while ntp_try < len(self.NTP_HOST):
            try:
                ntp = adafruit_ntp.NTP(pool, tz_offset=self.TZ, server=self.NTP_HOST[ntp_try])
                self._last_ntp_sync = time.time()
                return ntp.datetime
            except Exception as ex:
                print(f'Unable to connect to NTP Server {self.NTP_HOST[ntp_try]} with exception:', ex)
                ntp_try += 1
        raise Exception("Unable to contact NTP servers")


    def update_required(self) -> bool:
        
        if not self._last_ntp_sync or (self._last_ntp_sync and time.time() >= int(self._last_ntp_sync) + int(self.INTERVAL or 86400)):
            return True
        return False
