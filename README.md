##  This repo is to build a cloud native solution for auto drain nodes in kubernetes clusters
# Dependency kubernetes metric-server


# How to build the docker image
sudo docker build -t yunshengyan/drainy:drainy .
Sending build context to Docker daemon  92.67kB
Step 1/7 : FROM python:3.8
 ---> 900972ffeecd
Step 2/7 : RUN mkdir -p /app
 ---> Using cache
 ---> 2a03a8bf7df9
Step 3/7 : WORKDIR /app
 ---> Using cache
 ---> abe5ef790e53
Step 4/7 : COPY requirements.txt /app
 ---> Using cache
 ---> 2bfaaebf8e03
Step 5/7 : RUN pip install --no-cache-dir -r requirements.txt
 ---> Using cache
 ---> 5b34377b22ad
Step 6/7 : COPY . /app/
 ---> Using cache
 ---> 635b393ae5a5
Step 7/7 : CMD ["python", "/app/drainy.py"]
 ---> Using cache
 ---> 6bd75b0f30dc
Successfully built 6bd75b0f30dc
Successfully tagged yunshengyan/drainy:drainy

~/drainy$ sudo docker push yunshengyan/drainy:drainy
The push refers to repository [docker.io/yunshengyan/drainy]
ee9d0cba3312: Pushed
02044aac2453: Pushed
1549087263b9: Pushed
6ceb780e90ff: Pushed
1fe0699af9f7: Mounted from library/python
156568a71809: Mounted from library/python
5fca8a94d542: Mounted from library/python
6b183c62e3d7: Mounted from library/python
882fd36bfd35: Mounted from library/python
d1dec9917839: Mounted from library/python
d38adf39e1dd: Mounted from library/python
4ed121b04368: Mounted from library/python
d9d07d703dd5: Mounted from library/python
drainy: digest: sha256:036ddb18c9c28c1769fa2ed4c253673fab4ff5e07e845711d074514966588d93 size: 3052

