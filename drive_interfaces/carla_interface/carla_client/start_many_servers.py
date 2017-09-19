import os
import argparse

parser = argparse.ArgumentParser(description='Run multiple servers on multiple GPUs')
parser.add_argument('--num_gpus', metavar='NUM_GPUS', type=int, default=1, help='how many GPUs to use')
parser.add_argument('--start_gpu', metavar='START_GPU', type=int, default=0, help='which GPU to start with')
parser.add_argument('--processes_per_gpu', metavar='PROCESSES_PER_GPU', type=int, default=1, help='how many processes per GPU')
parser.add_argument('--cores_per_process', metavar='CORES_PER_PROCESS', type=int, default=1, help='how many CPU cores to use per process')
parser.add_argument('--start_core', metavar='START_CORE', type=int, default=0, help='which CPU core to start with')
parser.add_argument('--start_port', metavar='START_PORT', type=int, default=2000, help='which port to start with')
parser.add_argument('--resolution', metavar='RESOLUTION', type=str, default='160x120', help='image resolution')
parser.add_argument('--config_file', metavar='CONFIG_FILE', type=str, default='config_alexey.conf', help='a file with server config')
parser.add_argument('--out_file', metavar='OUT_FILE', type=str, default='run_servers.sh', help='the resulting script to be used to run the servers')
parser.add_argument('--server_version', metavar='SERVER_VERSION', type=str, default='2017_02_20', help='server version (e.g. 2017_02_20)')
args = parser.parse_args()

server_binary = os.path.join('..', args.server_version, args.server_version + '_Linux.x86_64')
command_template = 'DISPLAY=:0.%d taskset -c %d-%d ' + server_binary + ' ' + args.config_file + ' %d %d %d &\n'

with open(args.out_file, 'w') as f:
    curr_core = args.start_core
    curr_port = args.start_port
    for ngpu in range(args.start_gpu, args.start_gpu + args.num_gpus):
        for nprocess in range(args.processes_per_gpu):
            f.write(command_template % (ngpu, curr_core, curr_core + args.cores_per_process-1, curr_port, curr_port+1, curr_port+2))
            curr_port += 3
            curr_core += args.cores_per_process



	
	
