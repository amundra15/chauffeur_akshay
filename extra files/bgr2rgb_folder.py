import cv2
import os

input_path = './Images_0/'
save_path = './Images_1/'

if not os.path.exists(save_path):
	os.mkdir(save_path)

file_list_vec = []
file_list_vec.append(sorted(os.listdir(input_path)))
#print len(file_list_vec[0])
#print file_list_vec
for image_name in file_list_vec[0]:
	image_path = input_path + str(image_name)
	print image_path
	img = cv2.imread(image_path)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
	#cv2.imshow('image',img)
	#cv2.waitKey(0)
	output_path = save_path + str(image_name)
	cv2.imwrite(output_path,img)

#cv2.destroyAllWindows()
