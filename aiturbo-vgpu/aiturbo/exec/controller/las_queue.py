import sys
sys.path.append('/home/tank/maozz/test/exec/define')
import predictable_queue
import init
import time


LAS_CPU = []
LAS_GPU = []
LAS_queue_total_job_number = 0


def unpredict_to_predict() -> None:
    '''
    add job from LAS to predictable job queue
    '''
    global LAS_queue_total_job_number

    flag = []
    for i in range(len(LAS_CPU)):
        if LAS_CPU[i].predict_acc >= 0.5:
            LAS_CPU[i].job_state = 2
            predictable_queue.adjust_ready_queue.append(LAS_CPU[i])
            flag.append(i)
            LAS_queue_total_job_number -= 1

    for i in range(len(flag)-1, -1, -1):
        del LAS_CPU[flag[i]]
    flag.clear()

    for i in range(len(LAS_GPU)):
        if LAS_GPU[i].predict_acc >= 0.5:
            LAS_GPU[i].job_state = 2
            predictable_queue.adjust_ready_queue.append(LAS_GPU[i])
            flag.append(i)
            LAS_queue_total_job_number -= 1

    for i in range(len(flag)-1, -1, -1):
        del LAS_GPU[flag[i]]
    flag.clear()


def become_predictable(job_id) -> None:
    '''
    job turned into predictable job
    '''
    global LAS_queue_total_job_number

    for i in range(len(LAS_CPU)):
        if str(job_id) == str(LAS_CPU[i].id):
            LAS_CPU[i].setPredict_acc(0.9)

    for i in range(len(LAS_GPU)):
        if str(job_id) == str(LAS_GPU[i].id):
            LAS_GPU[i].setPredict_acc(0.9)
    pass

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

    for i in range(len(init.jobs)):
        if int(now_time) >= int(init.jobs[i].arrive_time) and init.jobs[i].job_state == '0' and str(init.jobs[i].finish_time) == "0":
            print("job {job_id} arrives in the LAS queue".format(
                job_id=init.jobs[i].id))
            init.jobs[i].job_state = 1
            LAS_queue_total_job_number += 1
            if init.jobs[i].worker_source_type == 'cpu':
                LAS_CPU.append(init.jobs[i])
            elif init.jobs[i].worker_source_type == 'gpu':
                LAS_GPU.append(init.jobs[i])
    # print("LAS GPU length: " + str(len(LAS_GPU)))
    if before_change != LAS_queue_total_job_number:
        return True
    else:
        return False