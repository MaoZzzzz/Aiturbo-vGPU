from ast import Str
import sys

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
running_time = [0,0,0,0,0,0,0,0,0,0]
queue_time = [0,0,0,0,0,0,0,0,0,0]

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
    # time_all = []
    # path = "/home/tank/maozz/test/exec/systemData/temp.txt"
    # for line in open(path):
    #     line = line.replace("\n", "")
    #     line_temp = line.split("\t")

    #     temp = []
    #     temp.append(line_temp[0])
    #     temp.append(line_temp[1])
    #     time_all.append(temp)

    # for i in range(len(time_all)):
    #     if str(time_all[i][0]) == str(now_time):
    #         las_queue.las_job_finish(i + 1)
    #         print("Job " + str(i + 1) + " is over")
    #     if str(time_all[i][1]) == str(now_time):
    #         las_queue.become_predictable(i + 1)
    '''
    judging that homework completes or turns predictable
    '''
    for i in range(len(init.jobs)):
        current_step = run_program.get_now_step(init.jobs[i].id)
        print("job " + str(init.jobs[i].id) + " current step is: " + str(current_step))
        if current_step != -1:
            # print("now job : " + init.jobs[i].id + " " + current_step)
            if int(current_step) >= int(init.jobs[i].total_steps):
                las_queue.las_job_finish(init.jobs[i].id)
                predictable_queue.adjust_job_finish(init.jobs[i].id)
                run_program.delete_job(init.jobs[i].id, True)
                init.jobs[i].finish_time = now_time
                print("Job " + str(i + 1) + " is over")


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
        if current_step != -1 and init.jobs[i].finish_time == '0':
            if str(time_all[i][1]) == '99999':
                continue
            print("作业 " + init.jobs[i].id + " 的当前步骤是 " + str(current_step))
            print("达到可预测的步骤数：" + str(int(init.jobs[i].total_steps) * (
                float(time_all[i][1]) / float(time_all[i][0]))))
            if int(current_step) >= int(int(init.jobs[i].total_steps) * (float(time_all[i][1]) / float(time_all[i][0]))) and str(init.jobs[i].predict_acc) == "0.0":
                las_queue.become_predictable(i + 1)
                return True
    return False


def mlfq_sequence(now_time) -> None:
    path = "/home/tank/maozz/experiment/experiment1/aiturbo.txt"

    job_running = []
    for i in range(len(init.jobs)):
        if str(init.jobs[i].finish_time) == '0' and str(init.jobs[i].is_running) == '1':
            job_run = "Job " + \
                init.jobs[i].id + " resources: " + str(init.jobs[i].ps_num) + " " + str(
                    init.jobs[i].worker_num) + " " + str(init.jobs[i].gpu_num) + " " + "\n"
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

    if now_time % 10 == 0:
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
        is_predict = predictable_job()
        las_queue.unpredict_to_predict()

        # print("LAS_GPU queue length:" + str(len(las_queue.LAS_GPU)))
        if now_time % 240 == 0 or is_predict:
            predictable_queue.empty_queue()
            predictable_queue.resource_benefit_calculation()
            predictable_queue.resource_incre_queue.sort(
                key=lambda job: float(job.service_add))
            predictable_queue.resource_decre_queue.sort(
                key=lambda job: float(job.service_delete))
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

            run_program.delete_job(
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], False)
            run_program.init_job(job_id)
            run_program.run_job(job_id)

            # for i in range(len(mlfq_queue.MLFQ)):
            #     for j in range(len(mlfq_queue.MLFQ[i])):
            #         if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
            #             init_job(mlfq_queue.MLFQ[i][j])

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        running_time[int(mlfq_queue.MLFQ[i][j].id)-1] = running_time[int(mlfq_queue.MLFQ[i][j].id)-1] + 300
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

            for i in range(len(init.jobs)):
                init.jobs[i].is_running = 0

            predictable_queue.service_queue.clear()
            mlfq_queue.schedule_queue.clear()
        # elif now_time % 120 == 0 or is_arrive:
        elif is_arrive:
            # elif now_time % 120 == 0 or now_time == 1:
            # if now_time % 20 != 0:
            predictable_queue.calculate_service_queue()
            predictable_queue.calculate_sort_position()
            mlfq_queue.temp_caluculate_schedule_queue()
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

            run_program.delete_job(
                ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"], False)
            run_program.init_job(job_id)
            run_program.run_job(job_id)

            # for i in range(len(mlfq_queue.MLFQ)):
            #     for j in range(len(mlfq_queue.MLFQ[i])):
            #         if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
            #             init_job(mlfq_queue.MLFQ[i][j])

            for i in range(len(mlfq_queue.MLFQ)):
                for j in range(len(mlfq_queue.MLFQ[i])):
                    if str(mlfq_queue.MLFQ[i][j].is_running) == '1':
                        running_time[int(mlfq_queue.MLFQ[i][j].id)-1] = running_time[int(mlfq_queue.MLFQ[i][j].id)-1] + 300
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

            for i in range(len(init.jobs)):
                init.jobs[i].is_running = 0

            predictable_queue.service_queue.clear()
            mlfq_queue.schedule_queue.clear()
        # break
        finish_job(now_time)
        mlfq_sequence(now_time)


        # name = init.jobs[0].model_name + "_" + str(init.jobs[0].ps_num) + "_" + str(init.jobs[0].worker_num) + "_" + str(init.jobs[0].gpu_num)
        # filename = "/home/tank/maozz/experiment/step/{}.txt".format(name)
        # with open(filename,mode='a+') as f:
        #     string = str(now_time) + " " + str(run_program.get_now_step(init.jobs[0].id)) + "\n"
        #     f.write(string)
        # if now_time % 240 == 0:
        #     os.system("bash /home/tank/maozz/del.sh")


if __name__ == '__main__':
    main()
