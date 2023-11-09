from asyncio import Task
import sys
import os
import time
import requests
import socket
import subprocess
import threading
import logging
from get_podlist import KubernetesTools

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

ROLE = os.getenv("ROLE")

HOST_NAME = os.getenv("HOSTNAME")  # exported by k8s
HOST_IP = socket.gethostbyname(HOST_NAME)
NUM_WORKER = os.getenv("NUM_WORKER")
NUM_SERVER = os.getenv("NUM_SERVER")

JOB_NAME = os.getenv("JOB_NAME")
TASK_ID = os.getenv("TASK")

PROG = os.getenv("PROG")  # the python main file starting training
WORK_DIR = os.getenv("WORK_DIR")
NUM_STEP = os.getenv("NUM_STEP")
GPU_FREC = os.getenv("GPU_FREC")
BATCH_SIZE = os.getenv("BATCH_SIZE")
MODEL_NAME = os.getenv("MODEL_NAME")
DATASETS = os.getenv("DATASETS")
DATA_DIR_CIFAR = os.getenv("DATA_DIR_CIFAR")


def is_all_running(podlist):
    '''
    check whether all pods are running
    '''
    running = 0
    for i in range(len(podlist)):
        temp = podlist[i].to_dict()['status']['container_statuses']
        if temp == None:
            break
        for j in range(len(temp)):
            if('running' not in temp[j]['state']):
                running = 1
                break
    logging.info("waiting for pods running")
    if running == 0:
        return True
    else:
        return False


def is_not_none(ps_map, worker_map):
    '''
    check if ip array is empty
    '''
    running = 0
    for i in range(len(ps_map)):
        if ps_map.get(i) is None:
            running = 1
            break
    for j in range(len(worker_map)):
        if worker_map.get(j) is None:
            running = 1
            break
    logging.info("waiting for ip")
    if running == 0 and len(ps_map) == int(NUM_SERVER) and len(worker_map) == int(NUM_WORKER):
        return True
    else:
        return False


def get_map_ps(podlist):
    '''
    get ps pod <ip, id> mapping
    '''
    IPs = []
    for i in range(len(podlist)):
        if (podlist[i].to_dict()['metadata']['labels']['job'] == 'ps'):
            IPs.append(podlist[i].to_dict()['status']['pod_ip'])
    map = {}
    for i in range(len(IPs)):
        map[i] = IPs[i]
    return map


def get_map_worker(podlist):
    '''
    get worker pod <ip, id> mapping
    '''
    IPs = []
    for i in range(len(podlist)):
        if (podlist[i].to_dict()['metadata']['labels']['job'] == 'worker'):
            IPs.append(podlist[i].to_dict()['status']['pod_ip'])
    map = {}
    for i in range(len(IPs)):
        map[i] = IPs[i]
    return map


def main():
    global ROLE

    logging.info("starting script ...")

    # interprete command

    cmd = ""
    cmd = "python " + PROG
    # logging.info(GPU_FREC)
    # if float(GPU_FREC) < 1.0:
    #     cmd = "python " + PROG
    # else:
    #     cmd = "CUDA_VISIBLE_DEVICES=0,1 python " + PROG
    # cmd = "python " + PROG
    if ROLE == 'ps':
        cmd = cmd + " " + "--local_parameter_device=cpu"
    else:
        cmd = cmd + " " + "--local_parameter_device=gpu"
        g = str(int(float(GPU_FREC)))
        cmd = cmd + " " + "--num_gpus={gpu_frec}".format(gpu_frec=g)
        # if float(GPU_FREC) < 1.0:
        #     cmd = cmd + " " + "--gpu_memory_frac_for_testing={gpu_frec}".format(gpu_frec=GPU_FREC)
        # else:
        #     g = str(int(float(GPU_FREC)))
        #     cmd = cmd + " " + "--num_gpus={gpu_frec}".format(gpu_frec=g)
    if BATCH_SIZE is not None and BATCH_SIZE != '':
        cmd = cmd + " " + "--batch_size" + "=" + BATCH_SIZE
    if MODEL_NAME is not None:
        cmd = cmd + " " + "--model" + "=" + MODEL_NAME
    if ROLE is not None:
        cmd = cmd + " " + "--job_name" + "=" + ROLE
    if NUM_STEP is not None:
        cmd = cmd + " " + "--num_batches" + "=" + NUM_STEP
    if TASK_ID is not None:
        cmd = cmd + " " + "--task_index" + "=" + TASK_ID
    cmd = cmd + " " + "--use_unified_memory=True"
    cmd = cmd + " " + "--variable_update=parameter_server"

    env = os.environ.copy()

    # check pod status
    podlist = KubernetesTools().get_pod_info('mzz', JOB_NAME)
    logging.debug(str(podlist))

    while not is_all_running(podlist):
        time.sleep(1)
        podlist = KubernetesTools().get_pod_info('mzz', JOB_NAME)

    ps_map = get_map_ps(podlist)
    worker_map = get_map_worker(podlist)

    while not is_not_none(ps_map, worker_map):
        time.sleep(1)
        ps_map = get_map_ps(
            podlist=KubernetesTools().get_pod_info('mzz', JOB_NAME))
        worker_map = get_map_worker(
            podlist=KubernetesTools().get_pod_info('mzz', JOB_NAME))
    logging.info("PS IP: " + str(ps_map))
    logging.info("WORKER IP: " + str(worker_map))

    ps = "--ps_hosts="
    worker = "--worker_hosts="
    for i in range(int(NUM_SERVER)):
        ps = ps + ps_map.get(i) + ":2002"
        if i != int(NUM_SERVER) - 1:
            ps = ps + ","
    for i in range(int(NUM_WORKER)):
        worker = worker + worker_map.get(i) + ":2002"
        if i != int(NUM_WORKER) - 1:
            worker = worker + ","
    cmd = cmd + " " + ps + " " + worker
    cmd = cmd + " " + "--display_every=1"
    if DATASETS == 'cifar10':
        cmd = cmd + " " + "--data_name" + "=" + "cifar10"
        cmd = cmd + " " + "--data_dir" + "=" + DATA_DIR_CIFAR
    cmd = cmd + " --train_dir=/data" + " --save_model_secs=20"
    # if ROLE == "worker" and TASK_ID == "0":
    #     pass
    # else:
    #     cmd = cmd + " >> " + WORK_DIR + "training.txt"
    logging.info("cmd: " + cmd)

    env['NUM_WORKER'] = NUM_WORKER
    env['NUM_WORKER'] = NUM_SERVER
    # start ps/worker
    if ROLE == "ps":
        ROLE = "server"
    env['DMLC_ROLE'] = ROLE
    os.system(cmd)
    logging.info("Task finished successfully!")


if __name__ == '__main__':
    if len(sys.argv) != 1:
        print("Description: Tensorflow start script in k8s cluster")
        print("Usage: python start.py")
        sys.exit(1)
    main()