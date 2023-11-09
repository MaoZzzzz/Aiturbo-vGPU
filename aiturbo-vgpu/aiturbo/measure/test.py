import logging
import utils
import time
import os
from measure.job import Job
import sys

global logger
logger = utils.getLogger('measure-speed')
logger.info("clear all existing jobs")
os.system("echo tanklab | sudo kubectl delete jobs,daemonsets -n mzz --all")


job_name_list = ['alexnet', 'resnet-50', 'vgg-11',
                 'inception-bn', 'resnet-152', 'resnet-101']
neural_network_list = ['alexnet', 'resnet',
                       'vgg', 'inception-bn', 'resnet', 'resnet']
num_layers_list = ['', '50', '11', '', '152', '101']

node_list = ['tank-master']
ps_cpu = "10"
ps_gpu = "0"
ps_gmem = "0"  # 1对应的是256m，44对应11G
worker_cpu = "10"
worker_gpu = "40"
worker_gmem = "40"


job_id = 0
cwd = os.getcwd() + '/'
stats = []  # element format (#ps, #worker, speed, cpu)
txt = 'stats.txt'
if os.path.isfile(txt):  # back up
    time_str = str(int(time.time()))
    fn = './results/' + time_str + '.' + txt
    os.system('cp ' + txt + ' ' + fn)
f = open(txt, 'w')  # clear txt
f.close()

tic = time.time()
job_id = 1
num_ps = 1
num_worker = 1
batch_size = '128'

logger.info("------------------start job " +
            str(job_id) + "-------------------")
toc = time.time()
logger.info("time elapsed: " + str((toc-tic)/60) + " minutes")

measure_job = Job('measurement-imagenet', job_id, cwd)
measure_job.set_ps_resources(num_ps, ps_cpu, ps_gpu, ps_gmem)
# measure_job.set_ps_placement(node_list[:num_ps])

measure_job.set_worker_resources(
    num_worker, worker_cpu, worker_gpu, worker_gmem)
# measure_job.set_worker_placement(node_list[num_ps:num_ps+num_worker])

placement_list = node_list * 6
measure_job.set_ps_placement(placement_list[:num_ps])
measure_job.set_worker_placement(
    placement_list[num_ps:num_ps+num_worker])

image = 'mps-tensorflow-gpu-experiment:latest'
script = '/init.sh'
# script = '"-c", "while true; do echo hello; sleep 10;done"'
# script = '-c, while true; do echo hello; sleep 10;done'
prog = '/tf/benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py'
work_dir = '/tf/benchmarks/scripts/data/'
datasets = 'cifar10'
mount_dir_prefix = '/data/k8s-workdir/measurement/'
measure_job.set_container(
    image, script, prog, work_dir, mount_dir_prefix, datasets)

measure_job.set_data(data_dir='')
measure_job.set_network('resnet', '20')
measure_job.set_training('100', batch_size, "kv_store", gpus='')
measure_job.set_disp('1')

measure_job.start()

counter = 0
while(True):
    try:
        time.sleep(60)
    except:
        logger.info("detect Ctrl+C, exit...")
        measure_job.delete(True)
        sys.exit(0)

    counter += 1
    try:
        speed_list = measure_job.get_training_speed()
        # (ps_metrics, worker_metrics) = measure_job.get_metrics()
    except:
        logger.info("get training speed error!")
        measure_job.delete(True)
        sys.exit(0)

    model_name = measure_job.get_model_name()
    logger.info("model name: " + model_name + ", batch_size: " + batch_size +
                ", num_ps: " + str(num_ps) + ", num_worker: " + str(num_worker) +
                ", speed_list: " + str(speed_list) + ", sum_speed (samples/second): " + str(sum(speed_list)) +
                ", sum_speed(batches/second): " + str(sum(speed_list)/int(batch_size))
                )
    if counter >= 5:
        stat = (model_name, "", batch_size, num_ps, num_worker, speed_list)
        stats.append(stat)
        with open(txt, 'a') as f:  # append
            # for stat in stats:
            f.write(str(stat) + '\n')

        measure_job.delete(True)
        logger.info("sleep 3 seconds before next job")
        time.sleep(3)
        break
