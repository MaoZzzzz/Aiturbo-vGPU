import sys
from resources_define import Job, Pod

jobs = []
pods = []

def read_jobs(path) -> None:
    for line in open(path):
        line.replace(" ","	")
        line_temp = line.split("\t")

        if not line_temp[0].isdigit():
            continue

        job_temp = Job()
        job_temp.id = line_temp[0]
        job_temp.model_name = line_temp[1]
        job_temp.batch_size = line_temp[2]
        job_temp.synch = line_temp[3]
        job_temp.target_loss = line_temp[4]
        job_temp.total_steps = line_temp[5]
        job_temp.arrive_time = line_temp[6]
        job_temp.finish_time = line_temp[7]
        job_temp.job_state = line_temp[8]
        job_temp.ps_num = line_temp[9]
        job_temp.worker_num = line_temp[10]
        job_temp.ps_source_type = line_temp[11]
        job_temp.worker_source_type = line_temp[12]
        job_temp.gpu_num = line_temp[13]
        job_temp.cpu_core_worker = line_temp[14]
        job_temp.cpu_core_ps = line_temp[15]
        job_temp.threads_num = line_temp[16].replace("\n","")
        jobs.append(job_temp)

def read_pods(path) -> None:
    for line in open(path):
        line_temp = line.split("\t")

        if not line_temp[0].isdigit():
            continue

        pod_temp = Pod()
        pod_temp.id = line_temp[0]
        pod_temp.pod_name = line_temp[1]
        pod_temp.docker_id = line_temp[2]
        pod_temp.ip = line_temp[3]
        pod_temp.cpu_num = line_temp[4]
        pod_temp.gpu_num = line_temp[5]
        pod_temp.is_using = line_temp[6]
        pods.append(pod_temp)
        # pod_temp.job_id
        # pod_temp.cpu_list
        # pod_temp.gpu_list


def init_jobs():
    read_jobs("/home/tank/maozz/test/exec/systemData/5jobs.txt")

def main():
    print("1" + " " + "1")
    print("1" + "\t" + "1")
    # init_jobs()
    # for i in range(len(jobs)):
    #     print(jobs[i].model_name + " " + "".join(jobs[i].target_loss))   

if __name__ == '__main__':
	main()