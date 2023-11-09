import os
import threading


class Job(object):
    def __init__(self) -> None:
        # can read from the file
        self.id = 0
        self.model_name = ''
        self.batch_size = 0
        self.target_loss = 0.0
        self.total_steps = 0
        self.synch = True
        self.arrive_time = 0
        self.finish_time = 0
        self.job_state = 0 
        self.ps_num = 0
        self.worker_num = 0
        self.ps_source_type = ''
        self.worker_source_type = ''
        self.gpu_num = 0
        self.cpu_core_worker = 0
        self.cpu_core_ps = 0
        self.threads_num = 0
        
        # constantly changing while the program is running
        self.predict_acc = 0.0
        self.service_get = 0.0

        # job information needed for resource adjustment
        self.service_get = 0.0
        self.service_get_sort = 0
        self.service_add = 0.0
        self.service_add_sort = 0
        self.service_add_choice = -1
        self.service_delete = 0.0
        self.service_delete_sort = 0
        self.service_delete_choice = -1
        self.schedule_sort = 0

        # temporary variables while the job is running
        self.ps_num_temp = 0
        self.worker_num_temp = 0
        self.gpu_num_temp = 0
        self.threads_num_temp = 0

        # whether it is running in the cluster
        self.is_running = '0'
        self.last_running_state = '0'

    def setPredict_acc(self, predict_acc) -> None:
        self.predict_acc = predict_acc

    def delete(self, del_all=False):
        '''delete the job.
        Parameters
        ----------
        del_all: whether to delete all, including histories.
        '''
        # shutdown job in k8s
        temp_dir = self.dir + 'temp/'
        os.system('mkdir -p ' + temp_dir)

        fh = open(self.yaml, 'r')
        yamls = fh.read().split('---\n')
        fh.close()

        thread_list = []
        for i in range(len(yamls)):
            if len(yamls[i]) <= 1:  # skip invalid
                continue
            name = temp_dir + str(i) + '.yaml'
            with open(name, 'w') as fh:
                fh.write(yamls[i])
            thread = threading.Thread(
                target=(lambda name=name: os.system('echo tanklab | sudo kubectl delete -f ' + name)), args=())
            thread.start()
            thread_list.append(thread)
            # time.sleep(0.01)	# to avoid thread conflict reading the same variable name

        for thread in thread_list:
            thread.join()
        os.system('rm -r ' + temp_dir)

        # in case not delete all
        os.system('echo tanklab | sudo kubectl delete jobs -n mzz --selector=name=' + self.name)

        if del_all == False:
            return

        # remove mounted dirs on hosts
        thread_list = []
        for i in range(self.num_worker):
            node = self.worker_placement[i]
            worker_mount_dir = self.worker_mount_dirs[i]
            cmd = 'timeout 10 sshpass -p tanklab ssh root@' + node + ' "sudo rm -r ' + worker_mount_dir + '"'
            thread = threading.Thread(
                target=(lambda cmd=cmd: os.system(cmd)), args=())
            thread.start()
            thread_list.append(thread)

        for i in range(self.num_ps):
            node = self.ps_placement[i]
            ps_mount_dir = self.ps_mount_dirs[i]
            cmd = 'timeout 10 sshpass -p tanklab ssh root@' + node + ' "sudo rm -r ' + ps_mount_dir + '"'
            thread = threading.Thread(
                target=(lambda cmd=cmd: os.system(cmd)), args=())
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()
        # delete job working dir
        os.system('rm -r ' + self.dir)

class Pod(object):
    def __init__(self) -> None:
        self.id = 0
        self.pod_name = ''
        self.docker_id = ''
        self.ip = ''
        self.cpu_num = ''
        self.gpu_num = ''
        self.is_using = False
        self.job_id = ''
        self.cpu_list = []
        self.gpu_list = []

class Model(object):
    def __init__(self) -> None:
        self.model_name = ''
        self.speed_model_para_cpu = []
        self.speed_model_para_gpu = []
        self.cpu_worker_para = []
        self.cpu_ps_para = []
        self.mps_para = []