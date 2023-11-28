import paramiko
import random
import time


# define some constants
ROUTER_NAMES = ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"]
ROUTERS = {
    "R1":{"ip" : "192.168.100.1", "id" : "1.1.1.1"},
    "R2":{"ip" : "192.168.100.2", "id" : "1.1.1.2"},
    "R3":{"ip" : "192.168.100.3", "id" : "1.1.1.3"},
    "R4":{"ip" : "192.168.100.4", "id" : "1.1.1.4"},
    "R5":{"ip" : "192.168.100.5", "id" : "1.1.1.5"},
    "R6":{"ip" : "192.168.100.6", "id" : "1.1.1.6"},
    "R7":{"ip" : "192.168.100.7", "id" : "1.1.1.7"},
    "R8":{"ip" : "192.168.100.8", "id" : "1.1.1.8"},
           }
USERNAME = "Admin"
PASSWORD = "Adm1npa55"


# a function to establish ssh connection and returns the ssh object
def ssh_con(host, user, psswd):
    try:
        # add cipher and algorithm since ssh is strange on the isos
        paramiko.Transport._preferred_ciphers = ("aes256-cbc", )
        paramiko.Transport._preferred_kex = ("diffie-hellman-group-exchange-sha1", )

        # initialize ssh object thing
        ssh = paramiko.SSHClient()

        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)    

        ssh.connect(host, username=user, password=psswd, allow_agent=False, look_for_keys=False)
        print(f"Established ssh connection to {host}")
        return ssh
    except Exception as e:
        print(e)
        return None


def get_dr(ssh):
    try:
        # get ospf neighbors
        _, stdout, _ = ssh.exec_command("show ip ospf neighbor")

        # parse output
        ospf_output = stdout.read().decode()
        dr_info = [line.split() for line in ospf_output.splitlines() if "FULL" in line]

        # extract dr
        dr = ""
        bdr = ""
        for x in dr_info:
            if x[2] == "FULL/DR":
                dr = x[0]
            elif x[2] == "FULL/BDR":
                bdr = x[0]

        return dr, bdr 

    except Exception as e:
        print(e)
        return None, None
    

# function to choose a random new router to become dr (except the currently elected dr)
def elect(ugly):
    candidates = [i for i in ROUTER_NAMES if i != ugly] # copies all routers except current dr
    return random.choice(candidates)



# function to throne or dethrone routers
def throne(ssh, router_name, priority):
    try:
        # configure OSPF router priority
        connection = ssh.invoke_shell()
        connection.send("enable\n")
        time.sleep(.5)
        connection.send("Arwa123@enable\n")
        time.sleep(.5)
        connection.send("conf t\n")
        time.sleep(.5)
        connection.send("int gig 0/0\n")
        time.sleep(.5)
        connection.send(f"ip ospf priority {priority}\n")
        time.sleep(.5)
        connection.close()

        print(f"Priority of {router_name} changed")

    except Exception as e:
        print(e)

# get router name from id
def id_to_name(id):
    for name, data in ROUTERS.items():
        if data["id"] == id:
            return name


# function to reset ospf process
def reset_ospf_process(ssh):
    try:
        # reset ospf process
        connection = ssh.invoke_shell()
        connection.send("enable\n")
        time.sleep(.5)
        connection.send("Arwa123@enable\n")
        time.sleep(.5)
        connection.send("clear ip ospf process\n")
        time.sleep(.5)
        connection.send("y\n")
        # wait 30 seconds for advertisement process
        print("Waiting 30 seconds...")
        time.sleep(30)
        connection.close()
        print("OSPF process reset")

    except Exception as e:
        print(e)


def main():
    # connect to R1 to find who the DR is
    ssh_session = ssh_con(ROUTERS["R1"]["ip"], USERNAME, PASSWORD)
    dr, bdr = get_dr(ssh_session)
    # if no dr found then R1 is the dr
    if dr:
        dr = id_to_name(dr)
    else:
        dr = "R1"
    # if no bdr found then R1 is the bdr
    if bdr:
        bdr = id_to_name(bdr)
    else:
        bdr = "R1"
    print(f"Current DR is {dr}")
    print(f"Current BDR is {bdr}")

    new_dr = elect(dr)
    print(f"New DR is {new_dr}")

    # end current ssh session
    ssh_session.close()
    print("Closed Session with R1")
    
    # throne new dr
    ssh_session = ssh_con(ROUTERS[new_dr]["ip"], USERNAME, PASSWORD)
    throne(ssh_session, new_dr, "255")
    ssh_session.close()

    # reset ospf for new dr
    ssh_session = ssh_con(ROUTERS[new_dr]["ip"], USERNAME, PASSWORD)
    reset_ospf_process(ssh_session)
    ssh_session.close()
    
    # dethrone current dr
    ssh_session = ssh_con(ROUTERS[dr]["ip"], USERNAME, PASSWORD)
    throne(ssh_session, dr, "1")
    ssh_session.close()

    # reset ospf for dr
    ssh_session = ssh_con(ROUTERS[dr]["ip"], USERNAME, PASSWORD)
    reset_ospf_process(ssh_session)
    ssh_session.close()

    # reset ospf for bdr
    ssh_session = ssh_con(ROUTERS[bdr]["ip"], USERNAME, PASSWORD)
    reset_ospf_process(ssh_session)
    ssh_session.close()

    


if __name__ == "__main__":
    main()