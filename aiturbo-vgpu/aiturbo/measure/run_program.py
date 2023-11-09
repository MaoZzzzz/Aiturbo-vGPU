import sys
import utils
import os
from job import Job

global logger
logger = utils.getLogger('measure-speed')
node_list = ['kube-master', 'kube-node1']
node = 0
job_list = []
jobs = []


def read_jobs(path) -> None:
    global node
    cwd = os.getcwd() + '/'
    for line in open(path):
        line.replace(" ", "	")
        line_temp = line.split("\t")

        if not line_temp[0].isdigit():
            continue

        id = line_temp[0]
        job_temp = Job('measurement-imagenet', id, cwd)
        job_temp.set_ps_resources(int(line_temp[9]), int(line_temp[15]), 0, 0)
        job_temp.set_worker_resources(int(line_temp[10]), int(line_temp[14]), int(
            line_temp[13]), int(line_temp[16].replace("\n", "")))

        job_temp.set_network(line_temp[1], '')
        if str(line_temp[3]) == 'TRUE':
            job_temp.set_training(line_temp[5], 'sync')
        else:
            job_temp.set_training(line_temp[5], 'async')
        job_temp.set_batch_size(line_temp[2])

        image = 'mps-tensorflow-gpu-experiment:latest'
        script = '/init.sh'
        prog = '/tf/benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py'
        work_dir = '/tf/benchmarks/scripts/data/'
        # datasets = 'cifar10'
        datasets = 'imagenet'
        mount_dir_prefix = '/data/k8sworkdir/measurement/'

        job_temp.set_container(image, script, prog, work_dir, mount_dir_prefix,
                               datasets)
        job_temp.set_data(data_dir='')
        job_temp.set_disp('1')

        jobs.append(job_temp)


def init_job(job_id_list):
    read_jobs("/home/tank/maozz/test/exec/systemData/5jobs.txt")

    for i in range(len(job_id_list)):
        for j in range(len(jobs)):
            if str(jobs[j].id) == str(job_id_list[i]):
                job_list.append(jobs[j])
                break

    master = [30, 200]
    node1 = [30, 200]
    for i in range(len(job_list)):
        job_temp = job_list[i]
        ps_placement = []
        worker_placement = []
        if int(job_temp.num_ps) * int(job_temp.ps_cpu) <= master[0] and int(job_temp.num_worker) * int(job_temp.worker_gpu) <= master[1]:
            master[0] = master[0] - int(job_temp.num_ps) * int(job_temp.ps_cpu)
            master[1] = master[1] - int(job_temp.worker_gpu)
            node_placement = 'kube-master'
            for i in range(int(job_temp.num_ps)):
                ps_placement.append(node_placement)
            for i in range(int(job_temp.num_worker)):
                worker_placement.append(node_placement)
            job_temp.set_ps_placement(ps_placement)
            job_temp.set_worker_placement(worker_placement)
        elif int(job_temp.num_ps) * int(job_temp.ps_cpu) <= node1[0] and int(job_temp.num_worker) * int(job_temp.worker_gpu) <= node1[1]:
            node1[0] = node1[0] - int(job_temp.num_ps) * int(job_temp.ps_cpu)
            node1[1] = node1[1] - int(job_temp.worker_gpu)
            node_placement = 'kube-node1'
            for i in range(int(job_temp.num_ps)):
                ps_placement.append(node_placement)
            for i in range(int(job_temp.num_worker)):
                worker_placement.append(node_placement)
            job_temp.set_ps_placement(ps_placement)
            job_temp.set_worker_placement(worker_placement)
        else:
            for i in range(int(job_temp.num_ps)):
                ps_placement.append('none')
            for i in range(int(job_temp.num_worker)):
                worker_placement.append('none')
            job_temp.set_ps_placement(ps_placement)
            job_temp.set_worker_placement(worker_placement)

def delete_job(job_id_list, flag) -> None:
    '''
    delete jobs, including the file where the log is located, the file where the yaml is located, and the job in k8s
    '''
    for j in range(len(job_id_list)):
        index = -1
        job_id = job_id_list[j]
        if len(job_list) != 0:
            for i in range(len(job_list)):
                if job_list[i].id == job_id:
                    index = i
                    break
            if str(index) != "-1":
                job_list[int(index)].delete(flag)
                del job_list[int(index)]


def run_job(job_id_list) -> None:
    '''
    run job
    '''
    for j in range(len(job_id_list)):
        index = -1
        job_id = job_id_list[j]
        if len(job_list) != 0:
            for i in range(len(job_list)):
                if job_list[i].id == job_id:
                    index = i
                    break
            if str(index) != "-1":
                job_list[int(index)].start()


def get_now_step(job_id) -> int:
    '''
    get the current steps
    '''
    index = -1
    if len(job_list) != 0:
        for i in range(len(job_list)):
            if job_list[i].id == job_id:
                index = i
                break

        if str(index) == "-1":
            return -1

        path = job_list[int(index)].checkpoint + "checkpoint"

        if not os.path.exists(path):
            return -1

        first_line = []
        # read the current step of the model in the first line of the file
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            first_line = lines[0]
        return first_line.split(" ")[1].split("-")[1][:-2]
    return -1


# def init_job(id, ps_resources, worker_resources, network, training, batch_size,
#              init_flag):
#     '''
#     initialization job
#     '''
#     global node
#     cwd = os.getcwd() + '/'
#     job = Job('measurement-imagenet', id, cwd)
#     # placement_list = node_list * 20
#     # num_ps, ps_cpu, ps_gpu, ps_gmem
#     job.set_ps_resources(int(ps_resources[0]), 5, 0, 0)
#     # num_worker, worker_cpu, worker_gpu, worker_gmem
#     job.set_worker_resources(int(worker_resources[0]), 1,
#                              int(worker_resources[1]),
#                              int(worker_resources[2]))

#     node_placement = ""
#     if node % 2 == 0:
#         node_placement = node_list[0]
#     else:
#         node_placement = node_list[1]

#     ps_placement = []
#     worker_placement = []

#     node += 1
#     for i in range(int(ps_resources[0])):
#         ps_placement.append(node_placement)
#     for i in range(int(worker_resources[0])):
#         worker_placement.append(node_placement)

#     job.set_ps_placement(ps_placement)
#     job.set_worker_placement(worker_placement)
#     job.set_network(network, '')
#     job.set_training(training, 'sync')
#     job.set_batch_size(batch_size)

#     image = 'mps-tensorflow-gpu-experiment:latest'
#     script = '/init.sh'
#     prog = '/tf/benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py'
#     work_dir = '/tf/benchmarks/scripts/data/'
#     # datasets = 'cifar10'
#     datasets = 'imagenet'
#     mount_dir_prefix = '/data/k8sworkdir/measurement/'

#     job.set_container(image, script, prog, work_dir, mount_dir_prefix,
#                       datasets)
#     job.set_data(data_dir='')
#     job.set_disp('1')

#     if init_flag == False:
#         job.start()

#     job_list.append(job)

#     return node_placement


def main():
    init_job(2, [2], [2, 200, 88], "alexnet", "1024", "1024", True)
    run_job(2)
    # for i in range(len(job_list)-1, -1, -1):
    #     print(i)
    #     # delete_job(job_list[i].id)


if __name__ == '__main__':
    main()
