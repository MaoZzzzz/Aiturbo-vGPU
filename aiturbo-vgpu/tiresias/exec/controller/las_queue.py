import sys
sys.path.append('/home/tank/maozz/tiresias/exec/define')
import predictable_queue
import init_tir
import time


LAS_CPU = []
LAS_GPU = []
LAS_queue_total_job_number = 0


def las_job_finish(job_id) -> None:
    '''
    remove job from las queue
    '''
    global LAS_queue_total_job_number

    flag = []
    for i in range(len(LAS_CPU)):
        if str(job_id) == str(LAS_CPU[i].id):
            flag.append(i)
            LAS_queue_total_job_number -= 1

    for i in range(len(flag)-1, -1, -1):
        del LAS_CPU[flag[i]]
    flag.clear()

    for i in range(len(LAS_GPU)):
        if str(job_id) == str(LAS_GPU[i].id):
            flag.append(i)
            LAS_queue_total_job_number -= 1

    for i in range(len(flag)-1, -1, -1):
        del LAS_GPU[flag[i]]
    flag.clear()


def add_init_job_tolist(now_time) -> bool:
    '''
    queue jobs by time
    '''
    global LAS_queue_total_job_number

    before_change = LAS_queue_total_job_number

    for i in range(len(init_tir.jobs)):
        if int(now_time) >= int(init_tir.jobs[i].arrive_time) and init_tir.jobs[i].job_state == '0' and str(init_tir.jobs[i].finish_time) == "0":
            print("job {job_id} arrives in the LAS queue".format(
                job_id=init_tir.jobs[i].id))
            init_tir.jobs[i].job_state = 1
            LAS_queue_total_job_number += 1
            if init_tir.jobs[i].worker_source_type == 'cpu':
                LAS_CPU.append(init_tir.jobs[i])
            elif init_tir.jobs[i].worker_source_type == 'gpu':
                LAS_GPU.append(init_tir.jobs[i])
    # print("LAS GPU length: " + str(len(LAS_GPU)))
    if before_change != LAS_queue_total_job_number:
        return True
    else:
        return False