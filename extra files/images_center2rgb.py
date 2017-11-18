import h5py
import numpy as np
import os

h5_folder = './'
file_list_vec = []
file_list_vec.append(sorted(os.listdir(h5_folder)))
number_of_files = len(file_list_vec[0])

for h_num in range(number_of_files):
	print 'h_num:', h_num
	file = h5py.File(h5_folder+'data_'+ str(h_num).zfill(5) +'.h5', "r+")

	ini_data = file['images_center'] 
	shape = ini_data.shape
	final_data = file.create_dataset('rgb', shape,dtype=np.uint8,data=ini_data)

	del file["images_center"]
	
	file.close()
