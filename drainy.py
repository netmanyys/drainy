#!/usr/bin/env python
from kubernetes import client, config
import time



def node_cpu_capacity(session, node_name):
    return int(session.read_node_status(node_name).status.capacity['cpu'])

def show_node(session, node_name):
    return session.read_node_status(node_name)

def delete_pod(session, name, namespace):
    delete_options = client.V1DeleteOptions()
    api_response = session.delete_namespaced_pod(
        name=name,
        namespace=namespace,
        body=delete_options)
    # print(api_response)

def cordon_node(session, node_name):
    body = {
        "spec": {
            "unschedulable": True,
        },
    }
    session.patch_node(node_name, body)
    print("{} has been cordoned!".format(node_name))

def uncordon_node(session, node_name):
    body = {
        "spec": {
            "unschedulable": False,
        },
    }
    session.patch_node(node_name, body)
    print("{} has been uncordoned!".format(node_name))

def drain_node(session, node_name):

    cordon_node(session, node_name)
    # field selectors are a string, you need to parse the fields from the pods here
    field_selector = 'spec.nodeName='+node_name
    pods = session.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
    for i in pods.items:
        print("Going to delete pod %s\t%s\t%s" %
              (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
        delete_pod(session, name=i.metadata.name, namespace=i.metadata.namespace)
    print("{} has been drained!".format(node_name))


def drain_high_cpu_node(session):
    config.load_kube_config()

    api = client.CustomObjectsApi()
    k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    
    for stats in k8s_nodes['items']:
        # print("Node Name: %s\tCPU: %f\tMemory: %s" % (stats['metadata']['name'], float(stats['usage']['cpu'][:-1]) / (1000000000.0 * core_num) * 100, stats['usage']['memory']))
        node_name = stats['metadata']['name']
        core_num = node_cpu_capacity(session, node_name)
        cpu_usage = float(stats['usage']['cpu'][:-1]) / (1000000000.0 * core_num) * 100
        if cpu_usage > 80:
            print("{} cpu usage is way too high!".format(stats['metadata']['name']))
            drain_node(session, node_name)

   
def main():
    # it works only if this script is run by K8s as a POD
    config.load_incluster_config()
    # use this outside pods
    # config.load_kube_config()

    # grab the node name from the pod environment vars
    # node_name = os.environ.get('MY_NODE_NAME', None)
    session = client.CoreV1Api() 
    drain_high_cpu_node(session)
    
if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)
