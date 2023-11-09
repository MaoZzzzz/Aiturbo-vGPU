import sys
import predictable_queue

sys.path.append('/home/tank/maozz/tiresias/measure')

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

    remain_cpu = 57
    remain_gpu = 400
    remain_gmem = 176

    # determining which jobs to put into the cluster to run
    for i in range(len(MLFQ)):
        for j in range(len(MLFQ[i])):
            if str(MLFQ[i][j].job_state) == '1':
                if MLFQ[i][j].worker_source_type == 'gpu':
                    if (int(MLFQ[i][j].gpu_num) + 100 * int(MLFQ[i][j].ps_num)) <= int(remain_gpu):
                        MLFQ[i][j].is_running = 1
                        remain_gpu -= (int(MLFQ[i][j].gpu_num) + 100 * int(MLFQ[i][j].ps_num))
                        remain_gmem -= (int(MLFQ[i][j].threads_num) + 44 * int(MLFQ[i][j].ps_num))
                elif MLFQ[i][j].worker_source_type == 'cpu':
                    if (int(MLFQ[i][j].cpu_core_worker) * int(MLFQ[i][j].worker_num) + int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num)) <= remain_cpu:
                        MLFQ[i][j].is_running = 1
                        remain_cpu -= (int(MLFQ[i][j].cpu_core_worker) * int(
                            MLFQ[i][j].worker_num) + int(MLFQ[i][j].cpu_core_ps) * int(MLFQ[i][j].ps_num))


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
