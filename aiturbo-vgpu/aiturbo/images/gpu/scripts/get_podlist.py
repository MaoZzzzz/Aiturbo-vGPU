from kubernetes.client import api_client
from kubernetes.client.api import core_v1_api
from kubernetes.client.api import BatchV1Api
from kubernetes import client, config


class KubernetesTools(object):
    def __init__(self):
        self.k8s_url = 'https://192.168.1.138:6443'

    def get_token(self):
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as file:
            Token = file.read().strip('\n')
            return Token

    def get_api(self):
        configuration = client.Configuration()
        configuration.host = self.k8s_url
        configuration.verify_ssl = False
        configuration.api_key = {"authorization": "Bearer " + self.get_token()}
        client1 = api_client.ApiClient(configuration=configuration)
        api = core_v1_api.CoreV1Api(client1)
        #api = BatchV1Api(client1)
        return api

    def get_namespace_list(self):
        api = self.get_api()
        namespace_list = []
        for ns in api.list_namespace().items:
            # print(ns.metadata.name)
            namespace_list.append(ns.metadata.name)

        return namespace_list

    def get_pod_info(self, namespaces, name):
        api = self.get_api()
        # 示例参数
        resp = api.list_namespaced_pod(
            namespace=namespaces, label_selector='name={name_selector}'.format(name_selector=name)).items
        return resp
        # 详细信息
        for i in range(len(resp)):
            #            print(type(resp[i].to_dict()['status']['container_statuses'][0]))
            temp = resp[i].to_dict()['status']['container_statuses']

    def get_job_info(self, namespaces, job_name):
        api = self.get_api()
        # 示例参数
        resp = api.read_namespaced_job(namespace=namespaces, name=job_name)
        # 详细信息
        return resp


if __name__ == '__main__':
    pod = KubernetesTools().get_pod_info('mzz')
