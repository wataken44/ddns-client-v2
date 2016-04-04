### ddns-client-v2

DDNS client script which supports IPv6 and works with home routers

#### description

- IPv6 support  
This script supports IPv6(IPv6 only, IPv4/IPv6 dualstack) network

- works with home routers  
We cannot run scripts on home routers, but some DDNS scripts assumed to be executed on the router.  
This script can be executed on any machine in our LAN.

#### requirement
- python 3.x

#### installation & usage

     $ git clone https://github.com/wataken44/ddns-client-v2
     $ cd ddns-client-v2
     $ cp config-sample.json config.json
     $ vi config.json
     $ python ddns.py

#### misc

tested DDNS servers:  
* <https://dynv6.com/>
* <http://ieserver.net/ddns.html>
