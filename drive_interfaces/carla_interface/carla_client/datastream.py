import sys
is_py2 = sys.version[0] == '2'
if is_py2:
    from Queue import Queue
    from Queue import Empty
    from Queue import Full
else:
    from queue import Queue
    from queue import Full
from threading import Thread
import time
import random
from PIL import Image
from socket_util import *
import io
import sys
import numpy as np



sys.path.append('protoc')


from carla_pack_pb2 import Reward


def threaded(fn):
    def wrapper(*args, **kwargs):
        thread = Thread(target=fn, args=args, kwargs=kwargs)
        thread.setDaemon(True)
        thread.start()

        return thread
    return wrapper


class DataStream(object):

    def __init__(self,image_x=640,image_y=480):
        self._data_buffer = Queue(1)
        self._image_x = image_x
        self._image_y = image_y

        self._socket = 0
        self._running = True



    def _read_images(self,image_bytes_vec,images_lens):


        image_sizes_vec = []

        images = []  # Start with empty images and depths


        for i in range(len(images_lens)/4):   # get each size of the images
            #print len(reward.final_image_sizes[i*4:(i+1)*4])
            image_sizes_vec.append(struct.unpack('<L', images_lens[i*4:(i+1)*4])[0])




        tracked_pos =0 # a tracked position to get the images being iterated on the bytes vector
        #print "LEN ALL IMAGES ", len(reward.final_images)

        for i in range(len(image_sizes_vec)):  # Now we iterate and collect the amount of bites

            image_bytes = image_bytes_vec[tracked_pos:(tracked_pos+image_sizes_vec[i])]
            #print "len geting ", len(reward.final_images[tracked_pos:(tracked_pos+image_sizes_vec[i])])
            #stream = io.BytesIO(image_bytes)
            #image_result = Image.open(stream)
            #print "Len image ", len(image_bytes)
            #
            dt = np.dtype("uint8")
            #dt = dt.newbyteorder('>L')
            new_image =np.frombuffer(image_bytes,dtype=dt)

            images.append(np.reshape(new_image,(self._image_y,self._image_x,3)))
            #images.append(np.array(image_result))
            #print images[0].shape
            tracked_pos += image_sizes_vec[i]
            #print "PARSED IMAGE"
           

        return images


    def receive_data(self):

        depths = []


        capture_time = time.time()
        data  = get_message(self._socket)
        
        reward = Reward()
        reward.ParseFromString(data)
        
        images= self._read_images(reward.images,reward.image_sizes)

        logging.debug("RECEIVED IMAGES of len %d" % len(images))

        final_images =  self._read_images(reward.final_images,reward.final_image_sizes)
        logging.debug("RECEIVED Finals of len %d" % len(final_images))

        semantic_segs =  self._read_images(reward.semantic_segs,reward.semantic_seg_sizes)
        logging.debug("RECEIVED Segs of len %d" % len(semantic_segs))

        depths =  self._read_images(reward.depths,reward.depth_sizes)
        logging.debug("RECEIVED DEPTHS of len %d" % len(depths))

        reward.images =""
        reward.semantic_segs =""
        reward.final_images =""
        reward.depths = ""


        return [reward,images,final_images,semantic_segs,depths]


    def get_the_latest_data(self):

        try:
            data = self._data_buffer.get(timeout=5)

        except Empty:
            print("ERROR: No Data in 50 seconds, disconecting and reconecting from server ")
            self._running = False
            raise Empty

            
        
        else:
            self._data_buffer.task_done()
        finally:
            return data

    def start(self,socket):

        self._socket = socket

        self.run()
        

    def stop(self):
        self._running = False

    # We clean the buffer so that no old data is going to be used
    def clean(self):
        while True:
            try:
                aux=self._data_buffer.get(False)
            except Empty:
               
                return
      

    @threaded
    def run(self):
        try:
            while self._running:
                try:
                    self._data_buffer.put(self.receive_data(),timeout=5)
                except Full:
                    print ("ERROR: Queue Full for more than 50 seconds, disconecting and reconecting from server")
                    self._running = False

        except RuntimeError:
            print("Unexpected RuntimeError")
            self._running = False
        finally:
            logging.debug("We Are finishing the datastream thread ")

