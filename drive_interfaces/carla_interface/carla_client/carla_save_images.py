from __future__ import print_function
from carlau3d import CarlaU3D
from configcarla import configCarla
import argparse
import scipy.misc
import numpy as np
import time
import os

# TODO: later we may consider multiple agents being conected to the server

def print_reward_pack(pack):

	print(pack.speed)
	print(pack.impact)
	print(pack.sidewalk_intersect) 
	print(pack.objective)
	print(pack.player_position)
	print(pack.inertia_x)
	print(pack.inertia_y)
	print(pack.inertia_z)
	print(pack.timestamp)
	print(pack.image_number)
                
def pack_summary(pack):
    return 'timestamp %.3f | img %.3f | player %.3f %.3f | goal %.3f %.3f | speed %.5f | inertia %.8f %.8f %.8f | sidewalk %.3f | impact %.3f' % \
            (pack.timestamp, pack.image_number, pack.player_position[0], pack.player_position[1], pack.objective[0], pack.objective[1], pack.speed, \
             pack.inertia_x, pack.inertia_y, pack.inertia_z, pack.sidewalk_intersect, pack.impact)


def run_n_steps(client, num_steps, restart_freq=None, restart_close_to_goal=None, write_images_to='', verbose=0, gas=1.0, steer=0.0, log_detailed='', log_oneliner=''):
        client.start_new_episode(0,6)
        run_experiments = True
        start_time = time.time()
        prev_fps_time = start_time
        prev_fps_step = 0
        restarts = 0
        ntimestep = 0
        timestamps = []
        steps_corresp_to_images = []
        if log_detailed:
            log_detailed_f = open(log_detailed, 'w')
        for step in range(num_steps):
            pack = client.get_data()
            #print(type(pack.objective), pack.objective)
            if log_detailed:
                log_detailed_f.write(('Step %d: ' % step) + pack_summary(pack) + '\n')
            timestamps.append(pack.timestamp)
            distance_to_goal = np.sqrt((pack.objective[0] - pack.player_position[0])**2 + (pack.objective[1] - pack.player_position[1])**2)
            #if step == 0 or (restart_freq and step and ((step-1) % restart_freq == 0 or step % restart_freq == 0)):
            #    print(' * step', step)
            #    print_reward_pack(pack)
            if len(timestamps) < 2 or pack.timestamp != timestamps[-2]:
                ntimestep += 1
                print(('step %d, timestep %d: ' % (step, ntimestep)) + pack_summary(pack))
                if write_images_to:
                    if ntimestep == 1:
                        images = np.zeros((num_steps,) + pack.image.shape, dtype=np.uint8)
                    images[ntimestep-1] = pack.image
                    steps_corresp_to_images.append(step)

            client.control_agent(gas,steer)
            
            if verbose >= 2 and time.time() - prev_fps_time > 1:
                print("Step", step, "FPS", (step - prev_fps_step) / (time.time() - prev_fps_time))
                prev_fps_time = time.time()
                prev_fps_step = step
            if (restart_freq and step and step % restart_freq == 0) or \
               (restart_close_to_goal and distance_to_goal < restart_close_to_goal):
                restarts += 1
                print('\n *** Restarting %f *** \n' % (restarts,))
                client.start_new_episode(0,6)
                time.sleep(1)
        avg_fps = float(num_steps)/(time.time() - start_time)
        avg_fps_timesteps = float(ntimestep)/(time.time() - start_time)
        if verbose >= 1:
            print(" == Step", num_steps, "nominal FPS", avg_fps, "actual FPS", avg_fps_timesteps)
        if log_oneliner:
            with open(log_oneliner, 'a') as f:
                f.write("    %d steps, nominal FPS %f, actual FPS %f\n" % (num_steps, avg_fps, avg_fps_timesteps))
        if write_images_to:
            print('Writing the images to ' + write_images_to)
            if not os.path.exists(write_images_to):
                os.makedirs(write_images_to)
            for timestep in range(ntimestep-1):
                #print(timestep, ntimestep, len(steps_corresp_to_images))
                #scipy.misc.imsave(os.path.join(write_images_to, '%.6d_%.6d.png' % (timestep, steps_corresp_to_images[timestep])), images[timestep])
                scipy.misc.imsave(os.path.join(write_images_to, '%.6d.png' % timestep), images[timestep])
        with open('timestamps.txt','w') as f:
            for step,timestamp in enumerate(timestamps):
                f.write('%d %f\n' % (step,timestamp))
        return avg_fps, avg_fps_timesteps

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run multiple servers on multiple GPUs')
    parser.add_argument('host', metavar='HOST', type=str, help='host to connect to')
    parser.add_argument('port', metavar='PORT', type=int, help='port to connect to')
    parser.add_argument('--num_steps', metavar='NUM_STEPS', type=int, default=1000, help='numer of steps to run the simulator')
    parser.add_argument('--write_images_to', metavar='WRITE_IMAGES_TO', type=str, default='', help='where to write the images')
    parser.add_argument('--log_detailed', metavar='LOG_DETAILED', type=str, default='', help='where to write the detailed log')
    parser.add_argument('--log_oneliner', metavar='LOG_ONELINER', type=str, default='', help='where to write a one-liner summary')
    parser.add_argument('--restart_frequency', metavar='RESTART_FREQUENCY', type=int, default=0, help='how often to restart the episode')
    parser.add_argument('--restart_close_to_goal', metavar='RESTART_CLOSE_TO_GOAL', type=int, default=0, help='restart the episode is the agent is so close to the goal')
    parser.add_argument('--gas', metavar='GAS', type=float, default=1.0, help='gas control for the agent')
    parser.add_argument('--steer', metavar='STEER', type=float, default=0.0, help='steer control for the agent')
    args = parser.parse_args()

    config =configCarla()
    config.host = args.host
    config.port = args.port

    # instance a carla universe with the configurations provided inside the config class
    carla =CarlaU3D(config)
    print("STARTED U3D")
    # Conect to both carla servers. Data stream server and agent control server.
    carla.connect()

    print("CONECTED WORLD")

    # This already set the port to conect the agents
    modes,scenes= carla.receive_scene_conf()
    print("Modes", modes)
    print("Scenes", scenes)

    print(" RECEIVED SCENE CONF")

    carla.select_scene_conf(modes[0],scenes[0])

    print("SELECTED SCENE")


    possible_positions = carla.receive_episode_conf()
    print("Possible positions", possible_positions)

    print("RECEIVED POSIBLE POSITIONS")

    carla.connect_agent()
    
    run_n_steps(carla, args.num_steps, restart_freq=args.restart_frequency, restart_close_to_goal=args.restart_close_to_goal, \
                                       write_images_to=args.write_images_to, verbose=2, gas=args.gas, steer=args.steer, \
                                       log_detailed=args.log_detailed, log_oneliner=args.log_oneliner)


	
	
