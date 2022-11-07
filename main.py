#    Copyright [netmanyys / Yunsheng Yan] 

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

#!/usr/bin/env python

from kubernetes import client, config
from datetime import datetime
import threading
import time
from settings import CPU_THRESHOLD ,SUSPEND_AFTER_DRAIN

def time_now():
    return datetime.now().strftime("%H:%M:%S")

class Drainy:
    """
    This Drainy class is to auto-drain a faulty node as self-healing solution
    """
    def __init__(self):
        config.load_incluster_config()
        self.session = client.CoreV1Api() 
        self.drained = dict()
    
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
            print("{} Exception: Drainy:delete_pod {}".format(time_now(),e))   

    def cordon_node(self, node_name):
        try:
            body = {
                "spec": {
                    "unschedulable": True,
                },
            }
            self.session.patch_node(node_name, body)
            print("{} {} has been cordoned!".format(time_now(), node_name))
        except Exception as e:
            time_frame = datetime.now().strftime("%H:%M:%S")
            print("{} Exception: Drainy:cordon_node {}".format(time_now(),e))   

    def uncordon_node(self, node_name):
        try:
            body = {
                "spec": {
                    "unschedulable": False,
                },
            }
            self.session.patch_node(node_name, body)
            print("{} {} has been uncordoned!".format(time_now(), node_name))
        except Exception as e:
            print("{} Exception: Drainy:uncordon_node {}".format(time_now(), e))    

    def drain_node(self, node_name):
        try:
            self.cordon_node(node_name)
            # field selectors are a string, you need to parse the fields from the pods here
            field_selector = 'spec.nodeName='+node_name
            pods = self.session.list_pod_for_all_namespaces(watch=False, field_selector=field_selector)
            for i in pods.items:
                print("{} Going to delete pod {}\t{}\t{}".format(time_now(), i.status.pod_ip, i.metadata.namespace, i.metadata.name))
                self.delete_pod(name=i.metadata.name, namespace=i.metadata.namespace)
            print("{} {} has been drained!".format(time_now(), node_name))
        except Exception as e:
            print("{} Exception: Drainy:drain_node {}".format(time_now(),e))       

    def is_drained(self, node):
        if node in self.drained and self.drained[node]:
            return True
        else:
            return False
    def ttl_key_remove(self, key, ttl):
        try:
            time.sleep(ttl)
            if key in self.drained:
                self.drained.pop(key)
        except Exception as e:
            print("{} Exception: Drainy:ttl_key_remove {}".format(time_now(), e))            

    def drain_high_cpu_node(self):
        try:
            api = client.CustomObjectsApi()
            k8s_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
            
            for stats in k8s_nodes['items']:
                node_name = stats['metadata']['name']
                core_num = self.node_cpu_capacity(node_name)
                cpu_usage = float(stats['usage']['cpu'][:-1]) / (1000000000.0 * core_num) * 100
                if cpu_usage > CPU_THRESHOLD:
                    print("{} {} cpu usage is way too high!".format(time_now(), node_name))
                    if not self.is_drained(node_name):
                        # will only drain a node if it has not been drained
                        self.drained[node_name] = True
                        # After 10min(600 sec), remove node_name from self.drained dict
                        # This can avoid frequent drain to one particular node in 10 mins
                        t = threading.Thread(target=self.ttl_key_remove, args=(node_name, SUSPEND_AFTER_DRAIN))
                        t.start()
                        self.drain_node(node_name)

        except Exception as e:
            print("{} Exception: Drainy:drain_high_cpu_node {}".format(time_now(), e))

def main():
    try:
        d = Drainy()
        while True:
            d.drain_high_cpu_node()
            time.sleep(60)
    except Exception as e:
        print("{} Exception: main {}".format(time_now(), e))
    
if __name__ == '__main__':
    main()

