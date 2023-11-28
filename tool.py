import paramiko

# a function to establish ssh connection and returns the ssh object
def ssh_con(host, user, psswd):
    try:
        # initialize ssh object thing
        ssh = paramiko.SSHClient()

        # add cipher and algorithm since ssh is strange on the isos
        ssh.get_transport().set_algorithms(["diffie-hellman-group-exchange-sha1"])
        ssh.get_transport().set_ciphers(["aes256-cbc"])

        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)        

        ssh.connect(host, username=user, password=psswd)
        print(f"Established ssh connection to {host}")
        return ssh
    except Exception as e:
        print(e)
        return None


def main():
    host = "192.168.100.1"
    user = "Admin"
    password = "Adm1npa55"
    ssh_session = ssh_con(host, user, password)

if __name__ == "__main__":
    main()