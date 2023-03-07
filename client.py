import time
from scapy.all import *
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import *


def generate_random_mac():
    mac = [0x00, 0x16, 0x3e,
           random.randint(0x00, 0x7f),
           random.randint(0x00, 0xff),
           random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


client_mac = ""


def get_dns_ip():  # Get the DNS server IP address from the DHCP server
    # create dhcp discover packet
    dhcp_discover = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff") / \
        IP(src="0.0.0.0", dst="255.255.255.255") / \
        UDP(sport=68, dport=67) / BOOTP(chaddr=client_mac, xid=RandInt()) / \
        DHCP(options=[("message-type", "discover"),
                      ("requested_addr",
                       "0.0.0.0"),
                      "end"])
    # Send the DHCP discover packet and wait for a response
    temp_ip = ""
    count = 0
    discover_received = False
    while not discover_received:
        sendp(dhcp_discover)
        time.sleep(1)
        print("DHCP discover sent, waiting for offer...")
        for packet in sniff(filter="udp and dst port 68 ", iface="Ethernet", timeout=1, count=1):
            if (DHCP in packet) and (packet[DHCP].options[0][1] == 2):
                temp_ip = packet[BOOTP].yiaddr
                discover_received = True
                dns_server = next(
                    (x[1] for x in packet[DHCP].options if x[0] == "name_server"), None)
                print("DHCP offer received, IP address is " +
                      temp_ip + ", DNS server is " + dns_server)
                break
        count += 1
        if count == 3:
            print("No DHCP offer received")
            return None, None

    # Define the DHCP request packet
    print(temp_ip)
    dhcp_request = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff") / \
        IP(src="0.0.0.0", dst="255.255.255.255") / UDP(sport=68, dport=67) / \
        BOOTP(chaddr=client_mac, xid=RandInt()) / \
        DHCP(options=[("message-type", "request"),
                      ("requested_addr", temp_ip),
                      "end"])

    # Send the DHCP request packet and wait for a response
    offer_received = False
    while not offer_received:
        sendp(dhcp_request)
        time.sleep(1)
        # print(dhcp_request.summary)
        print("DHCP request sent, waiting for ack...")
        for packet in sniff(filter="udp and dst port 68 ", iface="Ethernet", timeout=1, count=1):
            if DHCP in packet and packet[DHCP].options[0][1] == 5:  # DHCP ACK
                offer_received = True
                break

    # Extract the assigned IP address and DNS server address from the DHCP offer packet
    offered_ip = packet[BOOTP].yiaddr
    conf.ip = offered_ip  # Set the IP address to use
    return dns_server, offered_ip


# Get the IP address of the requested domain name from the DNS server
def get_app_ip(domain_name, dns_server):
    # create DNS request packet
    dns_request = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff") / IP(src="127.0.0.1", dst=dns_server) / UDP(
        sport=20534, dport=53) / DNS(rd=1, qd=DNSQR(qname=domain_name))
    # Send the packet and wait for a response
    sendp(dns_request)
    response_received = False
    while not response_received:
        for packet in sniff(filter=f"udp src port 53 and ip src {dns_server}", iface=conf.iface, timeout=1, count=1):
            if DNS in packet and packet[DNS].rcode == 3:  # DNS error
                print("Domain name not found")
                return None
            if DNS in packet and packet[DNS].ancount > 0:
                response_received = True
                break
    return packet[DNS].an.rdata


if __name__ == "__main__":
    client_mac = generate_random_mac()  # generate random mac address for the client
    print("Client MAC address: " + client_mac)
    dns_server, new_ip = get_dns_ip()  # get the dns_ip from the dhcp server
    if dns_server is None or new_ip is None:
        print("No DNS server IP address received")
        exit(1)
    else:
        print("Assigned IP address: " + new_ip)
        print("DNS server: " + dns_server)

    # get the ip of app.html from dns server
    app_ip = get_app_ip("app.html", "127.0.0.1")  # temporary dns ip
    if app_ip is None:
        print("No IP address received")
        exit(1)
    else:
        print("IP address of app.html: " + app_ip)

    # connect to the web server and get the requested file:
