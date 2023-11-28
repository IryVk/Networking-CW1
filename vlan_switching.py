import time

from tool import ssh_con, USERNAME, PASSWORD


SWITCH = "192.168.100.10"
## WARNING: changing the vlans breaks the switch 


def switch_vlan(ssh, vlan):
    try:
        # switch the vlan to chosen vlan
        connection = ssh.invoke_shell()
        connection.send("enable\n")
        time.sleep(.5)
        connection.send("Arwa123@enable\n")
        time.sleep(.5)
        connection.send("conf t\n")
        time.sleep(.5)

        connection.send("int range gig 0/0-3\n")
        time.sleep(.5)
        connection.send(f"switchport access vlan {vlan}\n")

        connection.send("int range gig 1/0-3\n")
        time.sleep(.5)
        connection.send(f"switchport access vlan {vlan}\n")

        connection.send("int gig 2/0\n")
        time.sleep(.5)
        connection.send(f"switchport access vlan {vlan}\n")

        ## some prints to debug
        # time.sleep(.5)
        # outpt = connection.recv(65535)
        # time.sleep(.5)
        # print(str(outpt))

        time.sleep(.5)
        connection.close()

        print(f"Vlan Changed!")

    except Exception as e:
        print(e)


def main():
    # ask user what vlan they want to change to (please use 50)
    vlan = input("What vlan would you like to change to?(10, 20, 30, 50) ").strip()
    if vlan not in ["10", "20", "30", "50"]:
        print("Invalid VLAN")
        return
    
    ssh_session = ssh_con(SWITCH, USERNAME, PASSWORD)
    switch_vlan(ssh_session, vlan)

    ssh_session.close()


if __name__ == "__main__":
    main()
