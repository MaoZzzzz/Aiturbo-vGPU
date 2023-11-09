import sys

sys.path.append('/home/tank/maozz/test/exec/define')
sys.path.append('/home/tank/maozz/test/measure')

import resource_model
import run_program

def predict_model(beta0, beta1, beta2, loss) -> int:
    re_step = 0
    re_step = int(loss / (beta0 * (loss - beta2)) - beta1 / beta0)
    return re_step

def speed_func_syn(cita0, cita1, cita2, cita3, cita4, cita5, cita6, worker, ps, m, gpu, cpu_ps, cpu_worker) -> float:
    '''
    前后向传播时间：cpu_worker * (cita0 * m + cita1)
    更新时间：cita3 * cpu_ps * worker / ps, cita3是ti M,（在optimus中需要乘以worker/ps，但是aiturbo中不需要）
    ti agg：cita6
    ti over：cita4和cita5（在optimus中是不同的，在aiturbo中都是额外通信时间）
    '''
    cita0 = float(cita0)
    cita1 = float(cita1)
    cita2 = float(cita2)
    cita3 = float(cita3)
    cita4 = float(cita4)
    cita5 = float(cita5)
    cita6 = float(cita6)
    worker = float(worker)
    ps = float(ps)
    m = float(m)
    gpu = float(gpu)
    cpu_ps = float(cpu_ps)
    cpu_worker = float(cpu_worker)
    # speed = 1 / ((cpu_worker * (cita0 * m + cita1)) + cita2 * worker / ps + cita3 * cpu_ps * worker / ps + cita4 * worker + cita5 * ps + cita6 * gpu)
    speed = 1 / ((cpu_worker * (cita0 * m + cita1)) + cita2 * worker / ps + cita3 * worker / ps + cita4 * worker + cita5 * ps + cita6 * gpu)
    return speed

def speed_func_syn_optimus(cita0, cita1, cita2, cita3, cita4, cita5, cita6, worker, ps, m, gpu, cpu_ps, cpu_worker) -> float:
    cita0 = float(cita0)
    cita1 = float(cita1)
    cita2 = float(cita2)
    cita3 = float(cita3)
    cita4 = float(cita4)
    cita5 = float(cita5)
    cita6 = float(cita6)
    worker = float(worker)
    ps = float(ps)
    m = float(m)

    cita22 = cita2 + cita3
    speed = 1/ ((cita0 * m + cita1) + cita22 * worker / ps + cita4 * worker + cita5 * ps)
    return speed

def remain_step(job) -> float:
    current_step = run_program.get_now_step(job.id)
    return int(job.total_steps) - int(current_step)

def calu_remain_time(job) -> None:
    '''
    calculate remaining steps aiturbo
    '''
    remain_time = remain_step(job) / resource_model.speed_func(job)
    return remain_time

def calu_remain_time_optimus(job) -> None:
    '''
    calculate remaining steps optimus
    '''
    remain_time = remain_step(job) / resource_model.speed_func_optimus(job)
    return remain_time

def calu_remain_time2(job) -> None:
    '''
    calculate remaining steps
    '''
    current_step = run_program.get_now_step(job.id)
    remain_time= float(current_step) / resource_model.speed_func(job)
    return remain_time