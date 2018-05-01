#!/usr/bin/env python
import os
import time
import json
import subprocess
import openstack.cloud
from slackclient import SlackClient
max_num = 6
min_num = 3   #minium 3 servers in total, to make sure staefull pods working
Name = 'k8s-slave-'
SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
sc = SlackClient(SLACK_TOKEN)

def find_server(name):    
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes')
    server = conn.get_server(name_or_id= name)  
    return server
def delete_server(name):
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes')
    server = conn.delete_server(name_or_id=name)
    return server

def server_counter():
    for i in range(max_num):
        name = Name + str(i)
        server = find_server(name)
        if not server:           
            return i 
        elif server and (i == max_num - 1):
            return max_num

def reboot_server(server):
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes')
    conn.compute.reboot_server(server.id,reboot_type="HARD")

def create_server(name):
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes')
    network = conn.network.find_network('kubernetes')
    flavor = conn.compute.find_flavor('k8s-slave')
    image = conn.compute.find_image('Kubernetes')
    userdata = '''#cloud-config
        disable_root: 0
        '''
    server = conn.create_server(
        name= name, image=image.id, flavor=flavor.id, key_name='Lab', userdata=userdata, terminate_volume=True,
                config_drive=True, boot_from_volume=True, network= network.id, wait=True, auto_ip=False)  

    server = conn.compute.wait_for_server(server)
    return server    

def scale_up(num):
    try:
        os.remove("/home/ubuntu/bot/k8s/scale_up.cfg")
    except OSError:
        pass
    with open('/home/ubuntu/bot/k8s/scale_up.cfg', 'a') as f:
        f.write("[kube-node]\n")
    
    for i in range(num + 1):
        name = Name + str(i)
        server = find_server(name)
        if not server:           
            server = create_server(name)
            print ("New slave " + server.name + " has been created, with IP " + server.private_v4)
            reboot_server(server)
            with open('/home/ubuntu/bot/k8s/scale_up.cfg', 'a') as f:
                f.write(server.name+"\n")
        else:
            print ("server " + server.name + " exists!")
            with open('/home/ubuntu/bot/k8s/scale_up.cfg', 'a') as f:
                f.write(server.name + "\n")
    
    time.sleep(30)
                
    with open('/home/ubuntu/bot/k8s/scale_up.cfg', 'r') as f:
        content = f.readlines()
        for line in content:
            os.system('sudo ssh 10.240.105.29 ping -c 5 ' + line)
                
    time.sleep(30)
    
    with open('/home/ubuntu/k8s-deploy/openstack/scale_temp.txt', 'r') as f:
        content = f.read()
        with open('/home/ubuntu/bot/k8s/scale_up.cfg', 'a') as f:
            f.write(content)
    os.system('sudo scp /home/ubuntu/bot/k8s/scale_up.cfg 10.240.105.29://home/ubuntu/kubespray-master/inventory/mycluster/scale_up.cfg')
    os.system('sudo ssh 10.240.105.29 ansible-playbook -i /home/ubuntu/kubespray-master/inventory/mycluster/scale_up.cfg /home/ubuntu/kubespray-master/scale.yml')

def scale_down(num):  
    num = num - 1
    name = Name + str(num)
    os.system('sudo ssh ubuntu@10.240.105.29 kubectl delete node ' + name)
    server = delete_server(name)
#    print ("server " + name + " deleted!")

def auto_scale(num):
    cpu = []
    ram = []
    for i in range(num):
        name = Name + str(i)
        cpu_request = int(subprocess.check_output(['sudo ssh ubuntu@10.240.105.29 kubectl describe node ' + name + "  | grep Allocated -A 5 | grep -ve Event -ve Allocated -ve percent -ve -- -ve CPU | awk '{print $2}'| grep -Eo '[0-9]{1,3}'"],shell="true"))
        ram_request = int(subprocess.check_output(['sudo ssh ubuntu@10.240.105.29 kubectl describe node ' + name + "  | grep Allocated -A 5 | grep -ve Event -ve Allocated -ve percent -ve -- -ve CPU | awk '{print $6}'| grep -Eo '[0-9]{1,3}'"],shell="true"))
        cpu.append(cpu_request)
        ram.append(ram_request)

    total_cpu = sum(cpu)/num
    total_ram = sum(ram)/num
    fields = [
        {
        'title': 'Average CPU Request',
        'value': total_cpu,
        'short': True
        },
        {
        'title': 'Average RAM Request',
        'value': total_ram,
        'short': True
        }
    ]
    attachments = [
        {
            'fallback': 'Total Slave Resource Usage' ,
            'title': 'Total Slave Resource Usage',
            'fields': fields
        }
    ]
    if (total_cpu > 60) or (total_ram > 60):
        sc.api_call(
            'chat.postMessage',
            channel='logs',
    #        username=SLACK_USERNAME,
    #        icon_url=SLACK_ICON,
            text='cluster does not have enough resource, starting auto cluster scaling!',
            attachments=json.dumps(attachments)
        )
        return scale_up(num)
   
    if (total_cpu < 40) or (total_ram < 40):
        sc.api_call(
            'chat.postMessage',
            channel='logs',
    #        username=SLACK_USERNAME,
    #        icon_url=SLACK_ICON,
            text='Cluster has too much free resource, starting auto cluster downsizing!',
            attachments=json.dumps(attachments)
        )
        return scale_down(num)
    

num = server_counter()
if min_num < num <= max_num - 1:    
    auto_scale(num)
