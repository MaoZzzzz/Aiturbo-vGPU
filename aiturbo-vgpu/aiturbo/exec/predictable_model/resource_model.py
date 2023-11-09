from turtle import backward, forward
import predict_model
import init_model
import sys
import math
sys.path.append('/home/tank/maozz/test/exec/define')


def cpu_efficiency_worker(a, b, d, x) -> float:
    cpu_eff = float(a) * math.exp(float(b) * float(x) * -1) + float(d)
    return cpu_eff

def cpu_efficiency_ps(a, b, d, x) -> float:
    cpu_eff = float(a) * math.exp(float(b) * float(x) * -1) + float(d)
    return cpu_eff

def speed_func(job) -> float:
    '''
    calculate the step speed model
    '''
    for i in range(len(init_model.models)):
        if job.model_name == init_model.models[i].model_name:
            cpu_ps = init_model.models[i].cpu_ps_para
            cpu_worker = init_model.models[i].cpu_worker_para
            cpu_speed = init_model.models[i].speed_model_para_cpu
            gpu_speed = init_model.models[i].speed_model_para_gpu
            forward = init_model.models[i].forward
            backward = init_model.models[i].backward

            if job.ps_source_type == 'cpu' and job.worker_source_type == 'gpu':
                max100 = float(predict_model.speed_func_syn(gpu_speed[0], gpu_speed[1], gpu_speed[2], gpu_speed[3], gpu_speed[4], gpu_speed[5], gpu_speed[6], int(job.worker_num), int(job.ps_num), int(job.batch_size)/int(job.worker_num), int(job.worker_num), 1/cpu_efficiency_ps(cpu_ps[0], cpu_ps[1], cpu_ps[2], job.cpu_core_ps), 1))
                cofe = (float(backward[0]) / (float(backward[1]) + 100)) + float(backward[2])
                min1 = max100 / cofe
                now_cofe = ((float(backward[0]) / (float(backward[1]) + int(job.gpu_num)/int(job.worker_num))) + float(backward[2])) * min1
                return min1 * now_cofe
            elif job.ps_source_type == 'cpu' and job.worker_source_type == 'cpu':
                x = float(predict_model.speed_func_syn(cpu_speed[0], cpu_speed[1], cpu_speed[2], cpu_speed[3], cpu_speed[4], cpu_speed[5], 0, int(job.worker_num), int(job.ps_num), int(job.batch_size)/int(job.worker_num), 0, 1/cpu_efficiency_ps(cpu_ps[0], cpu_ps[1], cpu_ps[2], job.cpu_core_ps), 1/cpu_efficiency_worker(cpu_worker[0], cpu_worker[1], cpu_worker[2], job.cpu_core_worker)))
                return x
    return 0

def speed_func_optimus(job) -> float:
    '''
    calculate the step speed model
    '''
    for i in range(len(init_model.models)):
        if job.model_name == init_model.models[i].model_name:
            cpu_ps = init_model.models[i].cpu_ps_para
            cpu_worker = init_model.models[i].cpu_worker_para
            cpu_speed = init_model.models[i].speed_model_para_cpu
            gpu_speed = init_model.models[i].speed_model_para_gpu
            forward = init_model.models[i].forward
            backward = init_model.models[i].backward

            # if job.ps_source_type == 'cpu' and job.worker_source_type == 'gpu':
            #     return predict_model.speed_func_syn_optimus(gpu_speed[0], gpu_speed[1], gpu_speed[2], gpu_speed[3], gpu_speed[4], gpu_speed[5], gpu_speed[6], int(job.worker_num), int(job.ps_num), int(job.batch_size)/int(job.worker_num), int(job.gpu_num), 1/cpu_efficiency_ps(cpu_ps[0], cpu_ps[1], cpu_ps[2], job.cpu_core_ps), 1)
            # elif job.ps_source_type == 'cpu' and job.worker_source_type == 'cpu':
            #     return predict_model.speed_func_syn_optimus(cpu_speed[0], cpu_speed[1], cpu_speed[2], cpu_speed[3], cpu_speed[4], cpu_speed[5], 0, int(job.worker_num), int(job.ps_num), int(job.batch_size)/int(job.worker_num), 0, 1/cpu_efficiency_ps(cpu_ps[0], cpu_ps[1], cpu_ps[2], job.cpu_core_ps), 1/cpu_efficiency_worker(cpu_worker[0], cpu_worker[1], cpu_worker[2], job.cpu_core_worker))

            if job.ps_source_type == 'cpu' and job.worker_source_type == 'gpu':
                max100 = float(predict_model.speed_func_syn_optimus(gpu_speed[0], gpu_speed[1], gpu_speed[2], gpu_speed[3], gpu_speed[4], gpu_speed[5], gpu_speed[6], int(job.worker_num), int(job.ps_num), int(job.batch_size)/int(job.worker_num), int(job.worker_num), 1/cpu_efficiency_ps(cpu_ps[0], cpu_ps[1], cpu_ps[2], job.cpu_core_ps), 1))
                cofe = (float(backward[0]) / (float(backward[1]) + 100)) + float(backward[2])
                min1 = max100 / cofe
                now_cofe = ((float(backward[0]) / (float(backward[1]) + int(job.gpu_num)/int(job.worker_num))) + float(backward[2])) * min1
                return min1 * now_cofe
            elif job.ps_source_type == 'cpu' and job.worker_source_type == 'cpu':
                x = float(predict_model.speed_func_syn_optimus(cpu_speed[0], cpu_speed[1], cpu_speed[2], cpu_speed[3], cpu_speed[4], cpu_speed[5], 0, int(job.worker_num), int(job.ps_num), int(job.batch_size)/int(job.worker_num), 0, 1/cpu_efficiency_ps(cpu_ps[0], cpu_ps[1], cpu_ps[2], job.cpu_core_ps), 1/cpu_efficiency_worker(cpu_worker[0], cpu_worker[1], cpu_worker[2], job.cpu_core_worker)))
                return x
    
    return 0