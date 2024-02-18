import paramiko
import os
from io import StringIO

def send_files_to_droplet(droplet_ip, username, password, local_path, remote_path, files):
    """
    Sends files to a Digital Ocean droplet via SSH using an SSH key string.

    Args:
    - droplet_ip (str): IP address of the droplet.
    - username (str): Username for SSH.
    - ssh_private_key_string (str): SSH private key as a string.
    - local_path (str): Local directory containing the files.
    - remote_path (str): Remote directory to send the files to.
    - files (list): List of filenames to be sent.
    """
    print("Initializing SSH client...")
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())



    print(f"Connecting to {droplet_ip}...")
    ssh_client.connect(droplet_ip, username=username, password=password)
    print("Connection established.")
    # Check if remote directory exists, create if not
    print(f"Checking if remote directory {remote_path} exists...")
    stdin, stdout, stderr = ssh_client.exec_command(f'mkdir -p {remote_path}')
    exit_status = stdout.channel.recv_exit_status()  # wait for command to execute
    if exit_status == 0:
        print(f"Directory {remote_path} is ready.")
    else:
        print(f"Error in creating directory {remote_path}: {stderr.read().decode()}")

    print(f"Starting file transfer to {remote_path}...")
    with ssh_client.open_sftp() as sftp_client:
        for file in files:
            local_file = os.path.join(local_path, file)
            remote_file = os.path.join(remote_path, file)
            print(f"Transferring {local_file} to {remote_file}...")
            try:
                sftp_client.put(local_file, remote_file)
                print(f"File {local_file} transferred successfully.")
            except Exception as e:
                print(f"Error transferring file {local_file}: {e}")

    print("All files transferred. Closing connection.")
    ssh_client.close()

# Usage example
send_files_to_droplet(
    droplet_ip='167.99.4.120',
    username='root',
    password='NjTER$6fzjGTt8z',
    local_path='auth/',
    remote_path='/usr/bin/chatbot/auth/',
    #remote_path='/etc/supervisor/conf.d/',
    #files=['supervisord.conf']
    files = ['token.json', 'private.json']
    #files=['yahoo.py', 'run_chatbot.sh']
    #files=['yahoo.py', 'requirements.txt', '.env' , 'groupme.py']
)
#services\baseball_bot\auth\private.json