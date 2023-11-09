import os
import sys
sys.path.append('/home/tank/maozz/tiresias/exec/define')
sys.path.append('/home/tank/maozz/tiresias/measure-tir')
import mlfq_queue
import las_queue
import time
import init_tir
import init_model
import predictable_queue
import run_program_tir


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


def finish_job(now_time) -> None:
    '''
    judging that homework completes or turns predictable
    '''
    for i in range(len(init_tir.jobs)):
        current_step = run_program_tir.get_now_step(init_tir.jobs[i].id)
        if current_step != -1:
            # print("now job : " + init.jobs[i].id + " " + current_step)
            if int(current_step) >= int(init_tir.jobs[i].total_steps):
                las_queue.las_job_finish(init_tir.jobs[i].id)
                predictable_queue.adjust_job_finish(init_tir.jobs[i].id)
                run_program_tir.delete_job(init_tir.jobs[i].id, True)
                init_tir.jobs[i].finish_time = now_time
                print("Job " + str(i + 1) + " is over")


def mlfq_sequence(now_time) -> None:
    path = "/home/tank/maozz/experiment/experiment1/tiresias.txt"

    job_running = []
    for i in range(len(init_tir.jobs)):
        if str(init_tir.jobs[i].finish_time) == '0':
            job_run = "Job " + \
                init_tir.jobs[i].id + " resources: " + str(init_tir.jobs[i].ps_num) + " " + str(
                    init_tir.jobs[i].worker_num) + " " + str(init_tir.jobs[i].gpu_num) + " " + "\n"
            job_running.append(job_run)

    finish_time = []
    for i in range(60):
        finish_time.append(0)
    finish = ""
    for i in range(len(init_tir.jobs)):
        if str(init_tir.jobs[i].finish_time) != "0":
            finish_time[i] = init_tir.jobs[i].finish_time
    for i in range(len(init_tir.jobs)):
        finish = finish + str(finish_time[i]) + " "
    finish = finish + "\n"

    if now_time % 10 == 0:
        with open(path, "a") as file:
            file.write("time " + str(now_time) + ": " + "\n")
            for i in range(len(job_running)):
                file.write(job_running[i])
            file.write(finish)


def main():
    start_time = time.time()
    init_tir.init_jobs()
    init_model.init_models()
    while (True):
        time.sleep(1)
        now_time = int(time.time() - start_time)
        print("current time is: " + str(now_time))
        is_arrive = las_queue.add_init_job_tolist(now_time)

        mlfq_queue.init_MLFQ()

        if now_time % 240 == 0 or is_arrive:
            predictable_queue.empty_queue()
            predictable_queue.calculate_service_queue()
            predictable_queue.calculate_sort_position()
            mlfq_queue.caluculate_schedule_queue()
            mlfq_queue.claculate_MLFQ()
            mlfq_queue.update_get_service()

            cal_pree()

            job_id = []
            # preparing to run a job
            # first stop all the jobs in the cluster, then initialize the job list, and finally put it into the cluster to start the job
            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        job_id.append(mlfq_queue.MLFQ[i][j].id)

            run_program_tir.delete_job(
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], False)
            run_program_tir.init_job(job_id)
            run_program_tir.run_job(job_id)

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        print(
                            "Job " + str(mlfq_queue.MLFQ[i][j].id) + " in " + " MLFQ[" + str(i) + "]" + " is running:")
                        print(
                            "Job " + str(mlfq_queue.MLFQ[i][j].id) + " resources:")
                        print("ps num: " +
                              str(int(mlfq_queue.MLFQ[i][j].ps_num)))
                        print("worker num: " +
                              str(int(mlfq_queue.MLFQ[i][j].worker_num)))
                        print("gpu num: " +
                              str(int(mlfq_queue.MLFQ[i][j].gpu_num)))
                        print("gmem num: " +
                              str(int(mlfq_queue.MLFQ[i][j].threads_num)))

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    mlfq_queue.MLFQ[i][j].last_running_state = mlfq_queue.MLFQ[
                        i][j].is_running

            for i in range(len(mlfq_queue.MLFQ)):
                mlfq_queue.MLFQ[i].clear()

            for i in range(len(init_tir.jobs)):
                init_tir.jobs[i].is_running = 0

            predictable_queue.service_queue.clear()
            mlfq_queue.schedule_queue.clear()
        # break
        finish_job(now_time)
        mlfq_sequence(now_time)
        # if now_time % 300 == 0:
        #     os.system("bash /home/tank/maozz/del.sh")


if __name__ == '__main__':
    main()
