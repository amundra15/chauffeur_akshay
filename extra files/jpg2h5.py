import h5py
import numpy as np
import os
#from PIL import Image
import scipy.misc

import cv2
#import matplotlib.pyplot as plt

image_folder = './Images_0/'
file_list_vec = []
file_list_vec.append(sorted(os.listdir(image_folder)))
number_of_images = len(file_list_vec[0])

h5path = './'
image_count = 0

for h_num in range(28):
	print 'h_num:', h_num
	data = h5py.File(h5path+'data_'+ str(h_num).zfill(5) +'.h5', "r+")
	image_data = data['images_center'] 
	new_images = np.empty_like(image_data)
	for i in range(min(200,(number_of_images-image_count))):
		image_path = image_folder + str(file_list_vec[0][image_count])
		image = cv2.imread(image_path)
		image = image[115:375,:,:]
		new_images[i] = scipy.misc.imresize(image,[88,200]) #size2, size1

		image_count = image_count +1
	image_data[...] = new_images
	data.close()


'''images =  np.array(data['images_center'][0]).astype(np.uint8)
print images.shape'''

'''
image_data = data['images_center']       # load the data
print image_data.shape #(200, 88, 200, 3)
'''


'''
print "*******"

image = cv2.imread("1.jpg")
print image.shape
image = image[115:375,:,:]
#print images[i].shape
#print self._image_cut
print image.shape
#print image
image = scipy.misc.imresize(image,[88,200]) #size2, size1
print image.shape #(88, 200, 3)

plt.imshow(image)
plt.show()
'''
#cv2.imshow('image',image)
'''cv2.waitKey(0)

cv2.destroyAllWindows()'''
