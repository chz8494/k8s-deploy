
import openstack.cloud

Name = 'k8s-slave-2'

def find_server(name):    
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes')
    server = conn.get_server(name_or_id= name)  
    return server

conn = openstack.connect(cloud='cbopenstack-admin')
conn = conn.connect_as_project('Kubernetes')
server=find_server(Name)
conn.compute.reboot_server(server.id,reboot_type="HARD")
