import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa

#ia.seed(354)

class ImageAugmenter(object):


    def __init__(self,labels_to_augment,augment_amount):
        self._labels_to_augment = labels_to_augment
        self._augment_amount = augment_amount


    def augmenter_function(self,images,labels):

        high = lambda aug: iaa.Sometimes(0.9, aug)
        medium = lambda aug: iaa.Sometimes(0.6, aug)
        low = lambda aug: iaa.Sometimes(0.15, aug)

        if(self._augment_amount == 3):      #max augmentation
            road_aug = iaa.Sequential([
                iaa.Multiply((0.5, 1.25)),        
                #texture
                iaa.SomeOf(1 , [
                #iaa.AdditiveGaussianNoise(scale=(0, 0.01*255)),
                iaa.AddElementwise((-20, 20)),
                medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))
            ])])

            building_aug = iaa.Sequential([
                iaa.Multiply((0.5, 1.5), per_channel=0.8),
                #texture
                #iaa.SomeOf(1, [
                #high(iaa.AdditiveGaussianNoise(scale=(0, 0.03*255))),
                #medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                #medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))])
            ])

            grass_aug = iaa.Sequential([
                iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
                (iaa.WithChannels(0, iaa.Add((50, -50)))),
                iaa.WithChannels(2, iaa.Add((-30,30))),
                iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
                #texture
                iaa.SomeOf(2, [
                medium(iaa.AdditiveGaussianNoise(scale=(0, 0.06*255))),
                medium(iaa.AddElementwise((-25, 25))),
                medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))
                #low(iaa.Superpixels(p_replace=1, n_segments=(126, 128)))
            ])])

            sky_aug = iaa.Sequential([
                iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
                iaa.WithChannels(0, iaa.Add((-20, 20))),
                iaa.WithChannels(1, iaa.Add((0, 30))),
                iaa.WithChannels(2, iaa.Add((-10,0))),
                iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
                #medium(iaa.WithChannels(2, iaa.Add((-40, 40)))),
                #texture
                #iaa.SomeOf(1, [
                #medium(iaa.AddElementwise((-5, 5))),
                #medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.6, 1.4)))
                #low(iaa.Superpixels(p_replace=1, n_segments=(126, 144)))])
            ])


        elif(self._augment_amount == 2):         #mid augmentation
            road_aug = iaa.Sequential([
                high(iaa.Multiply((0.75, 1.15))),
                #texture
                iaa.SomeOf(1 , [
                #iaa.AdditiveGaussianNoise(scale=(0, 0.01*255)),
                iaa.AddElementwise((-8, 8)),
                medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))
            ])])

            building_aug = iaa.Sequential([
                iaa.Multiply((0.5, 1.5), per_channel=0.8),
                #texture
                #iaa.SomeOf(1, [
                #high(iaa.AdditiveGaussianNoise(scale=(0, 0.03*255))),
                #medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                #medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))])
            ])

            grass_aug = iaa.Sequential([
                iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
                (iaa.WithChannels(0, iaa.Add((50, -50)))),
                iaa.WithChannels(2, iaa.Add((-30,30))),
                iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
                #texture
                iaa.SomeOf(1, [
                medium(iaa.AdditiveGaussianNoise(scale=(0, 0.04*255))),
                medium(iaa.AddElementwise((-11, 11))),
                medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                medium(iaa.Emboss(alpha=(0.0, 0.75), strength=(0.5, 1.5)))
                #low(iaa.Superpixels(p_replace=1, n_segments=(126, 128)))
            ])])

            sky_aug = iaa.Sequential([
                iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
                iaa.WithChannels(0, iaa.Add((-30, 30))),
                iaa.WithChannels(1, iaa.Add((0, 30))),
                iaa.WithChannels(2, iaa.Add((-10,0))),
                iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
                #medium(iaa.WithChannels(2, iaa.Add((-40, 40)))),
                #texture
                #iaa.SomeOf(1, [
                #medium(iaa.AddElementwise((-5, 5))),
                #medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.6, 1.4)))
                #low(iaa.Superpixels(p_replace=1, n_segments=(126, 144)))])
            ])


        elif(self._augment_amount == 1):         #min augmentation
            road_aug = iaa.Sequential([
                high(iaa.Multiply((0.9, 1.05))),
                #texture
                iaa.SomeOf(1 , [
                #iaa.AdditiveGaussianNoise(scale=(0, 0.01*255)),
                iaa.AddElementwise((-3, 3)),
                medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.8, 1.2)))
            ])])

            building_aug = iaa.Sequential([
                iaa.Multiply((0.5, 1.5), per_channel=0.8),
                #texture
                #iaa.SomeOf(1, [
                #high(iaa.AdditiveGaussianNoise(scale=(0, 0.03*255))),
                #medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
                #medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))])
            ])

            grass_aug = iaa.Sequential([
                iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
                iaa.WithChannels(0, iaa.Add((50, -50))),
                iaa.WithChannels(2, iaa.Add((-30,30))),
                iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
                #texture
                iaa.SomeOf(1, [
                medium(iaa.AdditiveGaussianNoise(scale=(0, 0.02*255))),
                medium(iaa.AddElementwise((-10, 10))),
                medium(iaa.Sharpen(alpha=(0.0, 0.5), lightness=1)),
                medium(iaa.Emboss(alpha=(0.0, 0.5), strength=(0.5, 1.5)))
                #low(iaa.Superpixels(p_replace=1, n_segments=(126, 128)))
            ])])

            sky_aug = iaa.Sequential([
                iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
                iaa.WithChannels(0, iaa.Add((-20, 20))),
                iaa.WithChannels(1, iaa.Add((0, 10))),
                iaa.WithChannels(2, iaa.Add((-10,0))),
                iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
                medium(iaa.WithChannels(2, iaa.Add((-40, 40)))),
                #texture
                #iaa.SomeOf(1, [
                #medium(iaa.AddElementwise((-5, 5))),
                #medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.6, 1.4)))
                #low(iaa.Superpixels(p_replace=1, n_segments=(126, 144)))])
            ])


        '''fence = np.zeros_like(images)
        cond = labels == 2
        b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
        fence[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]'''


        if self._labels_to_augment["road"] == True:
            road = np.zeros_like(images)
            cond = labels == 8
            b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
            road[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

            new_road = sky_aug.augment_images(road)

            images = images + new_road - road


        if self._labels_to_augment["buildings"] == True:
            buildings = np.zeros_like(images)
            cond = labels == 1
            b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
            buildings[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

            new_buildings = sky_aug.augment_images(buildings)

            images = images + new_buildings - buildings


        if self._labels_to_augment["grass"] == True:
            grass = np.zeros_like(images)
            cond = labels == 9
            b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
            grass[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

            new_grass = sky_aug.augment_images(grass)

            images = images + new_grass - grass


        if self._labels_to_augment["sky_n_zebra"] == True:

            sky_n_zebra = np.zeros_like(images)
            cond = labels == 0
            b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
            sky_n_zebra[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

            new_sky_n_zebra = sky_aug.augment_images(sky_n_zebra)

            images = images + new_sky_n_zebra - sky_n_zebra

        #final = road + buildings + grass + sky_n_zebra + fence
        #comp = np.hstack((initial,final))

        #initial = buildings+grass+fence+road+sky_n_zebra

        return images



if __name__ == '__main__':

    import h5py
    import cv2
    import numpy as np


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

    augment_labels = {"road": True, "buildings": True, "grass": True , "sky_n_zebra": True }
    #augment_labels = {"road": False, "buildings": False, "grass": False, "sky_n_zebra": False }

    #print augment_labels["road"]
    augmenter_object = ImageAugmenter(augment_labels,1)
    result = augmenter_object.augmenter_function(final_rgb_image,final_seg_image)  #augmentation based on segmentation labels

    image = result[167]
    cv2.imshow('image', image )
    cv2.waitKey(0)
    cv2.destroyAllWindows()