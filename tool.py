import paramiko

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


def main():
    host = "192.168.100.1"
    user = "Admin"
    password = "Adm1npa55"
    ssh_session = ssh_con(host, user, password)

if __name__ == "__main__":
    main()