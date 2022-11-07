#!/usr/bin/env python
from kubernetes import client, config
import time


class Drainy:
    """
    This Drainy class is to auto-drain a faulty node as self-healing solution
    """
    def __init__(self):
        config.load_incluster_config()
        self.session = client.CoreV1Api() 
    
    def node_cpu_capacity(self, node_name):
        return int(self.session.read_node_status(node_name).status.capacity['cpu'])

    def show_node(self, node_name):
        return self.session.read_node_status(node_name)

    def delete_pod(self, name, namespace):
        try:
            delete_options = client.V1DeleteOptions()
            api_response = self.session.delete_namespaced_pod(
                name=name,
                namespace=namespace,
                body=delete_options)
            # print(api_response)
        except Exception as e:
            print("Exception: Drainy:delete_pod {}".format(e))   

    def cordon_node(self, node_name):
        try:
            body = {
                "spec": {
                    "unschedulable": True,
                },
            }
            self.session.patch_node(node_name, body)
            print("{} has been cordoned!".format(node_name))
        except Exception as e:
            print("Exception: Drainy:cordon_node {}".format(e))   

    def uncordon_node(self, node_name):
        try:
            body = {
                "spec": {
                    "unschedulable": False,
                },
            }
            self.session.patch_node(node_name, body)
            print("{} has been uncordoned!".format(node_name))
        except Exception as e:
            print("Exception: Drainy:uncordon_node {}".format(e))    

    def drain_node(self, node_name):
        try:
            self.cordon_node(self.session, node_name)
            # field selectors are a string, you need to parse the fields from the pods here
            field_selector = 'spec.nodeName='+node_name
            pods = self.session.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
            for i in pods.items:
                print("Going to delete pod %s\t%s\t%s" %
                    (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
                self.delete_pod(self.session, name=i.metadata.name, namespace=i.metadata.namespace)
            print("{} has been drained!".format(node_name))
        except Exception as e:
            print("Exception: Drainy:drain_node {}".format(e))       

    def drain_high_cpu_node(self):
        try:
            api = client.CustomObjectsApi()
            k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
            
            for stats in k8s_nodes['items']:
                # print("Node Name: %s\tCPU: %f\tMemory: %s" % (stats['metadata']['name'], float(stats['usage']['cpu'][:-1]) / (1000000000.0 * core_num) * 100, stats['usage']['memory']))
                node_name = stats['metadata']['name']
                core_num = self.node_cpu_capacity(node_name)
                cpu_usage = float(stats['usage']['cpu'][:-1]) / (1000000000.0 * core_num) * 100
                if cpu_usage > 80:
                    print("{} cpu usage is way too high!".format(stats['metadata']['name']))
                    self.drain_node(node_name)
        except Exception as e:
            print("Exception: Drainy:drain_high_cpu_node {}".format(e))

def main():
    try:
        d = Drainy()
        d.drain_high_cpu_node()
    except Exception as e:
        print("Exception: main {}".format(e))
    
if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)
