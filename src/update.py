#! /usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import argparse
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
    parser.add_argument('-a', '--addr', metavar='ADDR', type=str, required=True,
        help='Set local interface IP address to ADDR')
    parser.add_argument('-k', '--key', metavar='FILE', type=str, required=True,
        help='Load Wireguard private key from FILE')
    args = parser.parse_args()

    ## Read the private key file.
    with open(args.key, 'r') as keyfile:
        args.privatekey = keyfile.read().strip()

    ## Fetch the list of servers.
    serverlist = server.fetch()

    print(f'  {"HOSTNAME":24} {"IPv4-ADDR":16} {"PUBKEY":48}  {"LATENCY":12}  {"DOWNLOAD":12}  {"UPLOAD":12}')
    for s in serverlist:
        if s.vpntype != "wireguard":
            continue
        if len(args.names) and (s.hostname not in args.names):
            continue
        
        # Print server information
        print(f'  {s.hostname:24} {s.ipv4_addr_in:16} {s.pubkey:48}  ', end='')
        sys.stdout.flush()

        # Connect and prepare to run the benchmark
        bench = benchmark(args.privatekey, args.addr, s)
        bench.connect()
        if not bench.run():
            print('***failed***')
        else:
            latency = f'{bench.ping_avg} ms'
            download = pretty_speed(bench.download_speed)
            upload = pretty_speed(bench.upload_speed)
            print(f'{latency:12}  {download:12}  {upload:12}')

        bench.close()

