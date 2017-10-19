import h5py
import cv2
import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa

filename = 'data_00020.h5'
f = h5py.File(filename, 'r')

seg_image = []
rgb_image = []
# List all groups
#print("Keys: %s" % f.keys())
#print f.name

'''for name in f:
	print name'''
#a_group_key = f.keys()[0]

# Get the data
segmented_data = f["labels"]
rgb_data = f["rgb"]
print len(segmented_data)
print len(rgb_data)
seg_image.append(segmented_data[0])
rgb_image.append(rgb_data[0])
final_seg_image = np.array(seg_image[0])
final_rgb_image = np.array(rgb_image[0])
#print final_seg_image.shape
#print final_rgb_image.shape

#road = np.empty_like (final_rgb_image) 
'''for row in range(len(final_seg_image)):
  for col in range(len(final_seg_image[0])):
    if final_seg_image[row][col] == 8:
      road[row,col,:] = final_rgb_image[row,col,:]'''


road = np.empty_like (final_seg_image) 
'''road[final_seg_image > 8,final_seg_image > 8] = final_rgb_image '''

'''cond = final_seg_image == 8
print cond.shape
b = np.repeat(cond[:, :, np.newaxis], 3, axis=2)
print b.shape

road[b] = final_rgb_image[b]'''

road = (final_seg_image == 9)
#road[b] = final_rgb_image[b]
masked_data = cv2.bitwise_and(final_rgb_image, final_rgb_image, mask=road)



buildings = np.empty_like (final_rgb_image) 
for row in range(len(final_seg_image)):
  for col in range(len(final_seg_image[0])):
    if final_seg_image[row][col] == 1:
      buildings[row,col,:] = final_rgb_image[row,col,:]

fence = np.empty_like (final_rgb_image) 
for row in range(len(final_seg_image)):
  for col in range(len(final_seg_image[0])):
    if final_seg_image[row][col] == 2:
      fence[row,col,:] = final_rgb_image[row,col,:]

grass = np.empty_like (final_rgb_image) 
for row in range(len(final_seg_image)):
  for col in range(len(final_seg_image[0])):
    if final_seg_image[row][col] == 9:
      grass[row,col,:] = final_rgb_image[row,col,:]

sky_n_zebra = np.empty_like (final_rgb_image) 
for row in range(len(final_seg_image)):
  for col in range(len(final_seg_image[0])):
    if final_seg_image[row][col] == 0:
      sky_n_zebra[row,col,:] = final_rgb_image[row,col,:]

ia.seed(885)

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


aug_road = road_aug.augment_image(road)
tworoad = np.hstack((road,aug_road))

aug_building = building_aug.augment_image(buildings)
twobuilding = np.hstack((buildings,aug_building))

aug_grass = grass_aug.augment_image(grass)
twograss = np.hstack((grass,aug_grass))

aug_sky = sky_aug.augment_image(sky_n_zebra)
twosky = np.hstack((sky_n_zebra,aug_sky))

final = aug_road + aug_building + aug_grass + aug_sky+ fence
comp = np.hstack((final_rgb_image,final))



cv2.imshow('image',road )
#cv2.imshow('image',final_seg_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
