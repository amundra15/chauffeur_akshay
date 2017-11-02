import os
import re
count =0
import h5py
from shutil import copyfile
from shutil import move
def rename_folder(file_list,folder_name,initial_count=0):
	count = initial_count
	for filename in file_list:


		print filename
		if "data" in filename:
			newfilename = folder_name+"/data_"+str(count).zfill(5) + ".h5"

			os.rename(folder_name +'/'+ filename,newfilename )
			count +=1




def join_folders(folder_name_vec,file_list_vec,dest_folder,per_val_files=0.05,use_dirty_data=False):
	if not os.path.exists(dest_folder):
		os.mkdir(dest_folder)
		os.mkdir(dest_folder +  '/SeqTrain')
		os.mkdir(dest_folder +  '/SeqVal')
	count =0
	with open('clean_results','w') as f:
		for file_list in file_list_vec:

			count_int=0
			count_good_files=0
			for filename in file_list:


				if "data" in filename:
					print filename

					newfilename =  str(count)+"_data_"+str(count_int).zfill(5) + ".h5"
					print folder_list[count] +'/'+filename
					print folder_list[count] +'/'+newfilename
					if count_int > len(file_list)*per_val_files: 
						copyfile(folder_list[count] +'/'+filename,dest_folder+'/SeqTrain/'+newfilename)
					else:
						copyfile(folder_list[count] +'/'+filename,dest_folder+'/SeqVal/'+newfilename)
					count_int+=1


			count+=1





	#for filename in final_file_list:
	#	if count > number_val_files:
	#		break
	#	move(dest_folder+'/SeqTrain/'+filename,dest_folder+'/SeqVal/'+filename)
	#		count+=1

	rename_folder(sorted(os.listdir(dest_folder+'/SeqTrain')),dest_folder+'/SeqTrain')
	rename_folder(sorted(os.listdir(dest_folder+'/SeqVal')),dest_folder+'/SeqVal')


	

folder_list =['27_Akshay_4','27_Akshay_5','27_Akshay_6','27_Akshay_7','27_Akshay_8','27_Akshay_9',]
#for name in os.listdir('.'):
#	if name != 'join_folder.py':
#		folder_list.append(name)
	#folder_list.append(name[:-len('ColSideFree')])




print folder_list
file_list_vec = []

for i in range(0,len(folder_list)):

	file_list_vec.append(sorted(os.listdir(folder_list[i])))




join_folders(folder_list,file_list_vec,'ElektraData2')




