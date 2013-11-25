#!/usr/bin/python
import shutil
import sys
#from fabric.api import *
import logging
import paramiko 
import os

logging.basicConfig( level=logging.INFO )

#ssh = paramiko.SSHClient()

import sys
import time
import select
import paramiko

host = '192.168.1.5'
i = 1

#
# Try to connect to the host.
# Retry a few times if it fails.
#
while True:
    print "Trying to connect to %s (%i/30)" % (host, i)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host=host,username='default',password='Carb0nDay')
        print "Connected to %s" % host
        break
    except paramiko.AuthenticationException:
        print "Authentication failed when connecting to %s" % host
        sys.exit(1)
    except:
        print "Could not SSH to %s, waiting for it to start" % host
        i += 1
        time.sleep(2)
    
    # If we could not connect within time limit
    if i == 30:
        print "Could not connect to %s. Giving up" % host
        sys.exit(1)

# Send the command (non-blocking)
stdin, stdout, stderr = ssh.exec_command("show mac")

# Wait for the command to terminate
while not stdout.channel.exit_status_ready():
    # Only print data if there is data to read in the channel
    if stdout.channel.recv_ready():
        rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
        if len(rl) > 0:
            # Print data from stdout
            print stdout.channel.recv(1024),

#
# Disconnect from the host
#
print "Command done, closing SSH connection"
ssh.close()

'''
client = paramiko.SSHClient()
client.load_system_host_keys()
client.connect('192.168.1.5', username='default', password='Carb0nDay')
channel = client.get_transport().open_session()
channel.exec_command("show mac")
while True:
    if channel.exit_status_ready():
        break
    rl, wl, xl = select.select([channel], [], [], 0.0)
    if len(rl) > 0:
        print channel.recv(1024)

#ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.connect('192.168.1.5', username='default', password='Carb0nDay')
#stdin, stdout, stderr = ssh.exec_command('show mac')

account = read_login()
conn = SSH2()
conn.connect('192.168.1.5')
conn.login(account)

#conn.execute('show mac')

#type(stdin)
#data=stdout.readlines()
for line in data:
    line.translate(",", " ")
    print line
   

#ssh.exec_command('show mac \n')
env.host_string='192.168.1.5'
env.user='default'
env.password='Carb0nDay'
env.hosts='192.168.1.5'
out=run('set vlan create 2')
#print out
#print data
'''

