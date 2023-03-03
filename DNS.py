import time
from scapy.all import *
from scapy.all import DNS, DNSRR, IP, sendp, sniff, UDP, Ether
dns_server_ip = "127.0.0.1"
dns_server_port = 53
dns_mac_address = "00:00:00:00:00:00"
domains_list = [("app.html.", "1.1.1.32"),
                ("www.google.com.", "8.8.8.8")]


def check_domain_name(domain_name):
    for domain in domains_list:
        if domain_name == domain[0]:
            return domain[1]
    return None


def handle_dns_request(packet):
    print("DNS request received")
    domain_ip = check_domain_name(packet[DNS].qd.qname.decode("utf-8"))
    if domain_ip is None:
        print("DNS request for unknown domain")
        return

    dns_response = Ether(src=dns_mac_address, dst="ff:ff:ff:ff:ff:ff") / \
        IP(src=dns_server_ip, dst=packet[IP].src) \
        / UDP(sport=dns_server_port, dport=packet[UDP].sport) \
        / DNS(id=packet[DNS].id, qr=1, aa=1,
              qd=packet[DNS].qd, an=DNSRR(rrname=packet[DNS].qd.qname, ttl=10, rdata=domain_ip))
    sendp(dns_response)
    print("DNS response sent. waiting for next request...")


if __name__ == '__main__':
    print("Starting DNS server")
    sniff(
        filter=f"udp dst port 53 and ip dst {dns_server_ip}", prn=handle_dns_request)
