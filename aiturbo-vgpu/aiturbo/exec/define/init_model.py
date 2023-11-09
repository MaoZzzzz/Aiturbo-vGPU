from resources_define import Model
import sys

models = []


def read_models_ps_para(path) -> None:
    flag = 0
    for line in open(path):
        line_temp = line.split("\t")
        cpu_ps_para = []
        for i in range(len(line_temp) - 1):
            cpu_ps_para.append(line_temp[i + 1])
        models[flag].cpu_ps_para = cpu_ps_para
        flag += 1


def read_models_worker_para(path) -> None:
    flag = 0
    for line in open(path):
        line_temp = line.split("\t")
        cpu_worker_para = []
        for i in range(len(line_temp) - 1):
            cpu_worker_para.append(line_temp[i + 1])
        models[flag].cpu_worker_para = cpu_worker_para
        flag += 1


def read_models_speed_model_para_gpu(path) -> None:
    flag = 0
    for line in open(path):
        line_temp = line.split("\t")
        speed_model_para_gpu = []
        for i in range(len(line_temp) - 1):
            speed_model_para_gpu.append(line_temp[i + 1])
        models[flag].speed_model_para_gpu = speed_model_para_gpu
        flag += 1


def read_models_speed_model_para_cpu(path) -> None:
    flag = 0
    for line in open(path):
        line_temp = line.split("\t")
        speed_model_para_cpu = []
        for i in range(len(line_temp) - 1):
            speed_model_para_cpu.append(line_temp[i + 1])
        models[flag].speed_model_para_cpu = speed_model_para_cpu
        flag += 1


def read_models_forward(path) -> None:
    flag = 0
    for line in open(path):
        line = line.rstrip()
        line_temp = line.split(" ")
        forward = []
        for i in range(len(line_temp) - 1):
            forward.append(line_temp[i + 1])
        models[flag].forward = forward
        flag += 1


def read_models_backward(path) -> None:
    flag = 0
    for line in open(path):
        line = line.rstrip()
        line_temp = line.split(" ")
        backward = []
        for i in range(len(line_temp) - 1):
            backward.append(line_temp[i + 1])
        models[flag].backward = backward
        flag += 1


def init_models() -> None:
    '''
    initialize model parameters, the data comes from offline measurements
    '''
    for line in open("/home/tank/maozz/test/exec/systemData/cpu_ps.txt"):
        line_temp = line.split("\t")
        model_temp = Model()
        model_temp.model_name = line_temp[0]
        # model_temp.mps_para = mps_para
        models.append(model_temp)

    read_models_ps_para("/home/tank/maozz/test/exec/systemData/cpu_ps.txt")
    read_models_worker_para(
        "/home/tank/maozz/test/exec/systemData/cpu_worker.txt")
    read_models_speed_model_para_gpu(
        "/home/tank/maozz/test/exec/systemData/worker_gpu_speed2.txt")
    read_models_speed_model_para_cpu(
        "/home/tank/maozz/test/exec/systemData/worker_cpu_speed.txt")
    read_models_forward("/home/tank/maozz/test/exec/systemData/forward.txt")
    read_models_backward("/home/tank/maozz/test/exec/systemData/backward.txt")


def main():
    init_models()

    print(models[0].cpu_ps_para)
    # for i in range(len(models)):
    #     print(models[i].model_name + " " + "".join(models[i].forward))
    # # f = open("data.txt", "r")
    # # with open("data1.txt", 'w') as f:
    # #     for i in models:
    # #         f.write(i + '\n')


if __name__ == '__main__':
    main()
