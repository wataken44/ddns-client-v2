#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ddns.py
ddns client
"""

import datetime
import json
import logging
import os
import socket
import sys

try:
    # python 3
    from urllib.parse import urlparse, urlunparse
    from urllib.request import urlopen, Request
except:
    # python 2
    from urlparse import urlparse, urlunparse
    from urllib2 import urlopen, Request


def main():
    root_dir = os.path.abspath(os.path.dirname(__file__)) + "/"
    logging.basicConfig(
        filename=(root_dir + 'ddns.log'),level=logging.INFO,
        format='%(asctime)s: [%(levelname)s] %(message)s'
    )

    fp = open(root_dir + 'config.json')
    config = json.loads(fp.read())
    fp.close()

    periodical_file = root_dir + 'periodical.txt'    
    periodical_update = False
    if not os.path.exists(periodical_file):
        periodical_update = True
    else:
        fp = open(periodical_file)
        prev = datetime.datetime.strptime(fp.readline().strip(), '%Y-%m-%d %H:%M:%S.%f')
        fp.close()
        delta = datetime.datetime.now() - prev
        if delta.days >= config['periodical_update_days']:
            logging.info('periodical update -> true')
            periodical_update = True

    if periodical_update:
        fp = open(periodical_file, 'w')
        fp.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
        fp.close()

    http_ipv4 = None
    body = urlget(config['ip_url'], ipv6=False)
    if body:
        http_ipv4 = str(body.decode('utf-8'))

    http_ipv6 = None
    body = urlget(config['ip_url'], ipv6=True)
    if body:
        http_ipv6 = str(body.decode('utf-8'))

    for di in config['domains']:
        dns_ipv4 = None
        dns_ipv6 = None
        update = periodical_update
        domain = di['domain']
        if di['ipv4']:
            dns_ipv4 = lookup(domain, ipv6=False)
            update |= (http_ipv4 != dns_ipv4)
        if di['ipv6']:
            dns_ipv6 = lookup(domain, ipv6=True)
            update |= (http_ipv6 != dns_ipv6)
        if update:
            url = di['update_url'].replace('%ipv4%', http_ipv4).replace('%ipv6%', http_ipv6)
            urlget(url)
            if di['ipv4'] and di['ipv6']:
                logging.info('update %s: %s -> %s, %s -> %s', domain, dns_ipv4, http_ipv4, dns_ipv6, http_ipv6)
            elif di['ipv4']:
                logging.info('update %s: %s -> %s', domain, dns_ipv4, http_ipv4)
            elif di['ipv6']:
                logging.info('update %s: %s -> %s', domain, dns_ipv6, http_ipv6)
            
def lookup(host, ipv6=False):
    try:
        family = socket.AF_INET
        if ipv6:
            family = socket.AF_INET6
        info = socket.getaddrinfo(host, 80, family)
        # get [(family, socktype, proto, canonname, (address, port))]
    except socket.error:
        return None

    if len(info) > 0:
        return info[0][4][0]
    else:
        return None

def urlget(url, ipv6=False):
    pr = urlparse(url)
    host, port = pr.netloc, None
    if pr.netloc.find(':') >= 0:
        host, port = pr.netloc.split(':')

    ip = lookup(host, ipv6)
    if ip is None:
        return None

    # create header
    headers = {
        'Host': pr.netloc,
        'USER-AGENT': 'ddns-client-v2(https://github.com/wataken44/ddns-client-v2)'
    }

    # create new url
    netloc = ip
    if ipv6:
        netloc = "[%s]" % netloc
    if port is not None:
        netloc = "%s:%s" % (ip, port)
        
    pr = (pr.scheme, netloc, pr.path, pr.params, pr.query, pr.fragment)
    url = urlunparse(pr)

    req = Request(url, headers=headers)
    fp = urlopen(req)
    body = fp.read()
    fp.close()

    return body
    
    
if __name__ == "__main__":
    main()
