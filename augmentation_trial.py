import h5py
import cv2
import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa

filename = 'data_00020.h5'
f = h5py.File(filename, 'r')

seg_image = []
rgb_image = []

segmented_data = f["labels"]
rgb_data = f["rgb"]
#print len(segmented_data)
#print len(rgb_data)
seg_image.append(segmented_data[0])
rgb_image.append(rgb_data[0])
final_seg_image = np.array(seg_image[0])
final_rgb_image = np.array(rgb_image[0])

print final_rgb_image.shape


grass = np.empty_like(final_rgb_image)
cond = final_seg_image == 9
b = np.repeat(cond[:, :, np.newaxis], 3, axis=2) 
grass[b[:,:,:,0]] = final_rgb_image[b[:,:,:,0]]



fence = np.empty_like(final_rgb_image)
cond = final_seg_image == 2
b = np.repeat(cond[:, :, np.newaxis], 3, axis=2) 
fence[b[:,:,:,0]] = final_rgb_image[b[:,:,:,0]]

buildings = np.empty_like(final_rgb_image)
cond = final_seg_image == 1
b = np.repeat(cond[:, :, np.newaxis], 3, axis=2) 
buildings[b[:,:,:,0]] = final_rgb_image[b[:,:,:,0]]

road = np.empty_like(final_rgb_image)
sky_n_zebra = np.empty_like(final_rgb_image)
cond = final_seg_image == 0 
b = np.repeat(cond[:, :, np.newaxis], 3, axis=2) 
sky_n_zebra[b[:,:,:,0]] = final_rgb_image[b[:,:,:,0]]


'''cond2 = final_seg_image == 8 #8
b = np.repeat(cond2[:, :, np.newaxis], 3, axis=2) 
road[b[:,:,:,0]] = final_rgb_image[b[:,:,:,0]]
'''

ia.seed(85)

road_aug = iaa.Multiply((0.25, 1.25))

building_aug = iaa.Multiply((0.5, 1.5), per_channel=0.8)


grass_aug = iaa.Sequential([
    iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
    iaa.WithChannels(0, iaa.Add((50, -50))),
    iaa.WithChannels(2, iaa.Add((-30,30))),
    iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB")
])

sky_aug = iaa.Sequential([
    iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
    iaa.WithChannels(0, iaa.Add((-20, 20))),
    iaa.WithChannels(1, iaa.Add((0, 30))),
    iaa.WithChannels(2, iaa.Add((-10,0))),
    iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
    iaa.WithChannels(2, iaa.Add((-50, 80))),
])

#sky_aug = iaa.ContrastNormalization((0.5, 1.5), per_channel=0.5)

'''
aug_road = road_aug.augment_image(road)
tworoad = np.hstack((road,aug_road))

aug_building = building_aug.augment_image(buildings)
twobuilding = np.hstack((buildings,aug_building))

aug_grass = grass_aug.augment_image(grass)
twograss = np.hstack((grass,aug_grass))'''

'''aug_sky = sky_aug.augment_image(sky_n_zebra)
twosky = np.hstack((sky_n_zebra,aug_sky))

final = aug_road + aug_building + aug_grass + aug_sky+ fence
comp = np.hstack((final_rgb_image,final))'''

#initial = buildings+grass+fence+road

cv2.imshow('image', buildings )
#cv2.imshow('image',final_seg_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
