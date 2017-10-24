#import h5py
#import cv2
import numpy as np
import imgaug as ia
from imgaug import augmenters as iaa


class ImageAugmenter(object):


    def __init__(self,augment_labels):
        self._augment_lables = augment_labels


    def augmenter_function(self,images,labels):

        high = lambda aug: iaa.Sometimes(0.9, aug)
        medium = lambda aug: iaa.Sometimes(0.6, aug)
        low = lambda aug: iaa.Sometimes(0.15, aug)


        road_aug = iaa.Sequential([
            high(iaa.Multiply((0.25, 1.25))),
            #texture
            iaa.SomeOf(1 , [
            #iaa.AdditiveGaussianNoise(scale=(0, 0.01*255)),
            high(iaa.AddElementwise((-10, 10))),
            medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
            medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))
        ])])

        building_aug = iaa.Sequential([
            high(iaa.Multiply((0.5, 1.5), per_channel=0.8)),
            #texture
            iaa.SomeOf(1, [
            high(iaa.AdditiveGaussianNoise(scale=(0, 0.03*255))),
            medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
            medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))
        ])])

        grass_aug = iaa.Sequential([
            iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
            high(iaa.WithChannels(0, iaa.Add((50, -50)))),
            high(iaa.WithChannels(2, iaa.Add((-30,30)))),
            iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
            #texture
            iaa.SomeOf(2, [
            medium(iaa.AdditiveGaussianNoise(scale=(0, 0.05*255))),
            medium(iaa.AddElementwise((-50, 50))),
            medium(iaa.Sharpen(alpha=(0.0, 1.0), lightness=1)),
            medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.5, 1.5)))
            #low(iaa.Superpixels(p_replace=1, n_segments=(126, 128)))
        ])])

        sky_aug = iaa.Sequential([
            iaa.ChangeColorspace(from_colorspace="RGB", to_colorspace="HSV"),
            high(iaa.WithChannels(0, iaa.Add((-20, 20)))),
            high(iaa.WithChannels(1, iaa.Add((0, 30)))),
            high(iaa.WithChannels(2, iaa.Add((-10,0)))),
            iaa.ChangeColorspace(from_colorspace="HSV", to_colorspace="RGB"),
            medium(iaa.WithChannels(2, iaa.Add((-40, 40)))),
            #texture
            iaa.SomeOf(1, [
            medium(iaa.AddElementwise((-5, 5))),
            medium(iaa.Emboss(alpha=(0.0, 1.0), strength=(0.6, 1.4)))
            #low(iaa.Superpixels(p_replace=1, n_segments=(126, 144)))
        ])])


        grass = np.zeros_like(images)
        cond = labels == 9
        #print cond.shape
        b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
        #print b.shape 
        grass[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

        fence = np.zeros_like(images)
        cond = labels == 2
        b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
        fence[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

        buildings = np.zeros_like(images)
        cond = labels == 1
        b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
        buildings[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

        road = np.zeros_like(images)
        cond = labels == 8 
        b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
        road[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]

        sky_n_zebra = np.zeros_like(images)
        cond = labels == 0
        b = np.repeat(cond[:, :, :, np.newaxis], 3, axis=3)
        sky_n_zebra[b[:,:,:,:,0]] = images[b[:,:,:,:,0]]


        if self._augment_lables["road"] == True:
            road = road_aug.augment_images(road)

        if self._augment_lables["buildings"] == True:
            buildings = building_aug.augment_images(buildings)

        if self._augment_lables["grass"] == True:
            grass = grass_aug.augment_images(grass)

        if self._augment_lables["sky_n_zebra"] == True:
            sky_n_zebra = sky_aug.augment_images(sky_n_zebra)

        final = road + buildings + grass + sky_n_zebra + fence
        #comp = np.hstack((initial,final))

        #initial = buildings+grass+fence+road+sky_n_zebra

        return final

