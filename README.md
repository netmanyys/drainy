##  This repo is to build a cloud native solution for auto drain nodes in kubernetes clusters
## Dependency kubernetes metric-server
git clone https://github.com/kodekloudhub/kubernetes-metrics-server.git
cd kubernetes-metrics-server/
kubectl apply -f .

kubectl top nodes
kubectl top pods

## How to build the docker image
sudo docker build -t yunshengyan/drainy:drainy .
sudo docker push yunshengyan/drainy:drainy


## Deploy drainy
kubectl apply -f drainy-rbac.yml
kubectl apply -f drainy-deployment.yml

kubectl -n kube-system get pods | grep drainy