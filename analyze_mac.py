from scapy.all import *
from tabulate import tabulate
from time import sleep


count = 0
TRUSTED_MACS =[] # TODO: COMPILE LIST OF TRUSTED MACS


def analyzeL2(packet):
    """Analyzes layer 2 of the packet"""
    # PDU header info
    eth_pdu_type = (
        "Ethernet II" if packet.name == "Ethernet" else packet.name
    )  # 802.3, 802.11, Ethernet ii,...
    src_mac = packet.src
    dst_mac = packet.dst
    # If packet is Ethernet II packet find protocol
    if packet.haslayer(Ether):
        try:
            packet_proto = ETHER_TYPES[
                packet[Ether].type
            ]  # Try to translate type no. to name
        except:
            packet_proto = packet[Ether].type
    # If packet is another standard, find protcol type by index
    else:
        try:
            packet_proto = str(packet[2]).split(" ")[0]  # Protocol: STP, ICMP, ARP,...
        except:
            packet_proto = None
    size = len(packet)
    # Determine if packet is unicast, multicast, or broadcast
    if dst_mac == "ff:ff:ff:ff:ff:ff":
        packet_type = "Broadcast"
    elif (int(dst_mac.split(":")[0], 16) & 1) == 1:
        packet_type = "Multicast"
    else:
        packet_type = "Unicast"

    # Return dict of info
    return {
        "eth_type": eth_pdu_type,
        "src": src_mac,
        "dst": dst_mac,
        "proto": packet_proto,
        "size": size,
        "cast_type": packet_type,
    }


def compare_mac(mac):
    # TODO: COMPARE EXTRACTED MAC TO LIST
    if mac not in TRUSTED_MACS:
        ...
        # Send mac to AI server
    else:
        print("Trusted Source")


def output(packet):
    # counter for packet number
    global count
    count += 1

    # Get layer 2 info
    l2 = analyzeL2(packet)
    # Put info into table
    l2_table = [
        ["Ethernet Standard:", l2["eth_type"]],
        ["Source MAC Address:", l2["src"]],
        ["Destination MAC Address:", l2["dst"]],
        ["Protocol:", l2["proto"]],
    ]

    # format prints
    print("#" * 30)
    print("#" + f"Packet {count} ({l2['cast_type']})".center(28) + "#")
    print("#" * 30)
    print("-" * 100)
    print("Layer 2 Information")
    print("-" * 100)
    print(tabulate(l2_table, tablefmt="plain"))
    print("-" * 100)


def main():
    sleep(5)
    try:
        while True:
            sniff(count=1, prn=output)
            sleep(60)  # Wait one minute before capturing another packet
    # To ensure that the packet being analyzed is done before ending program
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()