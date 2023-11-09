import sys
from xmlrpc.client import boolean

sys.path.append('/home/tank/maozz/test/exec/define')
sys.path.append('/home/tank/maozz/test/measure')
import mlfq_queue
import las_queue
import threading
import time
import os
import init
import init_model
import predictable_queue
import run_program


pree_num = 0


def cal_pree() -> None:
    '''
    statistical preemption times
    '''
    global pree_num
    for i in range(len(mlfq_queue.MLFQ)):
        for j in range(len(mlfq_queue.MLFQ[i])):
            if str(mlfq_queue.MLFQ[i][j].is_running) == '1' and str(
                    mlfq_queue.MLFQ[i][j].last_running_state) == '0':
                if i == 1:
                    flag1 = 0
                    for k in range(len(mlfq_queue.MLFQ[i + 1])):
                        if str(mlfq_queue.MLFQ[i + 1][k].is_running) == '1':
                            flag1 = 1
                            break
                    if flag1 == 1:
                        pree_num += 1
                elif i == 0:
                    flag1 = 0
                    for k in range(len(mlfq_queue.MLFQ[i + 2])):
                        if str(mlfq_queue.MLFQ[i + 2][k].is_running) == '1':
                            flag1 = 1
                    for k in range(len(mlfq_queue.MLFQ[i + 1])):
                        if str(mlfq_queue.MLFQ[i + 1][k].is_running) == '1':
                            flag1 = 1
                    if flag1 == 1:
                        pree_num += 1


def finish_job(now_time) -> boolean:
    '''
    judging that homework completes or turns predictable
    '''
    for i in range(len(init.jobs)):
        current_step = run_program.get_now_step(init.jobs[i].id)
        if current_step != -1:
            print("now job : " + init.jobs[i].id + " " + current_step)
            if int(current_step) >= int(init.jobs[i].total_steps):
                las_queue.las_job_finish(init.jobs[i].id)
                predictable_queue.adjust_job_finish(init.jobs[i].id)
                run_program.delete_job(init.jobs[i].id, True)
                init.jobs[i].finish_time = now_time
                print("Job " + str(i + 1) + " is over")
                return init.jobs[i].id
    return "-1"


def predictable_job() -> None:
    '''
    convert jobs to predictable jobs
    '''
    time_all = []
    path = "/home/tank/maozz/test/exec/systemData/temp.txt"
    for line in open(path):
        line = line.replace("\n", "")
        line_temp = line.split("\t")

        temp = []
        temp.append(line_temp[0])
        temp.append(line_temp[1])
        time_all.append(temp)

    for i in range(len(init.jobs)):
        current_step = run_program.get_now_step(init.jobs[i].id)
        if current_step != -1:
            if str(time_all[i][1]) == '99999':
                break
            if int(current_step) >= int(int(init.jobs[i].total_steps) * (float(time_all[i][1]) / float(time_all[i][0]))):
                las_queue.become_predictable(i + 1)


def init_job(job) -> None:
    '''
    initialization job
    '''
    # avoid conflict between two Job classes
    ps_resources = []
    worker_resources = []
    ps_resources.append(job.ps_num)
    worker_resources.append(job.worker_num)
    worker_resources.append(job.gpu_num)
    worker_resources.append(job.threads_num)

    run_program.init_job(job.id, ps_resources, worker_resources,
                         job.model_name, job.total_steps, job.batch_size, True)
    # my_process = Process(target = run_program.init_job, args = (job.id, ps_resources, worker_resources, job.model_name, job.total_steps, job.batch_size))
    # my_process.start()
    # my_process.join()


def mlfq_sequence(now_time) -> None:
    path = "/home/tank/maozz/experiment/experiment1/rstf.txt"

    job_running = []
    for i in range(len(init.jobs)):
        if str(init.jobs[i].last_running_state) == '1':
            job_run = "Job " + \
                init.jobs[i].id + " in " + \
                str(i) + " is running " + "\n"
            job_running.append(job_run)

    finish_time = []
    for i in range(60):
        finish_time.append(0)
    finish = ""
    for i in range(len(init.jobs)):
        if str(init.jobs[i].finish_time) != "0":
            finish_time[i] = init.jobs[i].finish_time
    for i in range(len(init.jobs)):
        finish = finish + str(finish_time[i]) + " "
    finish = finish + "\n"

    with open(path, "a") as file:
        file.write("time " + str(now_time) + ": " + "\n")
        for i in range(len(job_running)):
            file.write(job_running[i])
        file.write(finish)


def main():
    start_time = time.time()
    init.init_jobs()
    init_model.init_models()
    while (True):
        time.sleep(1)
        now_time = int(time.time() - start_time)
        print("current time is: " + str(now_time))
        is_arrive = las_queue.add_init_job_tolist(now_time)

        mlfq_queue.init_MLFQ()
        predictable_job()
        las_queue.unpredict_to_predict()

        # print("LAS_GPU queue length:" + str(len(las_queue.LAS_GPU)))
        if now_time % 120 == 0 or is_arrive:
            predictable_queue.empty_queue()
            predictable_queue.resource_incre_queue.sort(
                key=lambda job: float(job.service_add))
            predictable_queue.resource_decre_queue.sort(
                key=lambda job: float(job.service_delete))
            predictable_queue.calculate_service_queue_rstf()
            predictable_queue.calculate_sort_position()
            mlfq_queue.caluculate_schedule_queue()
            mlfq_queue.claculate_MLFQ()
            mlfq_queue.update_get_service()


            cal_pree()


            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        # thread = threading.Thread(target = run_program.delete_job,args = mlfq_queue.MLFQ[i][j].id)
                        # thread.start()
                        run_program.delete_job(mlfq_queue.MLFQ[i][j].id, False)
                        # time.sleep(30)

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        init_job(mlfq_queue.MLFQ[i][j])
                        # thread = threading.Thread(target = run_program.run_job,args = mlfq_queue.MLFQ[i][j].id)
                        # thread.start()
                        run_program.run_job(mlfq_queue.MLFQ[i][j].id)

            # mlfq_sequence(now_time)

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        print("Job " + str(mlfq_queue.MLFQ[i][j].id) + " in " + " MLFQ[" + str(i) + "]" + " is running:")
                        print("Job " + str(mlfq_queue.MLFQ[i][j].id) + " resources:")
                        print("cpu num: " + str(int(mlfq_queue.MLFQ[i][j].cpu_core_ps) * int(mlfq_queue.MLFQ[i][j].ps_num)) )
                        print("gpu num: " + str(int(mlfq_queue.MLFQ[i][j].gpu_num)) )
                        print("gmem num: " + str(int(mlfq_queue.MLFQ[i][j].threads_num)) )

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    mlfq_queue.MLFQ[i][j].last_running_state = mlfq_queue.MLFQ[
                        i][j].is_running
            
            for i in range(len(mlfq_queue.MLFQ)):
                mlfq_queue.MLFQ[i].clear()

            for i in range(len(init.jobs)):
                init.jobs[i].is_running = 0

            predictable_queue.service_queue.clear()
            mlfq_queue.schedule_queue.clear()
    
        # break
        finish_job(now_time)
        mlfq_sequence(now_time)


if __name__ == '__main__':
    main()

