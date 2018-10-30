sudo scp k8s-master-0:/etc/kubernetes/admin.conf /home/ubuntu/.kube/config
git clone https://github.com/chz8494/k8s-nfs -b wt-dev
cd k8s-nfs
kubectl apply -f ./
cd ..
git clone https://source.cloud.google.com/newagent-c06cb/k8s-EFK
cd k8s-EFK
sh run.sh
cd ..
git clone https://github.com/kubernetes/heapster
cd heapster
kubectl create -f deploy/kube-config/influxdb/
kubectl create -f deploy/kube-config/rbac/heapster-rbac.yaml
cd ..
kubectl apply -f admin-user.yml
kubectl apply -f ClusterRoleBinding.yml
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/master/src/deploy/recommended/kubernetes-dashboard.yaml

helm install stable/prometheus -n prometheus --namespace logging
