import math
import sys
import copy
import las_queue
import init

sys.path.append('/home/tank/maozz/test/exec/predictable_model')

import predict_model
from resources_define import Job


model_name_1 = ["vgg16", "vgg19", "lenet", "overfeat", "alexnet", "resnet50", "mobilenet"]
model_name_2 = ["vgg11", "googlenet", "trivial", "inception3","inception4", "resnet101", "resnet152"]

gpu_comp_cpu = 10
cpu_core_per_pod = 5

# predictable work but not tuned yet
adjust_ready_queue = []
resource_incre_queue = []
resource_decre_queue = []
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


def calculate_service_queue_rstf() -> None:
    '''
    consolidate all jobs by number of services
    '''
    for i in range(len(las_queue.LAS_CPU)):
        service_queue.append(las_queue.LAS_CPU[i])

    for i in range(len(las_queue.LAS_GPU)):
        service_queue.append(las_queue.LAS_GPU[i])

    for i in range(len(adjust_ready_queue)):
        service_queue.append(adjust_ready_queue[i])

    service_queue.sort(key=lambda job: float(
        predict_model.calu_remain_time(job)))


def calculate_sort_position() -> None:
    '''
    TODO
    '''
    for i in range(len(resource_incre_queue)):
        resource_incre_queue[i].service_add_sort += 1

    for i in range(len(resource_decre_queue)):
        resource_decre_queue[i].service_delete_sort += 1

    for i in range(len(service_queue)):
        service_queue[i].service_get_sort += 1


def empty_queue() -> None:
    '''
    empty the queue before recomputing resources
    '''
    resource_incre_queue.clear()
    resource_decre_queue.clear()
    service_queue.clear()


def resource_benefit_calculation() -> None:
    '''
    calculate resource benefits and obtain positive and negative benefit queues
    '''
    for i in range(len(adjust_ready_queue)):
        if adjust_ready_queue[i].worker_source_type == 'gpu':
            temp1 = copy.deepcopy(adjust_ready_queue[i])
            temp2 = copy.deepcopy(adjust_ready_queue[i])
            temp3 = copy.deepcopy(adjust_ready_queue[i])

            temp1.ps_num = int(temp1.ps_num) + 1
            temp2.worker_num = int(temp2.worker_num) + 1
            temp2.threads_num = int(temp2.threads_num) + 44
            temp2.gpu_num = int(temp2.gpu_num) + 100
            temp3.threads_num = int(temp3.threads_num) + 44
            temp3.gpu_num = int(temp3.gpu_num) + 100

            add_ps = 99999999999999999999 if int(temp1.ps_num) > 10 or int(
                temp1.worker_num) > 4 else predict_model.calu_remain_time(temp1) * calculate_service(temp1)
            add_worker = 99999999999999999999 if int(temp2.ps_num) > 10 or int(temp2.worker_num) > 4 or int(temp2.threads_num) / int(temp2.worker_num) > 44 or int(temp2.gpu_num) / int(temp2.worker_num) > 100 or int(temp2.threads_num) > 176 or int(
                temp2.gpu_num) > 400 else predict_model.calu_remain_time(temp2) * calculate_service(temp2)
            add_gpu = 99999999999999999999 if int(temp3.threads_num) / int(temp3.worker_num) > 44 or int(temp3.gpu_num) / int(temp3.worker_num) > 100 or int(temp3.threads_num) > 176 or int(
                temp3.gpu_num) > 400 else predict_model.calu_remain_time(temp3) * calculate_service(temp3)

            service = predict_model.calu_remain_time(
                adjust_ready_queue[i]) * calculate_service(adjust_ready_queue[i])

            print("===============================================")
            print("job {i} service num:".format(i=adjust_ready_queue[i].id))
            print("add_ps" + " {addps} ".format(addps=add_ps))
            print("add_worker" + " {addworker} ".format(addworker=add_worker))
            print("add_gpu" + " {addgpu} ".format(addgpu=add_gpu))
            print("service" + " {service} ".format(service=service))

            if service - add_ps > max(service - add_worker, service - add_gpu):
                adjust_ready_queue[i].service_add_choice = 0
                adjust_ready_queue[i].service_add = service - add_ps
            elif service - add_worker > max(service - add_ps, service - add_gpu):
                adjust_ready_queue[i].service_add_choice = 2
                adjust_ready_queue[i].service_add = service - add_worker
            elif service - add_gpu > max(service - add_ps, service - add_worker):
                adjust_ready_queue[i].service_add_choice = 3
                adjust_ready_queue[i].service_add = service - add_gpu
            elif add_ps == 99999999999999999999 or add_worker == 99999999999999999999 or add_gpu == 99999999999999999999:
                print("there are not enough resources to allocate")
                adjust_ready_queue[i].service_add_choice = 4
                adjust_ready_queue[i].service_add = 99999999999999999999

            temp1 = copy.deepcopy(adjust_ready_queue[i])
            temp2 = copy.deepcopy(adjust_ready_queue[i])
            temp3 = copy.deepcopy(adjust_ready_queue[i])
            
            temp1.ps_num = int(temp1.ps_num) - 1
            temp2.worker_num = int(temp2.worker_num) - 1
            temp2.threads_num = int(temp2.threads_num) - 44
            temp2.gpu_num = int(temp2.gpu_num) - 100
            temp3.threads_num = int(temp3.threads_num) - 44
            temp3.gpu_num = int(temp3.gpu_num) - 100

            delete_ps = 99999999999999999999 if int(temp1.ps_num) <= 0 else predict_model.calu_remain_time(
                temp1) * calculate_service(temp1)
            delete_worker = 99999999999999999999 if (int(temp2.worker_num) <= 0 or int(temp2.gpu_num) <= 0 or int(
                temp2.threads_num) <= 0) else predict_model.calu_remain_time(temp2) * calculate_service(temp2)
            delete_gpu = 99999999999999999999 if (int(temp3.gpu_num) <= 0 or int(
                temp3.threads_num) <= 0) else predict_model.calu_remain_time(temp3) * calculate_service(temp3)

            print("delete_ps" + " {addps} ".format(addps=delete_ps))
            print("delete_worker" +
                  " {addworker} ".format(addworker=delete_worker))
            print("delete_gpu" + " {addgpu} ".format(addgpu=delete_gpu))

            if service - delete_ps > max(service - delete_worker, service - delete_gpu):
                adjust_ready_queue[i].service_delete_choice = 0
                adjust_ready_queue[i].service_delete = service - delete_ps
            elif service - delete_worker > max(service - delete_ps, service - delete_gpu):
                adjust_ready_queue[i].service_delete_choice = 2
                adjust_ready_queue[i].service_delete = service - delete_worker
            elif service - delete_gpu > max(service - delete_ps, service - delete_worker):
                adjust_ready_queue[i].service_delete_choice = 3
                adjust_ready_queue[i].service_delete = service - delete_gpu
            elif delete_ps == 99999999999999999999 or delete_worker == 99999999999999999999 or delete_gpu == 99999999999999999999:
                print("there are unit resources in the resource and cannot be deleted")
                adjust_ready_queue[i].service_delete_choice = 4
                adjust_ready_queue[i].service_delete = 99999999999999999999
            
            if (float(adjust_ready_queue[i].service_delete < adjust_ready_queue[i].service_add)):
                print("进入增队列")
                resource_incre_queue.append(adjust_ready_queue[i])
            else:
                print("进入减少减队列")
                resource_decre_queue.append(adjust_ready_queue[i])


def resource_benefit_calculation_mps() -> None:
    '''
    calculate resource benefits and obtain positive and negative benefit queues
    '''
    for i in range(len(adjust_ready_queue)):
        if adjust_ready_queue[i].worker_source_type == 'gpu':
            temp1 = copy.deepcopy(adjust_ready_queue[i])
            temp2 = copy.deepcopy(adjust_ready_queue[i])
            temp3 = copy.deepcopy(adjust_ready_queue[i])

            temp1.ps_num = int(temp1.ps_num) + 1
            temp2.worker_num = int(temp2.worker_num) + 1
            # if temp2.model_name in model_name_1:
            #     temp2.threads_num = int(temp2.threads_num) + 22
            # else:
            #     temp2.threads_num = int(temp2.threads_num) + 33
            temp2.threads_num = int(temp2.threads_num) + 44
            temp2.gpu_num = int(temp2.gpu_num) + 50
            temp3.gpu_num = int(temp3.gpu_num) + 50

            # add_ps = 99999 if (int(temp1.ps_num) * 5 + int(temp1.worker_num) *
            #                    1) >= 27 else predict_model.calu_remain_time(temp1) * calculate_service(temp1)
            # add_worker = 99999 if (int(temp2.ps_num) * 5 + int(temp2.worker_num) * 1) >= 27 or int(temp2.threads_num) / int(temp2.worker_num) >= 44 or int(
            #     temp2.gpu_num) / int(temp2.worker_num) >= 100 or int(temp2.threads_num) >= 88 or int(
            #     temp2.gpu_num) >= 200 else predict_model.calu_remain_time(temp2) * calculate_service(temp2)
            # add_gpu = 99999 if int(temp2.threads_num) / int(temp2.worker_num) >= 44 or int(
            #     temp2.gpu_num) / int(temp2.worker_num) >= 100 or int(temp3.threads_num) >= 88 or int(
            #     temp3.gpu_num) >= 200 else predict_model.calu_remain_time(temp3) * calculate_service(temp3)

            add_ps = 99999999999999999999 if int(temp1.ps_num) > 10 or int(
                temp1.worker_num) > 4 else predict_model.calu_remain_time(temp1) * calculate_service(temp1)
            add_worker = 99999999999999999999 if int(temp2.ps_num) > 10 or int(temp2.worker_num) > 4 or int(temp2.threads_num) / int(temp2.worker_num) > 44 or int(temp2.gpu_num) / int(temp2.worker_num) > 100 or int(temp2.threads_num) > 176 or int(
                temp2.gpu_num) > 400 else predict_model.calu_remain_time(temp2) * calculate_service(temp2)
            add_gpu = 99999999999999999999 if int(temp3.threads_num) / int(temp3.worker_num) > 44 or int(temp3.gpu_num) / int(temp3.worker_num) > 100 or int(temp3.threads_num) > 176 or int(
                temp3.gpu_num) > 400 else predict_model.calu_remain_time(temp3) * calculate_service(temp3)

            service = predict_model.calu_remain_time(
                adjust_ready_queue[i]) * calculate_service(adjust_ready_queue[i])

            print("===============================================")
            print("job {i} service num:".format(i=adjust_ready_queue[i].id))
            print("add_ps" + " {addps} ".format(addps=add_ps))
            print("add_worker" + " {addworker} ".format(addworker=add_worker))
            print("add_gpu" + " {addgpu} ".format(addgpu=add_gpu))
            print("service" + " {service} ".format(service=service))

            if service - add_ps > max(service - add_worker, service - add_gpu):
                adjust_ready_queue[i].service_add_choice = 0
                adjust_ready_queue[i].service_add = service - add_ps
            elif service - add_worker > max(service - add_ps, service - add_gpu):
                adjust_ready_queue[i].service_add_choice = 2
                adjust_ready_queue[i].service_add = service - add_worker
            elif service - add_gpu > max(service - add_ps, service - add_worker):
                adjust_ready_queue[i].service_add_choice = 3
                adjust_ready_queue[i].service_add = service - add_gpu
            elif add_ps == 99999999999999999999 or add_worker == 99999999999999999999 or add_gpu == 99999999999999999999:
                print("there are not enough resources to allocate")
                adjust_ready_queue[i].service_add_choice = 4
                adjust_ready_queue[i].service_add = 99999999999999999999

            temp1 = copy.deepcopy(adjust_ready_queue[i])
            temp2 = copy.deepcopy(adjust_ready_queue[i])
            temp3 = copy.deepcopy(adjust_ready_queue[i])

            temp1.ps_num = int(temp1.ps_num) - 1
            temp2.worker_num = int(temp2.worker_num) - 1
            # if temp2.model_name in model_name_1:
            #     temp2.threads_num = int(temp2.threads_num) - 22
            # else:
            #     temp2.threads_num = int(temp2.threads_num) - 33
            temp2.threads_num = int(temp2.threads_num) - 44
            temp2.gpu_num = int(temp2.gpu_num) - 50
            temp3.gpu_num = int(temp3.gpu_num) - 50

            delete_ps = 99999999999999999999 if int(temp1.ps_num) <= 0 else predict_model.calu_remain_time(
                temp1) * calculate_service(temp1)
            delete_worker = 99999999999999999999 if (int(temp2.worker_num) <= 0 or int(temp2.gpu_num) <= 0 or int(
                temp2.threads_num) <= 0) else predict_model.calu_remain_time(temp2) * calculate_service(temp2)
            delete_gpu = 99999999999999999999 if (int(temp3.gpu_num) <= 0 or int(
                temp3.threads_num) <= 0) else predict_model.calu_remain_time(temp3) * calculate_service(temp3)

            print("delete_ps" + " {addps} ".format(addps=delete_ps))
            print("delete_worker" +
                  " {addworker} ".format(addworker=delete_worker))
            print("delete_gpu" + " {addgpu} ".format(addgpu=delete_gpu))

            if service - delete_ps > max(service - delete_worker, service - delete_gpu):
                adjust_ready_queue[i].service_delete_choice = 0
                adjust_ready_queue[i].service_delete = service - delete_ps
            elif service - delete_worker > max(service - delete_ps, service - delete_gpu):
                adjust_ready_queue[i].service_delete_choice = 2
                adjust_ready_queue[i].service_delete = service - delete_worker
            elif service - delete_gpu > max(service - delete_ps, service - delete_worker):
                adjust_ready_queue[i].service_delete_choice = 3
                adjust_ready_queue[i].service_delete = service - delete_gpu
            elif delete_ps == 99999999999999999999 or delete_worker == 99999999999999999999 or delete_gpu == 99999999999999999999:
                print("there are unit resources in the resource and cannot be deleted")
                adjust_ready_queue[i].service_delete_choice = 4
                adjust_ready_queue[i].service_delete = 99999999999999999999

            if (float(adjust_ready_queue[i].service_delete < adjust_ready_queue[i].service_add)):
                print("进入增队列")
                resource_incre_queue.append(adjust_ready_queue[i])
            else:
                print("进入减少减队列")
                resource_decre_queue.append(adjust_ready_queue[i])


def resource_benefit_calculation_optimus() -> None:
    '''
    calculate resource benefits and obtain positive benefit queues in optimus
    '''
    for i in range(len(init.jobs)):
        if init.jobs[i].worker_source_type == 'gpu':
            temp1 = copy.deepcopy(init.jobs[i])
            temp2 = copy.deepcopy(init.jobs[i])

            temp1.ps_num = int(temp1.ps_num) + 1
            temp2.worker_num = int(temp2.worker_num) + 1
            temp2.threads_num = int(temp2.threads_num) + 44
            temp2.gpu_num = int(temp2.gpu_num) + 100

            add_ps = 99999 if int(temp1.ps_num) > 10 or int(
                temp1.worker_num) > 4 else predict_model.calu_remain_time_optimus(temp1) * calculate_service(temp1)
            add_worker = 99999 if int(temp2.ps_num) > 10 or int(temp2.worker_num) > 4 or int(temp2.threads_num) / int(temp2.worker_num) > 44 or int(temp2.gpu_num) / int(temp2.worker_num) > 100 or int(temp2.threads_num) > 176 or int(
                temp2.gpu_num) > 400 else predict_model.calu_remain_time_optimus(temp2) * calculate_service(temp2)
            service = predict_model.calu_remain_time_optimus(
                init.jobs[i]) * calculate_service(init.jobs[i])

            # print("===============================================")
            # print("job {i} service num:".format(i=init.jobs[i].id))
            # print("add_ps" + " {addps} ".format(addps=add_ps))
            # print("add_worker" + " {addworker} ".format(addworker=add_worker))
            # print("service" + " {service} ".format(service=service))

            if service < add_ps and service < add_worker:
                init.jobs[i].service_add_choice = 4
                init.jobs[i].service_add = 0
            elif service - add_ps > service - add_worker:
                init.jobs[i].service_add_choice = 0
                init.jobs[i].service_add = service - add_ps
            elif service - add_worker > service - add_ps:
                init.jobs[i].service_add_choice = 2
                init.jobs[i].service_add = service - add_worker
            elif add_ps == 99999 or add_worker == 99999:
                print("there are not enough resources to allocate")
                init.jobs[i].service_delete_choice = 4
            resource_incre_queue.append(init.jobs[i])
