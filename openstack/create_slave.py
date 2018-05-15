import openstack.cloud
num = 4
Name = 'k8s-slave-'


def find_server(name):    
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes-dev')
    server = conn.get_server(name_or_id= name)  
    return server

def reboot_server(server):
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes-dev')
    conn.compute.reboot_server(server.id,reboot_type="HARD")

def create_server(name):
    conn = openstack.connect(cloud='cbopenstack-admin')
    conn = conn.connect_as_project('Kubernetes-dev')
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
    
for i in range(num):
    name = Name + str(i)
    server = find_server(name)
    if not server:           
        server = create_server(name)
        print ("New slave " + server.name + " has been created, with IP " + server.private_v4)
        reboot_server(server)
    else:
        print ("server " + server.name + " exists!")

