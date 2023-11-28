import paramiko
import random


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
        dr_info = [line.split() for line in ospf_output.splitlines() if "DR" in line]

        # extract dr and br
        dr_router_id = dr_info[0][0]
        bdr_router_id = dr_info[0][2]

        return dr_router_id, bdr_router_id

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
        command = f"interface gig 0/0\nip ospf priority {priority}"
        _, _, stderr = ssh.exec_command(command)

        # error check
        if stderr.read():
            print(f"Error changing priority: {stderr.read().decode()}")
        else:
            print(f"Priority changed for router {router_name}")

    except Exception as e:
        print(f"e")


def main():
    # connect to R1 to find who the DR is
    ssh_session = ssh_con(ROUTERS["R1"]["ip"], USERNAME, PASSWORD)
    dr, bdr = get_dr(ssh_session)
    print(f"Current DR is {dr}")
    new_dr = elect(dr)

    # end current ssh session
    ssh_session.close()
    print("Closed Session with R1")

    print(f"Starting Session with {dr}")
    ssh_session = ssh_con(ROUTERS[dr]["ip"], USERNAME, PASSWORD)
    # dethrone current dr
    throne(ssh_session, dr, "1")
    ssh_session.close()

    # throne new dr
    throne(ssh_session, dr, "100")
    ssh_session.close()


if __name__ == "__main__":
    main()