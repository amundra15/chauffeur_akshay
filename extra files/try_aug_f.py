import sys
sys.path.append('train')

import h5py
import cv2
import numpy as np

from image_augmenter import *

filename = 'data_00020.h5'
f = h5py.File(filename, 'r')

seg_image = []
rgb_image = []

segmented_data = f["labels"]
rgb_data = f["rgb"]
#print len(segmented_data)
#print len(rgb_data)
seg_image.append(segmented_data)
rgb_image.append(rgb_data)
final_seg_image = np.array(seg_image[0])
final_rgb_image = np.array(rgb_image[0])

#augment_labels = {"road": False, "buildings": False, "grass": False, "sky_n_zebra": False }
augment_labels = {"road": True, "buildings": True, "grass": True, "sky_n_zebra": True }
#print augment_labels

#print augment_labels["road"]
augmenter_object = ImageAugmenter(augment_labels)
result = augmenter_object.augmenter_function(final_rgb_image,final_seg_image)  #augmentation based on segmentation labels

image = result[13]
cv2.imshow('image', image )
cv2.waitKey(0)
cv2.destroyAllWindows()