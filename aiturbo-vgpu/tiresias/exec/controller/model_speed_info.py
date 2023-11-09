import os
import time
import sys
from pyexpat import model


# model_name = ["vgg11", "vgg16", "vgg19", "lenet", "googlenet", "overfeat", "alexnet", "trivial", "inception3",
#               "inception4", "resnet50", "resnet101", "resnet152", "mobilenet"]
# batch_size = ["128", "64", "32", "1024", "256",
#               "512", "1024", "1024", "64", "32", "64", "64", "32", "1024"]

model_name = ["trivial"]
batch_size = ["1024"]

modelname = ""
batchsize = ""
numbatches = ""
numps = ""
numworker = ""
gpu = ""
gmem = ""
string = "1" + "\t" + modelname + "\t" + batchsize + "\t" + "TRUE" + "\t" + "0.3" + "\t" + "300" + "\t" + \
    "1" + "\t" + "0" + "\t" + "0" + "\t" + numps + "\t" +\
    numworker + "\t" + "cpu" + "\t" + "gpu" + "\t" + \
    gpu + "\t" + "1" + "\t" + "5" + "\t" + gmem

# num_ps = ["1", "1", "1", "1", "1", "1", "1", "1"]
# num_worker = ["1", "1", "1", "1", "1", "1", "1", "1"]
# gpus = ["30", "40",
#         "50", "60", "70", "80", "90", "100"]
# gmems = ["44", "44",
#          "44", "44", "44", "44", "44", "44"]

num_ps = ["1"]
num_worker = ["1"]
gpus = ["100"]
gmems = ["44"]

for i in range(len(model_name)):
    modelname = model_name[i]
    batchsize = batch_size[i]
    for j in range(len(num_ps)):
        numps = num_ps[j]
        numworker = num_worker[j]
        gpu = gpus[j]
        gmem = gmems[j]
        # string = "1" + "\t" + modelname + "\t" + batchsize + "\t" + "TRUE" + "\t" + "0.3" + "\t" + "2000" + "\t" + \
        #     "1" + "\t" + "0" + "\t" + "0" + "\t" + numps + "\t" +\
        #     numworker + "\t" + "cpu" + "\t" + "gpu" + "\t" + \
        #     gpu + "\t" + "1" + "\t" + "5" + "\t" + gmem

        string = "1" + "\t" + modelname + "\t" + batchsize + "\t" + "TRUE" + "\t" + "0.3" + "\t" + "300" + "\t" + \
            "1" + "\t" + "0" + "\t" + "0" + "\t" + numps + "\t" +\
            numworker + "\t" + "cpu" + "\t" + "gpu" + "\t" + \
            gpu + "\t" + "1" + "\t" + "5" + "\t" + gmem

        print(string)
        # sys.exit()
        file = open(
            "/home/tank/maozz/test/exec/systemData/5jobs.txt", 'w').close()
        with open("/home/tank/maozz/test/exec/systemData/5jobs.txt", "a+") as f:
            f.write("id	model_name	batch_size	synch	target_loss	total_steps	arrive_time	finish_time	job_state	ps_num	worker_num	ps_source_type	worker_source_type	gpu_num	cpu_core_worker	cpu_core_ps	threads_num" + "\n")
            f.write(string)
        os.system("python /home/tank/maozz/test/exec/controller/stop.py")
        os.system("kubectl delete jobs,daemonsets -n mzz --all")
        os.system(
            "sshpass -p tankcloud ssh root@192.168.1.135 sudo rm -rf /data/k8sworkdir/measurement/ *")
        time.sleep(5)
