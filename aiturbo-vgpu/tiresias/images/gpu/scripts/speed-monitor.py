import os
import logging
import time
import subprocess
import sys


logging.basicConfig(level=logging.INFO,	format='%(asctime)s.%(msecs)03d %(module)s %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
ROLE = os.getenv("ROLE")
WORK_DIR = os.getenv("WORK_DIR")
NUM_WORKER = os.getenv("NUM_WORKER")

# read the log file and monitor the training progress
# give log file name
# give record file name
# run the function in a separate thread
def update_speed(logfile, recordfile):
	filesize = 0
	line_number = 0
	
	# logfile = 'training.log'
	# recordfile = 'speed.txt'	# change to the correct path ....../data/mxnet-data/......
	if not os.path.exists(logfile):
		os.system(r"touch {}".format(logfile))

	with open(recordfile, 'w') as fh:
		fh.write('0 0\n')
	logging.info('starting speed monitor to track average training speed ...')

	speed_list = []
	while True:
		time.sleep(5)
		try:
			cursize = os.path.getsize(logfile)
		except OSError as e:
			logging.warning(e)
			continue

		if cursize == filesize:	# no changes in the log file
			continue
		else:
			filesize = cursize
		
		# Epoch[0] Time cost=50.885
		# Epoch[1] Batch [70]	Speed: 1.08 samples/sec	accuracy=0.000000
		logging.debug("real number of lines" + str(subprocess.check_output("cat " + logfile + " | wc -l", shell=True)))
		with open(logfile, 'r') as f:
			for i in range(line_number):
				try:
					f.next()
				except Exception as e:
					logging.error(str(e) + "line_number: " +str(line_number))
			for line in f:
				line_number += 1
				logging.debug("line number: " + str(line_number))
				logging.debug("real number of lines" + str(subprocess.check_output("cat " + logfile + " | wc -l", shell=True)))
				start = line.find('sec:')
				end = line.find('+')	
				if start > -1 and end > -1 and end > start:
					string = line[start:end].split(' ')[1]
					try:
						speed = float(string)
						speed_list.append(speed)
					except ValueError as e:
						logging.warning(e)
						break
		
		if len(speed_list) == 0:
			continue
		
		print(speed_list)
		avg_speed = sum(speed_list)/len(speed_list)
		logging.info('Average Training Speed: ' + str(avg_speed))
		
		stb_speed = 0
		if len(speed_list) <= 5:
			stb_speed = avg_speed
		else:
			pos = int(2*len(speed_list)/3)
			stb_speed = sum(speed_list[pos:])/len(speed_list[pos:])	# only consider the later part

		logging.info('Stable Training Speed: ' + str(stb_speed))
			
		
		with open(recordfile, 'w') as fh:
			fh.write(str(avg_speed) + ' ' + str(stb_speed) + '\n')


def get_step(logfile, recordfile):
	'''
	get the step the job is currently running
	'''
	if not os.path.exists(logfile):
		os.system(r"touch {}".format(logfile))
		os.system("chmod 777 {}".format(logfile))

	if not os.path.exists(recordfile):
		os.system(r"touch {}".format(recordfile))
		os.system("chmod 777 {}".format(recordfile))

	while True:
		time.sleep(5)

		line = __get_last_line(logfile).split(" ")
		if line[0].isdigit():
			with open(recordfile, 'a') as f:
				f.write(int(line[0]) * int(NUM_WORKER))
			

			
def __get_last_line(self, filename):
    '''
    get last line of a file
    :param filename: file name
    :return: last line or None for empty file
    '''
    try:
        filesize = os.path.getsize(filename)
        if filesize == 0:
            return None
        else:
            with open(filename, 'rb') as fp: # to use seek from end, must use mode 'rb'
                offset = -8                 # initialize offset
                while -offset < filesize:   # offset cannot exceed file size
                    fp.seek(offset, 2)      # read # offset chars from eof(represent by number '2')
                    lines = fp.readlines()  # read from fp to eof
                    if len(lines) >= 2:     # if contains at least 2 lines
                        return lines[-1]    # then last line is totally included
                    else:
                        offset *= 2         # enlarge offset
                fp.seek(0)
                lines = fp.readlines()
                return lines[-1]
    except FileNotFoundError:
        print(filename + ' not found!')
        return None

def main():
	# logfile = '/data/k8s-workdir/measurement/1-measurement-imagenet-worker-0/1.txt'
	# recordfile = '/home/tank/maozz/speed.txt'
	logfile = WORK_DIR + 'training.txt'
	recordfile =  WORK_DIR + 'speed.txt'
	if ROLE == 'worker':
		get_step(logfile, recordfile)
		# update_speed(logfile, recordfile)
	
	
	
if __name__ == '__main__':
	if len(sys.argv) != 1:
		print("Description: monitor training progress in k8s cluster")
		print("Usage: python update_progress.py")
		sys.exit(1)
	main()