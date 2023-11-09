from calendar import c
from math import ceil
import sys
import time
import datetime
import os
import threading
import subprocess


class Job(object):
    '''job description.
    Parameters
    ----------
    id: int
    num_ps: int
    num_worker: int
    other parameters: string or list of strings
    work to be done on Tuesday 8/8/2017: 
            (1) modify template file, worker and server mount different dirs
            (2) modify template file, set work_dir and export it as an env
            (3) add support for gpu and get_progress() if necessary
    '''

    def __init__(self, type, id, dir_prefix):
        '''initialize a job
        job type: eg., measurement-imagenet, i.e., category-dataset
        '''
        self.id = id
        self.name = str(id) + '-' + type

        now = time.time()
        self.timestamp = str(datetime.datetime.fromtimestamp(
            now).strftime('%Y-%m-%d-%H:%M:%S'))
        self.dir = dir_prefix + self.name + '-' + self.timestamp + '/'
        os.system('sudo mkdir -p ' + self.dir)

        self.num_ps = 0
        self.ps_cpu = '1'
        self.ps_gpu = '0'
        self.ps_gmem = '0'

        self.num_worker = 0
        self.worker_cpu = '1'
        self.worker_gpu = '100'
        self.worker_gmem = '44'

        self.ps_placement = ''
        self.worker_placement = ''

        self.disp_batches = '5'
        self.speed_list = []
        self.ps_metrics = []
        self.worker_metrics = []
        self.ps_pods = []
        self.worker_pods = []
        self.numsteps = []

        self.sync_meth = ''

    def set_ps_resources(self, num_ps, ps_cpu, ps_gpu, ps_gmem):
        '''resource requirements of parameter servers'''
        self.num_ps = num_ps
        # self.ps_cpu = str(ceil(int(ps_cpu)/int(num_ps)))
        self.ps_cpu = str(ps_cpu)
        self.ps_gpu = str(ps_gpu)
        self.ps_gmem = str(ps_gmem)

    def set_worker_resources(self, num_worker, worker_cpu, worker_gpu, worker_gmem):
        '''resource requirements of workers'''
        self.num_worker = num_worker
        self.worker_cpu = str(worker_cpu)
        self.worker_gpu = str(ceil(int(worker_gpu)/int(num_worker)))
        self.worker_gmem = str(ceil(int(worker_gmem)/int(num_worker)))

    def set_ps_placement(self, ps_placement):
        '''the placement of parameter servers'''
        if isinstance(ps_placement, list):
            if len(ps_placement) == self.num_ps:
                self.ps_placement = ps_placement
            else:
                raise RuntimeError(
                    'ps_placement is not consistent with num_ps')
        else:
            raise TypeError('ps_placement is not a list')

    def set_worker_placement(self, worker_placement):
        '''the placement of workers'''
        if isinstance(worker_placement, list):
            if len(worker_placement) == self.num_worker:
                self.worker_placement = worker_placement
            else:
                raise RuntimeError(
                    'worker_placement is not consistent with num_worker')
        else:
            raise TypeError('worker_placement is not a list')

    def _set_mount_dirs(self, type, mount_dir_prefix):
        '''directories on hosts mounted to containers'''
        mount_dirs = []
        if type == 'ps':
            for i in range(self.num_ps):
                postfix = self.name + '-ps-' + str(i) + '/'
                mount_dir = mount_dir_prefix + postfix
                mount_dirs.append(mount_dir)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "mkdir -p ' + mount_dir + '"'
                os.system(cmd)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "echo tankcloud | sudo chmod 777 ' + mount_dir + '"'
                os.system(cmd)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "touch ' + mount_dir + 'training.txt"'
                os.system(cmd)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "echo tankcloud | sudo chmod 777 ' + mount_dir + 'training.txt"'
                os.system(cmd)

        elif type == 'worker':
            for i in range(self.num_worker):
                postfix = self.name + '-worker-' + str(i) + '/'
                mount_dir = mount_dir_prefix + postfix
                mount_dirs.append(mount_dir)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "mkdir -p ' + mount_dir + '"'
                # cmd = 'sshpass -p tankcloud ssh root@' + \
                #     "kube-master" + ' "mkdir -p ' + mount_dir + '"'
                os.system(cmd)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "echo tankcloud | sudo chmod 777 ' + mount_dir + '"'
                os.system(cmd)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "touch ' + mount_dir + 'training.txt"'
                os.system(cmd)
                cmd = 'sshpass -p tankcloud ssh root@' + \
                    'kube-node1' + ' "echo tankcloud | sudo chmod 777 ' + mount_dir + 'training.txt"'
                os.system(cmd)
        return mount_dirs

    def _set_mount_hadoop_dirs(self, type, mount_dir_prefix):
        '''directories on hosts mounted to containers'''
        mount_dirs = []
        if type == 'ps':
            for i in range(self.num_ps):
                postfix = self.name + '-ps-' + str(i) + '/'
                mount_dir = mount_dir_prefix + postfix
                mount_dirs.append(mount_dir)
                cmd = 'hadoop fs -mkdir ' + mount_dir
                os.system(cmd)

        elif type == 'worker':
            for i in range(self.num_worker):
                postfix = self.name + '-worker-' + str(i) + '/'
                mount_dir = mount_dir_prefix + postfix
                mount_dirs.append(mount_dir)
                cmd = 'hadoop fs -mkdir ' + mount_dir
                os.system(cmd)
        return mount_dirs

    def _set_checkpoint(self, mount_dir_prefix):
        '''directory on hosts mounted to checkpoint'''
        postfix = self.name + '-checkpoint/'
        checkpoint_dir = mount_dir_prefix + postfix
        cmd = 'sshpass -p tankcloud ssh root@' + \
            'kube-node1' + ' "mkdir -p ' + checkpoint_dir + '"'
        os.system(cmd)
        cmd = 'sshpass -p tankcloud ssh root@' + \
            'kube-node1' + ' "echo tankcloud | sudo chmod 777 ' + checkpoint_dir + '"'
        os.system(cmd)
        return checkpoint_dir

    def _set_hadoop_checkpoint(self, mount_dir_prefix):
        '''directory on hosts mounted to checkpoint'''
        postfix = self.name + '-checkpoint/'
        checkpoint_dir = mount_dir_prefix + postfix
        cmd = 'hadoop fs -mkdir ' + checkpoint_dir
        os.system(cmd)
        return checkpoint_dir

    def set_container(self, image, script, prog, work_dir, mount_dir_prefix, datasets, volume='k8s-train-volume',):
        '''container description'''
        self.image = image
        self.script = script
        self.prog = prog
        self.work_dir = work_dir
        self.ps_mount_dirs = self._set_mount_dirs('ps', mount_dir_prefix)
        self.worker_mount_dirs = self._set_mount_dirs(
            'worker', mount_dir_prefix)
        self.checkpoint = self._set_checkpoint(mount_dir_prefix)
        self.datasets = datasets
        self.volume = volume

    def set_data(self, data_dir=''):
        '''data specification'''
        self.data_dir = data_dir

    def set_network(self, neural_network='', num_layers=''):
        '''neural network'''
        self.neural_network = neural_network
        self.num_layers = num_layers
        if num_layers == '':
            self.model_name = self.neural_network
        else:
            self.model_name = self.neural_network + '' + self.num_layers

    def set_batch_size(self, batch_size=''):
        '''neural network'''
        self.batch_size = batch_size

    def set_training(self, total_steps='', sync_meth=''):
        '''training hyper-parameters'''
        self.sync_meth = sync_meth

        # the batch size of each worker for sync training may be different
        if sync_meth == 'async':
            self.sync_mode = "async"
            self.numsteps = [total_steps for i in range(self.num_worker)]
        elif sync_meth == 'sync':
            self.sync_mode = "sync"
            avg_steps = int(total_steps) / int(self.num_worker)
            rem_steps = int(total_steps) % int(self.num_worker)
            numsteps = [int(avg_steps) for i in range(int(self.num_worker))]
            for i in range(rem_steps):
                numsteps[i] = numsteps[i] + 1
            self.numsteps = [str(i) for i in numsteps]

    def set_disp(self, disp_batches):
        '''display frequency'''
        self.disp_batches = str(disp_batches)

    def __list_to_str(self, _listofstr):
        string = ''
        for i in range(len(_listofstr)):
            if i < len(_listofstr) - 1:
                string = string + _listofstr[i] + ','
            else:
                string = string + _listofstr[i]
        return string

    def _create(self):
        '''create job definition, i.e., yaml file'''

        variables = {}
        variables['JOB_NAME'] = self.name
        variables['MODEL_NAME'] = self.model_name

        variables['IMAGE'] = self.image
        variables['SCRIPT'] = self.script
        variables['PROG'] = self.prog
        variables['DATASETS'] = self.datasets
        variables['WORK_DIR'] = self.work_dir
        # variables['DATA_DIR'] = self.data_dir
        variables['PS_MOUNT_DIRS'] = self.__list_to_str(self.ps_mount_dirs)
        variables['WORKER_MOUNT_DIRS'] = self.__list_to_str(
            self.worker_mount_dirs)
        variables['CHECKPOINT'] = self.checkpoint
        variables['VOLUME'] = self.volume
        variables['SYNC_MODE'] = self.sync_mode

        variables['NUM_PS'] = str(self.num_ps)
        variables['PS_CPU'] = self.ps_cpu
        variables['PS_GPU'] = self.ps_gpu
        variables['PS_GMEM'] = self.ps_gmem

        variables['NUM_WORKER'] = str(self.num_worker)
        variables['WORKER_CPU'] = self.worker_cpu
        variables['WORKER_GPU'] = self.worker_gpu
        variables['WORKER_GMEM'] = self.worker_gmem

        variables['PS_PLACEMENT'] = self.__list_to_str(self.ps_placement)
        variables['WORKER_PLACEMENT'] = self.__list_to_str(
            self.worker_placement)

        variables['NUMSTEPS'] = self.__list_to_str(self.numsteps)
        variables['GPU_FREC'] = str(round(int(self.worker_gmem)/44, 1))
        variables['BATCH_SIZE'] = self.batch_size

        variables['DISP_BATCHES'] = self.disp_batches

        # copy template file
        self.jinja = self.dir + self.name + '.jinja'
        os.system(
            "echo tankcloud | sudo cp /home/tank/maozz/test/templates/k8s-mxnet-template.jinja " + self.jinja)

        # replace variables in jinja file
        temp_file = self.jinja + '.temp'
        for key, value in variables.items():
            os.system('sed -e "s@\$' + key + '@' + value +
                      '@g" "' + self.jinja + '"' + ' > ' + temp_file)
            os.system('rm ' + self.jinja)
            os.system('mv ' + temp_file + ' ' + self.jinja)

        # generate yaml file
        self.yaml = self.dir + self.name + '.yaml'
        os.system("python /home/tank/maozz/test/templates/render-template.py " +
                  self.jinja + " > " + self.yaml)
        time.sleep(1)

    def _read_progress(self):
        '''get the job progress from each worker'''
        return

    def _read_training_speed(self):
        '''get the job training speed from each worker'''
        speed_fn = 'speed.txt'
        if self.speed_list is None or self.speed_list == []:
            self.speed_list = [0 for i in range(self.num_worker)]
        thread_list = []
        for i in range(self.num_worker):
            node = self.worker_placement[i]
            local_file = self.worker_mount_dirs[i] + speed_fn
            '''
			cmd = 'scp ' + node + ':' + local_file + ' ' + self.dir # the new txt will replace the old one, no need to delete
			os.system(cmd)
			try:
				with open(self.dir+speed_fn, 'r') as fh:
					stb_speed = float(fh.readline().replace('\n', '').split(' ')[1])
					self.speed_list[i] = float('%.3f'%(stb_speed))
			except Exception as e:
				print e
				continue
			'''
            cmd = "sshpass -p tankcloud ssh root@" + node + " 'cat " + local_file + "'"

            def run(self, cmd, i):
                try:
                    output = subprocess.check_output(cmd, shell=True)
                    # the other side is opening and writing the file, try again
                    counter = 0
                    while(output == '' or output == None):
                        output = subprocess.check_output(cmd, shell=True)
                        time.sleep(0.001*(10**counter))
                        counter = counter + 1
                        if counter > 2:
                            break
                    stb_speed = float(str(output).replace(
                        '\n', '').split(' ')[1][:-3])
                    self.speed_list[i] = float('%.3f' % (stb_speed))
                except Exception as e:
                    print(e)

            thread = threading.Thread(target=run, args=(self, cmd, i))
            thread.start()
            thread_list.append(thread)
        for thread in thread_list:
            thread.join()

    def get_model_name(self):
        return self.model_name

    def get_training_speed(self):
        self._read_training_speed()
        print(self.speed_list)
        return list(self.speed_list)

    def __get_pods(self, task):
        '''
        get the names of the pods belonging to the task

        NAME                                    READY     STATUS    RESTARTS   AGE
        1-measurement-imagenet-ps-0-mzv2z       1/1       Running   0          1m
        '''
        if task == 'ps':
            self.ps_pods = []
        elif task == 'worker':
            self.worker_pods = []
        else:
            raise ValueError('task can only either be ps or worker!')

        cmd = 'kubectl get pods --selector=' + 'name=' + self.name + \
            ',' + 'job=' + task + ' --namespace=mzz' + ' |grep ' + task
        output = subprocess.check_output(cmd, shell=True)
        lines = output.split('\n')
        for line in lines:
            if len(line) > 0:
                words = line.split(' ')
                if task == 'ps':
                    self.ps_pods.append(words[0])
                else:
                    self.worker_pods.append(words[0])

    def _read_metrics(self):
        '''get the metrics of the pods of this job'''

        # get ps pods
        self.__get_pods('ps')
        self.__get_pods('worker')

        # get heapster cluster ip
        # heapster               192.168.192.16    <none>        80/TCP              5d
        #cmd = "kubectl get services --namespace=kube-system | grep heapster |awk '{print $2}'"
        cmd = "kubectl get services --namespace=mzz | grep heapster |awk '{print $2}'"
        heapster_cluster_ip = subprocess.check_output(
            cmd, shell=True).replace('\n', '')
        if heapster_cluster_ip == '':
            heapster_cluster_ip = '192.168.192.16'

        '''
		{
		  "metrics": [
		   {
		    "timestamp": "2017-08-14T08:10:00Z",
		    "value": 0
		   }
		  ],
		  "latestTimestamp": "2017-08-14T08:10:00Z"
		 }
		'''
        self.ps_metrics = []
        self.worker_metrics = []
        # cpu: milli core, mem: bytes, net: bytes/second
        metric_keys = ['cpu/usage_rate', 'memory/usage',
                       'network/tx_rate', 'network/rx_rate']
        for pod in (self.ps_pods + self.worker_pods):
            pod_metrics = {}
            for metric_key in metric_keys:
                url = 'http://' + heapster_cluster_ip + \
                    '/api/v1/model/namespaces/default/pods/' + pod + '/metrics/' + metric_key
                try:
                    output = requests.get(url, verify=False).json()
                    # get latest value, maybe empty since heapster update metrics per minute
                    metric_value = int(output['metrics'][-1]['value'])
                except:
                    # print "ERROR when requesting pod metrics!"
                    metric_value = 0
                pod_metrics[metric_key] = metric_value
            if pod in self.ps_pods:
                self.ps_metrics.append(pod_metrics)
            else:
                self.worker_metrics.append(pod_metrics)

    def get_metrics(self):
        self._read_metrics()
        return (list(self.ps_metrics), list(self.worker_metrics))

    def start(self):
        '''start the job in k8s'''
        self._create()
        # sys.exit()
        os.system("sudo kubectl create -f " + self.yaml)

    def delete(self, del_all=False):
        '''delete the job.
        Parameters
        ----------
        del_all: whether to delete all, including histories.
        '''

        # shutdown job in k8s

        temp_dir = self.dir + 'temp/'
        os.system('mkdir -p ' + temp_dir)

        # fh = open(self.yaml, 'r')
        # yamls = fh.read().split('---\n')
        # fh.close()

        # thread_list = []
        # for i in range(len(yamls)):
        #     if len(yamls[i]) <= 1:  # skip invalid
        #         continue
        #     name = temp_dir + str(i) + '.yaml'
        #     with open(name, 'w') as fh:
        #         fh.write(yamls[i])
        #     thread = threading.Thread(
        #         target=(lambda name=name: os.system('echo tankcloud | sudo kubectl delete -f ' + name)), args=())
        #     thread.start()
        #     thread_list.append(thread)
        #     # time.sleep(0.01)	# to avoid thread conflict reading the same variable name

        # for thread in thread_list:
        #     thread.join()
        # os.system('rm -r ' + temp_dir)

        # in case not delete all
        os.system(
            'echo tankcloud | sudo kubectl delete jobs -n mzz --selector=name=' + self.name)

        if del_all == False:
            return

        # remove mounted dirs on hosts
        thread_list = []
        for i in range(self.num_worker):
            # node = self.worker_placement[i]
            worker_mount_dir = self.worker_mount_dirs[i]
            cmd = 'timeout 10 sshpass -p tankcloud ssh root@192.168.1.135' + \
                ' "sudo rm -r ' + worker_mount_dir + '"'
            thread = threading.Thread(
                target=(lambda cmd=cmd: os.system(cmd)), args=())
            thread.start()
            thread_list.append(thread)

        for i in range(self.num_ps):
            # node = self.ps_placement[i]
            ps_mount_dir = self.ps_mount_dirs[i]
            cmd = 'timeout 10 sshpass -p tankcloud ssh root@192.168.1.135' + \
                ' "sudo rm -r ' + ps_mount_dir + '"'
            thread = threading.Thread(
                target=(lambda cmd=cmd: os.system(cmd)), args=())
            thread.start()
            thread_list.append(thread)\

        checkpoint_dir = self.checkpoint
        cmd = 'timeout 10 sshpass -p tankcloud ssh root@192.168.1.135' + \
            ' "sudo rm -rf ' + checkpoint_dir + '"'
        thread = threading.Thread(
            target=(lambda cmd=cmd: os.system(cmd)), args=())
        thread.start()
        thread_list.append(thread)

        for thread in thread_list:
            thread.join()
        # delete job working dir
        os.system('rm -r ' + self.dir)
