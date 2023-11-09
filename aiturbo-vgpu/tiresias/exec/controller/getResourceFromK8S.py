import os
import sys


class Node(object):
    '''Node description.
    Parameters
    ----------
    id: int
    num_ps: int
    num_worker: int
    other parameters: string or list of strings
    work to be done on Tuesday 8/8/2017: 
            (1) modify template file, worker and server mount different dirs
            (2) modify template file, set work_dir and export it as an env
            (3) add support for gpu and get_progress() if necessary
    '''

    def __init__(self, node_name) -> None:
        '''
        initialize a node
        '''
        self.cpu = 0
        self.gpu = 0
        self.gmem = 0

        self.node_name = node_name

    def setProperty(self, cpu, gpu, gmem) -> None:
        '''
        set parameters for a node
        '''
        self.cpu = cpu
        # self.memory = memory
        self.gpu = gpu
        self.gmem = gmem

    def getProperty(self) -> list:
        '''
        get parameters from a node
        '''
        result = [self.cpu, self.gpu, self.gmem]
        return result

    def getName(self) -> str:
        '''
        get name from a node
        '''
        return self.node_name


def readFromK8s(node: Node) -> list:
    '''
    get the remain resource of a node
    '''
    total_property = []
    used_property = []
    property_flag = 0
    used_property_flag = 0
    path = "/home/tank/maozz/test/exec/systemData/{node_name}.txt".format(
        node_name=node.getName())

    cmd = "sudo kubectl describe node {node_name}".format(
        node_name=node.getName())
    cmd = cmd + " > " + path
    os.system(cmd)

    for line in open(path):
        if property_flag != 0 and len(total_property) < 9:
            total_property.append(line.split(" ")[-1].replace("\n", ''))
        if line.split(" ")[0] == "Capacity:\n":
            property_flag = 1
        if len(total_property) == 8:
            break

    for line in open(path):
        if used_property_flag != 0 and len(used_property) < 11:
            used_property.append(line.split(" ")[-1].replace("\n", ''))
        if line.split(" ")[0] == "Allocated" and line.split(" ")[1] == "resources:\n":
            used_property_flag = 1
        if len(used_property) == 10:
            break
    
    # for line in open(path):
    #     if used_property_flag != 0 and len(used_property) < 11:
    #         a = line.split(" ")
    #         b = []
    #         for i in range(len(a)):
    #             if a[i] != '':
    #                 b.append(a[i])
    #         if b[0] == 'cpu' or b[0] == 'memory':
    #             used_property.append(b[3].replace("\n",''))
    #         if b[0] == 'tencent.com/vcuda-core' or b[0] == 'tencent.com/vcuda-memory':
    #             used_property.append(b[2].replace("\n",''))
    #     # if line.split(" ")[0] == "Allocated" and line.split(" ")[1] == "resources:\n":
    #     #     used_property_flag = 1
    #     if line.split(" ")[0] == "Allocatable:\n":
    #         used_property_flag = 1
    #     if len(used_property) == 10:
    #         break

    # print(used_property)
    # used_property[0] = used_property[0][:-1]
    # used_property[1] = used_property[1][:-2]
    return total_property, used_property


def init_node() -> Node:
    master = Node("kube-master")
    total_property_master, used_property_master = readFromK8s(master)
    master.setProperty(int(total_property_master[0]) - int(used_property_master[0]) , int(total_property_master[-2]) - int(used_property_master[-2]), int(total_property_master[-1]) - int(used_property_master[-1]))
    # master.setProperty(int(used_property_master[0]), int(used_property_master[-2]), int(used_property_master[-1]))

    node1 = Node("kube-node1")
    total_property, used_property_node1 = readFromK8s(node1)
    node1.setProperty(int(total_property[0]) - int(used_property_node1[0]) , int(total_property[-2]) - int(used_property_node1[-2]), int(total_property[-1]) - int(used_property_node1[-1]))
    # node1.setProperty(int(used_property_node1[0]), int(used_property_node1[-2]), int(used_property_node1[-1]))

    nodes = Node("all")
    nodes.setProperty(master.cpu+node1.cpu, master.gpu +
                      node1.gpu, master.gmem+node1.gmem)
    return nodes


def main():
    master = Node("kube-master")
    total_property, used_property = readFromK8s(master)
    print(total_property)
    print(used_property)
    master.setProperty(property[0], property[4], property[6], property[7])
    print(master.cpu + " " + master.gpu)
    pass


if __name__ == '__main__':
    main()
