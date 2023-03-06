from scapy.all import *
from scapy.all import IP, sendp, sniff, UDP, Ether, BOOTP, DHCP

# DHCP server is a server that listens for DHCP requests and sends back DHCP offers.

# DHCP DISCOVER: Client broadcasts that it needs to lease an IP configuration from a DHCP server
# DHCP OFFER: Server broadcasts to offer an IP configuration
# DHCP REQUEST: Client broadcasts to formally ask for the offered IP configuration
# DHCP ACKNOWLEDGE (ACK): Server broadcasts confirming the leased IP configuration


# Define the DHCP server's IP address and the IP address pool
dhcp_server_ip = "127.0.0.1"
dhcp_port = 67
ip_pool_start = "10.100.102.27"
ip_pool_end = "10.100.102.255"
DHCP_SERVER_MAC = "00:00:00:00:00:01"
lease_time = 86400  # Define the DHCP lease time (in seconds) -- 1 day
dns_server_ip = "127.127.1.1"  # Define the DNS server IP address
ip_dic = {}  # Dictionary to store the MAC address and the assigned IP address of each client


def is_ip_assigned(requested_ip):

    return requested_ip in ip_dic.values()


def generate_ip():
    start_ip_int = int(ip_pool_start.split(".")[-1])
    end_ip_int = int(ip_pool_end.split(".")[-1])

    ip_int = random.randint(start_ip_int, end_ip_int)
    ip_address = "10.100.102." + str(ip_int)

    return ip_address


def handle_dhcp_discover(packet):
    if DHCP in packet and packet[DHCP].options[0][1] == 1:  # DHCP discover
        print("DHCP discover received")

        # Extract the client's MAC address from the DHCP discover packet
        client_mac = packet[Ether].src
        if client_mac in ip_dic:
            print("Client already has an IP address")
            return

        # Generate a random IP address from the pool and check if it's already assigned
        offered_ip = None
        while not offered_ip:
            ip_address = generate_ip()
            if not is_ip_assigned(ip_address):
                offered_ip = ip_address

        # Define the DHCP options to be sent to the client with the ip address genarated
        dhcp_options = [("message-type", "offer"), ("subnet_mask", "255.255.255.0"), ("router", dhcp_server_ip),
                        ("lease_time", lease_time), ("name_server", dns_server_ip), "end"]
        print(f"Offering IP address {offered_ip} to client {client_mac}")
        time.sleep(1)
        # Send the DHCP offer packet with the same xid as the DHCP discover packet
        dhcp_offer = Ether(src=DHCP_SERVER_MAC, dst=client_mac) / \
            IP(src=dhcp_server_ip, dst="255.255.255.255") / UDP(sport=67, dport=68) / \
            BOOTP(op=2, yiaddr=offered_ip, siaddr=dhcp_server_ip, chaddr=client_mac, xid=packet[BOOTP].xid) / \
            DHCP(options=dhcp_options)
        sendp(dhcp_offer)


def handle_dhcp_request(packet):
    # Extract the client's MAC address and requested IP address from the DHCP request packet
    client_mac = packet[Ether].src
    requested_ip = packet[DHCP].options[1][1]

    # Check if the requested IP address is available
    if is_ip_assigned(requested_ip):
        print(f"IP address {requested_ip} is not available")
        return
    ip_dic.update({client_mac: requested_ip})
    print(f"Assigning IP address {requested_ip} to client {client_mac}")
    time.sleep(1)
    # send the DHCP ACK packet
    dhcp_ack = Ether(src=DHCP_SERVER_MAC, dst="ff:ff:ff:ff:ff:ff") / \
        IP(src=dhcp_server_ip, dst="255.255.255.255") / \
        UDP(sport=67, dport=68) / \
        BOOTP(op=2, yiaddr=requested_ip, siaddr=dhcp_server_ip, chaddr=client_mac, xid=packet[BOOTP].xid) / \
        DHCP(options=[("message-type", "ack"), ("subnet_mask", "255.255.255.0"), ("router", dhcp_server_ip),
                      ("lease_time", lease_time), ("name_server", dns_server_ip), "end"])
    sendp(dhcp_ack)
    print("sent ack. finished. waiting for next packet...")
    print(ip_dic)


def handle_dhcp(packet):
    if DHCP in packet and packet[DHCP].options[0][1] == 1:  # DHCP discover
        # thread1 = threading.Thread(target=handle_dhcp_discover, args=(packet,))
        # thread1.start()
        handle_dhcp_discover(packet)
    elif DHCP in packet and packet[DHCP].options[0][1] == 3:  # DHCP request
        # thread2 = threading.Thread(target=handle_dhcp_request, args=(packet,))
        # thread2.start()
        handle_dhcp_request(packet)


if __name__ == '__main__':
    # Start sniffing for DHCP packets
    print("Starting DHCP server")
    sniff(
        filter=f"udp and dst port 67", iface="Ethernet", prn=handle_dhcp)
