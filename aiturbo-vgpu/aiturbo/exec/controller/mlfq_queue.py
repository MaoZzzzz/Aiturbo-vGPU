import sys
import predictable_queue
import getResourceFromK8S
import top_controller

sys.path.append('/home/tank/maozz/test/measure')
import run_program

MLFQ = []
MLFQ_threshold = [30, 180, 100000000]
MLFQ_list_number = 3

schedule_queue = []


def init_MLFQ() -> None:
    '''
    initialize MLFQ queue
    '''
    MLFQ.clear()
    for i in range(MLFQ_list_number):
        MLFQ.append([])


def temp_caluculate_schedule_queue() -> None:
    '''
    statistical preemption information, excluding resource changes
    '''
    for i in range(len(predictable_queue.service_queue)):
        if str(predictable_queue.service_queue[i].job_state) == '1':
            predictable_queue.service_queue[i].schedule_sort = int(
                predictable_queue.service_queue[i].service_get_sort) * 2
            schedule_queue.append(predictable_queue.service_queue[i])
        elif str(predictable_queue.service_queue[i].job_state) == '2':
            predictable_queue.service_queue[i].ps_num_temp = predictable_queue.service_queue[i].ps_num
            predictable_queue.service_queue[i].worker_num_temp = predictable_queue.service_queue[i].worker_num
            predictable_queue.service_queue[i].gpu_num_temp = predictable_queue.service_queue[i].gpu_num
            if predictable_queue.service_queue[i] in predictable_queue.resource_incre_queue:
                predictable_queue.service_queue[i].schedule_sort = predictable_queue.service_queue[
                    i].service_add_sort + predictable_queue.service_queue[i].service_get_sort
                schedule_queue.append(predictable_queue.service_queue[i])
            else:
                predictable_queue.service_queue[i].schedule_sort = predictable_queue.service_queue[
                    i].service_delete_sort + predictable_queue.service_queue[i].service_get_sort
                schedule_queue.append(predictable_queue.service_queue[i])


def caluculate_schedule_queue() -> None:
    '''
    statistical preemption information
    '''
    # for i in range(len(predictable_queue.service_queue)):
    #     predictable_queue.service_queue[i].job_state = '2'
    for i in range(len(predictable_queue.service_queue)):
        if str(predictable_queue.service_queue[i].job_state) == '1':
            predictable_queue.service_queue[i].schedule_sort = int(
                predictable_queue.service_queue[i].service_get_sort) * 2
            schedule_queue.append(predictable_queue.service_queue[i])
        elif str(predictable_queue.service_queue[i].job_state) == '2':
            predictable_queue.service_queue[i].ps_num_temp = predictable_queue.service_queue[i].ps_num
            predictable_queue.service_queue[i].worker_num_temp = predictable_queue.service_queue[i].worker_num
            predictable_queue.service_queue[i].gpu_num_temp = predictable_queue.service_queue[i].gpu_num
            predictable_queue.service_queue[i].threads_num_temp = predictable_queue.service_queue[i].threads_num
            if predictable_queue.service_queue[i] in predictable_queue.resource_incre_queue:
                predictable_queue.service_queue[i].schedule_sort = predictable_queue.service_queue[
                    i].service_add_sort + predictable_queue.service_queue[i].service_get_sort

                if predictable_queue.service_queue[i].service_add_choice == 0:
                    # predictable_queue.service_queue[i].ps_num_temp = int(predictable_queue.service_queue[i].ps_num_temp) + 1
                    predictable_queue.service_queue[i].ps_num = int(
                        predictable_queue.service_queue[i].ps_num_temp) + 1
                elif predictable_queue.service_queue[i].service_add_choice == 2:
                    # predictable_queue.service_queue[i].worker_num_temp = int(predictable_queue.service_queue[i].worker_num_temp) + 1
                    # predictable_queue.service_queue[i].gpu_num_temp = int(predictable_queue.service_queue[i].gpu_num_temp) + 100
                    # predictable_queue.service_queue[i].threads_num_temp = int(predictable_queue.service_queue[i].threads_num_temp) + 44
                    predictable_queue.service_queue[i].worker_num = int(
                        predictable_queue.service_queue[i].worker_num_temp) + 1
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) + 100
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) + 44
                elif predictable_queue.service_queue[i].service_add_choice == 3:
                    # predictable_queue.service_queue[i].gpu_num_temp = int(predictable_queue.service_queue[i].gpu_num_temp) + 100
                    # predictable_queue.service_queue[i].threads_num_temp = int(predictable_queue.service_queue[i].threads_num_temp) + 44
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) + 100
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) + 44

                schedule_queue.append(predictable_queue.service_queue[i])
            else:
                predictable_queue.service_queue[i].schedule_sort = predictable_queue.service_queue[
                    i].service_delete_sort + predictable_queue.service_queue[i].service_get_sort

                if predictable_queue.service_queue[i].service_delete_choice == 0:
                    # predictable_queue.service_queue[i].ps_num_temp = int(predictable_queue.service_queue[i].ps_num_temp) - 1
                    predictable_queue.service_queue[i].ps_num = int(
                        predictable_queue.service_queue[i].ps_num_temp) - 1
                elif predictable_queue.service_queue[i].service_delete_choice == 2:
                    # predictable_queue.service_queue[i].worker_num_temp = int(predictable_queue.service_queue[i].worker_num_temp) - 1
                    # predictable_queue.service_queue[i].gpu_num_temp = int(predictable_queue.service_queue[i].gpu_num_temp) - 100
                    # predictable_queue.service_queue[i].threads_num_temp = int(predictable_queue.service_queue[i].threads_num_temp) - 44
                    predictable_queue.service_queue[i].worker_num = int(
                        predictable_queue.service_queue[i].worker_num_temp) - 1
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) - 100
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) - 44
                elif predictable_queue.service_queue[i].service_delete_choice == 3:
                    # predictable_queue.service_queue[i].gpu_num_temp = int(predictable_queue.service_queue[i].gpu_num_temp) - 100
                    # predictable_queue.service_queue[i].threads_num_temp = int(predictable_queue.service_queue[i].threads_num_temp) - 44
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) - 100
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) - 44

                schedule_queue.append(predictable_queue.service_queue[i])


def caluculate_schedule_queue_mps() -> None:
    '''
    statistical preemption information
    '''
    for i in range(len(predictable_queue.service_queue)):
        if str(predictable_queue.service_queue[i].job_state) == '1':
            predictable_queue.service_queue[i].schedule_sort = int(
                predictable_queue.service_queue[i].service_get_sort) * 2
            schedule_queue.append(predictable_queue.service_queue[i])
        elif str(predictable_queue.service_queue[i].job_state) == '2':
            predictable_queue.service_queue[i].ps_num_temp = predictable_queue.service_queue[i].ps_num
            predictable_queue.service_queue[i].worker_num_temp = predictable_queue.service_queue[i].worker_num
            predictable_queue.service_queue[i].gpu_num_temp = predictable_queue.service_queue[i].gpu_num
            predictable_queue.service_queue[i].threads_num_temp = predictable_queue.service_queue[i].threads_num
            if predictable_queue.service_queue[i] in predictable_queue.resource_incre_queue:
                predictable_queue.service_queue[i].schedule_sort = predictable_queue.service_queue[
                    i].service_add_sort + predictable_queue.service_queue[i].service_get_sort

                if predictable_queue.service_queue[i].service_add_choice == 0:
                    predictable_queue.service_queue[i].ps_num = int(
                        predictable_queue.service_queue[i].ps_num_temp) + 1
                elif predictable_queue.service_queue[i].service_add_choice == 2:
                    predictable_queue.service_queue[i].worker_num = int(
                        predictable_queue.service_queue[i].worker_num_temp) + 1
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) + 25
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) + 11
                elif predictable_queue.service_queue[i].service_add_choice == 3:
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) + 25
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) + 11

                schedule_queue.append(predictable_queue.service_queue[i])
            else:
                predictable_queue.service_queue[i].schedule_sort = predictable_queue.service_queue[
                    i].service_delete_sort + predictable_queue.service_queue[i].service_get_sort

                if predictable_queue.service_queue[i].service_delete_choice == 0:
                    predictable_queue.service_queue[i].ps_num = int(
                        predictable_queue.service_queue[i].ps_num_temp) - 1
                elif predictable_queue.service_queue[i].service_delete_choice == 2:
                    predictable_queue.service_queue[i].worker_num = int(
                        predictable_queue.service_queue[i].worker_num_temp) - 1
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) - 25
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) - 11
                elif predictable_queue.service_queue[i].service_delete_choice == 3:
                    predictable_queue.service_queue[i].gpu_num = int(
                        predictable_queue.service_queue[i].gpu_num_temp) - 25
                    predictable_queue.service_queue[i].threads_num = int(
                        predictable_queue.service_queue[i].threads_num_temp) - 11

                schedule_queue.append(predictable_queue.service_queue[i])


def claculate_MLFQ() -> None:
    '''
    statistical preemption information, excluding resource changes
    '''
    global remain_cpu
    global remain_gpu
    global remain_gmem

    schedule_queue.sort(key=lambda job: float(job.schedule_sort))

    # put the job to be scheduled into the MLFQ queue
    for i in range(len(schedule_queue)):
        for j in range(MLFQ_list_number):
            if schedule_queue[i].schedule_sort < MLFQ_threshold[j]:
                MLFQ[j].append(schedule_queue[i])
                break

    # node = getResourceFromK8S.init_node()

    # remain_cpu = node.cpu
    # remain_gpu = node.gpu
    # remain_gmem = node.gmem
    # remain_cpu_master = 30
    # remain_gpu_master = 200
    # remain_gmem_master = 88

    # remain_cpu_node1 = 32
    # remain_gpu_node1 = 200
    # remain_gmem_node1 = 88
    remain_cpu = 57
    remain_gpu = 400
    remain_gmem = 176

    # determining which jobs to put into the cluster to run
    for i in range(len(MLFQ)):
        for j in range(len(MLFQ[i])):
            # place = top_controller.init_job(MLFQ[i][j])
            # if place == 'kube-master':
            #     remain_cpu = remain_cpu_master
            #     remain_gpu = remain_gpu_master
            #     remain_gmem = remain_gmem_master
            # elif place == 'kube-node1':
            #     remain_cpu = remain_cpu_node1
            #     remain_gpu = remain_gpu_node1
            #     remain_gmem = remain_gmem_node1
            
            # run_program.delete_job(MLFQ[i][j].id, False)

            if str(MLFQ[i][j].job_state) == '1':
                if MLFQ[i][j].worker_source_type == 'gpu':
                    if int(MLFQ[i][j].gpu_num) <= int(remain_gpu) and (int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num) + int(MLFQ[i][j].worker_num)) <= remain_cpu and int(MLFQ[i][j].threads_num) <= int(remain_gmem):
                        MLFQ[i][j].is_running = 1
                        remain_cpu -= int(MLFQ[i][j].cpu_core_ps) * \
                            int(MLFQ[i][j].ps_num)
                        remain_gpu -= int(MLFQ[i][j].gpu_num)
                        remain_gmem -= int(MLFQ[i][j].threads_num)
                elif MLFQ[i][j].worker_source_type == 'cpu':
                    if (int(MLFQ[i][j].cpu_core_worker) * int(MLFQ[i][j].worker_num) + int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num)) <= remain_cpu:
                        MLFQ[i][j].is_running = 1
                        remain_cpu -= (int(MLFQ[i][j].cpu_core_worker) * int(
                            MLFQ[i][j].worker_num) + int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num))
            elif str(MLFQ[i][j].job_state) == '2':
                if MLFQ[i][j].worker_source_type == 'gpu':
                    if int(MLFQ[i][j].gpu_num) <= int(remain_gpu) and (int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num) + int(MLFQ[i][j].worker_num)) <= remain_cpu and int(MLFQ[i][j].threads_num) <= int(remain_gmem):
                        MLFQ[i][j].is_running = 1
                        remain_cpu -= int(MLFQ[i][j].cpu_core_ps) * \
                            int(MLFQ[i][j].ps_num)
                        remain_gpu -= int(MLFQ[i][j].gpu_num)
                        remain_gmem -= int(MLFQ[i][j].threads_num)
                elif MLFQ[i][j].worker_source_type == 'cpu':
                    if (int(MLFQ[i][j].cpu_core_worker) * int(MLFQ[i][j].worker_num) + int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num)) <= remain_cpu:
                        MLFQ[i][j].is_running = 1
                        remain_cpu -= (int(MLFQ[i][j].cpu_core_worker) * int(
                            MLFQ[i][j].worker_num) + int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num))

            # if place == 'kube-master':
            #     remain_cpu_master = remain_cpu
            #     remain_gpu_master = remain_gpu
            #     remain_gmem_master = remain_gmem
            # elif place == 'kube-node1':
            #     remain_cpu_node1 = remain_cpu
            #     remain_gpu_node1 = remain_gpu
            #     remain_gmem_node1 = remain_gmem


def update_get_service() -> None:
    '''
    update the number of services already acquired
    '''
    for i in range(len(MLFQ)):
        for j in range(len(MLFQ[i])):
            if str(MLFQ[i][j].is_running) == '1':
                if MLFQ[i][j].worker_source_type == 'gpu':
                    temp = float(
                        MLFQ[i][j].gpu_num) * float(predictable_queue.gpu_comp_cpu) + float(MLFQ[i][j].ps_num)
                    MLFQ[i][j].service_get = MLFQ[i][j].service_get + temp
                elif MLFQ[i][j].worker_source_type == 'cpu':
                    temp = float(MLFQ[i][j].worker_num) + \
                        float(MLFQ[i][j].ps_num())
                    MLFQ[i][j].service_get = MLFQ[i][j].service_get + temp
