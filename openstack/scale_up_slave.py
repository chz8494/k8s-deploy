import os
import time
import paramiko
import openstack.cloud
max_num = 10
Name = 'k8s-slave-'
increase_num = 2

def find_server(name):    
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes')
    server = conn.get_server(name_or_id= name)  
    return server

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
        name= name, image=image.id, flavor=flavor.id, key_name='Lab', userdata=userdata,
                config_drive=True, boot_from_volume=True, network= network.id, wait=True, auto_ip=False)  

    server = conn.compute.wait_for_server(server)
    return server    

def server_counter(num):
    for i in range(num):
        name = Name + str(i)
        server = find_server(name)
        if not server:           
            return i
            
try:
    os.remove("/home/ubuntu/bot/k8s/scale_up.cfg")
except OSError:
    pass
with open('/home/ubuntu/bot/k8s/scale_up.cfg', 'a') as f:
    f.write("[kube-node]\n")

num = server_counter(max_num)
for i in range(num + increase_num):
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
