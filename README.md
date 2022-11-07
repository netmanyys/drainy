Drainy is a cloud native solution for auto drain nodes in kubernetes clusters
### Dependency kubernetes metric-server
```
git clone https://github.com/kodekloudhub/kubernetes-metrics-server.git
cd kubernetes-metrics-server/
kubectl apply -f .

kubectl top nodes
kubectl top pods
```

### How to build the docker image
```
sudo docker system prune -a # type y
version-id=0.8
sudo docker build -t yunshengyan/drainy:$version-id .
sudo docker push yunshengyan/drainy:$version-id
```

### Deploy drainy
```
kubectl apply -f drainy-rbac.yml
kubectl apply -f drainy-deployment.yml
kubectl -n kube-system get pods | grep drainy
```