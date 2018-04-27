#!/bin/bash

source kube-openstack.sh

ansible-playbook -i /home/ubuntu/kubespray-master/inventory/mycluster/scale_up.cfg /home/ubuntu/kubespray-master/scale.yml
