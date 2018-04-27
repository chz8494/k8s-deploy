import os
import  paramiko
with open('/home/ubuntu/kubespray-master/inventory/mycluster/scale_up.cfg', 'r') as f:
    content = f.readlines()
    for line in content:
        try:
            client = paramiko.SSHClient()
            client.load_system_host_keys()
            print line
            a=client.connect(line)
            print a
        except Exception as e:
#            os.system('ping -c 5 ' + line)
            print e
