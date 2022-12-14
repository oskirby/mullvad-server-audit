#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import json
import random
import urllib.request

class server:
    def __init__(self, js):
        self.__json = js

    @property
    def json(self):
        return self.__json

    @property
    def hostname(self):
        return self.__json["hostname"]
    
    @property
    def country_code(self):
        return self.__json["country_code"]
    
    @property
    def country_name(self):
        return self.__json["country_name"]
    
    @property
    def city_code(self):
        return self.__json["city_code"]
    
    @property
    def city_name(self):
        return self.__json["city_name"]
    
    def provider(self):
        return self.__json["provider"]

    @property
    def ipv4_addr_in(self):
        return self.__json["ipv4_addr_in"]
    
    @property
    def ipv6_addr_in(self):
        return self.__json["ipv6_addr_in"]

    @property
    def network_port_speed(self):
        return self.__json["network_port_speed"]
    
    @property
    def pubkey(self):
        return self.__json["pubkey"]
    
    @property
    def vpntype(self):
        return self.__json["type"]
    
    def __str__(self):
        return f'server({self.hostname})'
    
    def __repr__(self):
        return f'server("{self.__json}")'
    
    def wgpeer(self, port=None, allowedips=None):
        if port is None:
            port = random.randrange(4000, 32768)

        if allowedips is None:
            allowedips = ['0.0.0.0/0']

        return '\n'.join([
            '[Peer]',
            f'# Name = {self.hostname}.relays.mullvad.net',
            f'AllowedIPs = {",".join(allowedips)}',
            f'Endpoint = {self.ipv4_addr_in}:{port}',
            f'PublicKey = {self.pubkey}',
            f'PersistentKeepalive = 60'
        ])

def fetch(url='https://api.mullvad.net/www/relays/all/'):
    serverlist = []

    with urllib.request.urlopen(url) as response:
        js = json.loads(response.read())
        for serverjs in js:
            serverlist.append(server(serverjs))
    
    return serverlist

## Do some testing....
if __name__ == "__main__":
    pass