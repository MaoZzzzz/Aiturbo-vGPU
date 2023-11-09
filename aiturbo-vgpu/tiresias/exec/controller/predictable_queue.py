import sys
import las_queue

sys.path.append('/home/tank/maozz/tiresias/exec/predictable_model')

import predict_model
from resources_define import Job


model_name_1 = ["vgg16", "vgg19", "lenet", "overfeat", "alexnet", "resnet50", "mobilenet"]
model_name_2 = ["vgg11", "googlenet", "trivial", "inception3","inception4", "resnet101", "resnet152"]

gpu_comp_cpu = 10
cpu_core_per_pod = 5

# predictable work but not tuned yet
adjust_ready_queue = []
service_queue = []


def adjust_job_finish(job_id) -> None:
    '''
    remove job from adjust queue
    '''
    global LAS_queue_total_job_number

    flag = []
    for i in range(len(adjust_ready_queue)):
        if str(job_id) == str(adjust_ready_queue[i].id):
            flag.append(i)

    for i in range(len(flag)-1, -1, -1):
        del adjust_ready_queue[flag[i]]
    flag.clear()


def calculate_service(job) -> float:
    '''
    calculate the current number of services
    '''
    service = (int(job.gpu_num) / 100) * int(gpu_comp_cpu) + \
        (int(job.worker_num) + int(job.ps_num)) * int(cpu_core_per_pod)
    return service


def calculate_service_queue() -> None:
    '''
    consolidate all jobs by number of services
    '''
    for i in range(len(las_queue.LAS_CPU)):
        service_queue.append(las_queue.LAS_CPU[i])

    for i in range(len(las_queue.LAS_GPU)):
        service_queue.append(las_queue.LAS_GPU[i])

    for i in range(len(adjust_ready_queue)):
        service_queue.append(adjust_ready_queue[i])

    service_queue.sort(key=lambda job: float(job.service_get))


def calculate_sort_position() -> None:
    '''
    TODO
    '''
    for i in range(len(service_queue)):
        service_queue[i].service_get_sort += 1


def empty_queue() -> None:
    '''
    empty the queue before recomputing resources
    '''
    service_queue.clear()