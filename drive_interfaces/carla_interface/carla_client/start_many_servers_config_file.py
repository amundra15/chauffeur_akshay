
import argparse

parser = argparse.ArgumentParser(description='Run multiple servers on multiple GPUs')
parser.add_argument('--num_gpus', metavar='NUM_GPUS', type=int, default=1, help='how many GPUs to use')
parser.add_argument('--start_gpu', metavar='START_GPU', type=int, default=0, help='which GPU to start with')
parser.add_argument('--processes_per_gpu', metavar='PROCESSES_PER_GPU', type=int, default=1, help='how many processes per GPU')
parser.add_argument('--cores_per_process', metavar='CORES_PER_PROCESS', type=int, default=1, help='how many CPU cores to use per process')
parser.add_argument('--start_core', metavar='START_CORE', type=int, default=0, help='which CPU core to start with')
parser.add_argument('--start_port', metavar='START_PORT', type=int, default=2000, help='which port to start with')
parser.add_argument('--display_num', metavar='DISPLAY_NUM', type=int, default=0, help='which display to use')
#parser.add_argument('--resolution', metavar='RESOLUTION', type=str, default='160x120', help='image resolution')
parser.add_argument('--config_file', metavar='CONFIG_FILE', type=str, help='a file with a list of servers')
parser.add_argument('--out_file', metavar='OUT_FILE', type=str, default='run_servers_config_file.sh', help='the resulting script to be used to run the servers')
#parser.add_argument('--server_binary', metavar='SERVER_BINARY', type=str, default='../2017_02_17/2017_02_17_Linux.x86_64', help='server binary')
parser.add_argument('--server_version', metavar='SERVER_VERSION', type=str, default='2017_02_17', help='server version (for example, 2017_02_17)')
args = parser.parse_args()

server_binary = '../{version}/{version}_Linux.x86_64'.format(version=args.server_version) 
command_template = 'bash set_ports_in_config_file.sh ' + args.server_version + ' %d\n' + \
                   'DISPLAY=:%d.%d taskset -c %d-%d ' + server_binary + ' &\n' + \
                   'sleep 5\n'

with open(args.out_file, 'w') as f:
    if args.config_file:
        raise Exception('Not implemented')
    else:
        curr_core = args.start_core
        curr_port = args.start_port
        for ngpu in range(args.start_gpu, args.start_gpu + args.num_gpus):
            for nprocess in range(args.processes_per_gpu):
                f.write(command_template % (curr_port, args.display_num, ngpu, curr_core, curr_core + args.cores_per_process-1))
                curr_port += 3
                curr_core += args.cores_per_process



	
	
