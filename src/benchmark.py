#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import json
import random
import server
import subprocess
import sys
import time
import urllib.request

class benchmark:
    def __init__(self, privkey, address, server):
        self.__privkey = privkey
        self.__server = server
        self.__address = address
        self.__ifname = 'wgbench0'
        self.__conffile = f'/tmp/wireguard/{self.__ifname}.conf'

        ## Results
        self.__ping_min = None
        self.__ping_avg = None
        self.__ping_max = None
        self.__download_speed = 0
        self.__upload_speed = 0
    
    def __del__(self):
        self.close()
    
    def __enter__(self):
        self.connect()
    
    def __exit__(self, *args):
        self.close()

    @property
    def ping_min(self):
        return self.__ping_min

    @property
    def ping_avg(self):
        return self.__ping_avg

    @property
    def ping_max(self):
        return self.__ping_max
    
    @property
    def download_speed(self):
        return self.__download_speed
    
    @property
    def upload_speed(self):
        return self.__upload_speed

    def connect(self):
        ## Configure the wireguard interface
        os.makedirs('/tmp/wireguard', exist_ok=True)
        with open(self.__conffile, 'w') as fp:
            print(f'[Interface]', file=fp)
            print(f'Address = {self.__address}/32', file=fp)
            print(f'PrivateKey = {self.__privkey}', file=fp)
            print(f'DNS = 10.64.0.1', file=fp)
            print(f'Table = auto', file=fp)
            print(f'MTU = 1420', file=fp)
            print(f'', file=fp)
            print(self.__server.wgpeer(), file=fp)
        os.chmod(self.__conffile, 0o660)

        subprocess.run(['wg-quick', 'up', self.__conffile], capture_output=True, check=True)
        time.sleep(5)
    
    def close(self):
        ## Ensure the interface is destroyed
        if os.path.exists(self.__conffile):
            subprocess.run(['wg-quick', 'down', self.__conffile],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.remove(self.__conffile)

    def checkdns(self, domain='archive.mozilla.org'):
        result = subprocess.run(['dig', '@10.64.0.1', domain],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return (result.returncode == 0)

    def run(self):
        ## Abort quickly if we can't validate DNS
        if not self.checkdns():
            self.__download_speed = 0.0
            self.__upload_speed = 0.0
            self.__ping_avg = None
            return False
        
        ## Run the speedtest
        try:
            result = subprocess.run(['speedtest-cli', '--json', '--bytes'], stdout=subprocess.PIPE, text=True)
            js = json.loads(result.stdout)
            self.__download_speed = js['download']
            self.__upload_speed = js['upload']
            self.__ping_avg = js['ping']
            return True
        except:
            self.__download_speed = 0.0
            self.__upload_speed = 0.0
            self.__ping_avg = None
            return False

