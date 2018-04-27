#!/bin/bash

ansible-playbook -i /home/ubuntu/kubespray-master/inventory/mycluster/scale_down.cfg /home/ubuntu/kubespray-master/remove-node.yml
