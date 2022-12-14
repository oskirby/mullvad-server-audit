#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
import json
import sys

import server
from benchmark import benchmark

def pretty_speed(speed):
    if (speed > 1000000000):
        return f'{speed / 1000000000:.2f} GB/s'
    elif (speed > 1000000):
        return f'{speed / 1000000:.2f} MB/s'
    elif (speed > 1000):
        return f'{speed / 1000:.2f} kB/s'
    else:
        return f'{speed} B/s'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Parse the Mullvad server list and benchmark the servers')
    
    parser.add_argument('names', metavar='NAME', type=str, nargs='*',
        help='Server hostnames to update (default: all)')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
        help='Print verbose information about the translation file')
    parser.add_argument('-c', '--config', metavar='FILE', type=str,
        help='Load Wireguard interface configuration from FILE')
    parser.add_argument('-s', '--show', default=False, action='store_true',
        help='Show wireguard server information in JSON format')
    args = parser.parse_args()

    ## Fetch the list of servers.
    serverlist = server.fetch()

    ## Display entries in the server list.
    if (args.show):
        jslist = []
        for s in serverlist:
            if s.vpntype != "wireguard":
                continue
            if len(args.names) and (s.hostname not in args.names):
                continue
            jslist.append(s.json)
        
        print(json.dumps(jslist, indent=3))
        sys.exit(0)

    ## Benchmark servers
    if not args.config:
        print("Required argument not found: --config FILE", file=sys.stderr)
        sys.exit(1)

    print(f'  {"HOSTNAME":24} {"LOCATION":12} {"IPv4-ADDR":16} {"PUBKEY":48}  {"LATENCY":12}  {"DOWNLOAD":12}  {"UPLOAD":12}')
    for s in serverlist:
        if s.vpntype != "wireguard":
            continue
        if len(args.names) and (s.hostname not in args.names):
            continue
        
        # Print server information
        print(f'  {s.hostname:24} {s.city_name:12} {s.ipv4_addr_in:16} {s.pubkey:48}  ', end='')
        sys.stdout.flush()

        # Connect and prepare to run the benchmark
        bench = benchmark(args.config, s)
        bench.connect()
        if not bench.run():
            print('***failed***')
        else:
            latency = f'{bench.ping_avg} ms'
            download = pretty_speed(bench.download_speed)
            upload = pretty_speed(bench.upload_speed)
            print(f'{latency:12}  {download:12}  {upload:12}')

        bench.close()

