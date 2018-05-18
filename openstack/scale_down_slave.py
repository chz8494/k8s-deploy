import os
import openstack.cloud
max_num = 10
Name = 'k8s-slave-'
decrease_num = 2

def find_server(name):    
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes-staging')
    server = conn.get_server(name_or_id= name)  
    return server
def delete_server(name):
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes-staging')
    server = conn.delete_server(name_or_id=name)
    return server

def server_counter(num):
    for i in range(num):
        name = Name + str(i)
        server = find_server(name)
        if not server:           
            return i

try:
    os.remove("/home/ubuntu/kubespray-master/inventory/mycluster/scale_down.cfg")
except OSError:
    pass
with open('/home/ubuntu/kubespray-master/inventory/mycluster/scale_down.cfg', 'a') as the_file:
    the_file.write("[kube-node]\n")
    
num = server_counter(max_num)            
num = num - 1
for i in range(num, num - decrease_num, -1):
    name = Name + str(i)
    with open('/home/ubuntu/kubespray-master/inventory/mycluster/scale_down.cfg', 'a') as the_file:
        the_file.write(name + "\n")

os.system('ansible-playbook -i /home/ubuntu/kubespray-master/inventory/mycluster/scale_down.cfg /home/ubuntu/kubespray-master/remove-node.yml')

for i in range(num, num - decrease_num, -1):
    name = Name + str(i)
    server = delete_server(name)
    print ("server " + name + " deleted!")
