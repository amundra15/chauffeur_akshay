
from drawing_tools import *
from extra import *
import time
import math
import scipy
clock = pygame.time.Clock()


class  ScreenManager(object):


	def __init__(self):

		pygame.init()
		# Put some general parameterss
		self._render_iter=0
		#self._speed_limit =50.0
	


	# The We are going to enable up to six screens
	#    |0|1|2|
	#	 |3|4|5|
	# take into consideration the resolution when ploting
	# TODO: Resize properly to fit the screen ( MAYBE THIS COULD BE DONE DIRECTLY RESIZING screen and keeping SURFACES)

	def start_screen(self,resolution,number_of_views,scale=1):
		self._number_of_views = number_of_views

		self._resolution = resolution


		self._scale = scale


		if number_of_views == 1:

			size = (resolution[0],resolution[1])
		elif number_of_views == 2:

			size = (resolution[0]*2,resolution[1])
		elif number_of_views == 3:
			size = (resolution[0]*3,resolution[1])
		else:

			size = (resolution[0]*3,resolution[1]*3)


		self._screen = pygame.display.set_mode((size[0]*scale,size[1]*scale), pygame.DOUBLEBUF)


		self._screen.set_alpha(None)

		pygame.display.set_caption("Human/Machine - Driving Software")

		self._camera_surfaces =[]

		for i in range(number_of_views):
			camera_surface = pygame.surface.Surface(resolution,0,24).convert()

			self._camera_surfaces.append(camera_surface)





	def paint_on_screen(self,size,content,color,position,screen_number):

		myfont = pygame.font.SysFont("monospace", size*self._scale)

		position = (position[0]*self._scale,position[1]*self._scale)


		final_position = (position[0] + self._resolution[0]*(self._scale*(screen_number%3)),\
			position[1] + (self._resolution[1]*(self._scale*(screen_number/3))))


		content_to_write = myfont.render(content, 1, color)

		self._screen.blit(content_to_write, final_position) 

	def paint_line_screen(self,size,color,line,screen_number):

		myfont = pygame.font.SysFont("monospace", size*self._scale)

		origin =line[0]
		end = line[1]

		origin = (origin[0]*self._scale,origin[1]*self._scale)


		final_origin = (origin[0] + self._resolution[0]*(self._scale*(screen_number%3)),\
			origin[1] + (self._resolution[1]*(self._scale*(screen_number/3))))



		end = (end[0]*self._scale,end[1]*self._scale)


		final_end = (end[0] + self._resolution[0]*(self._scale*(screen_number%3)),\
			end[1] + (self._resolution[1]*(self._scale*(screen_number/3))))


		pygame.draw.line(self._screen, color,final_origin, final_end, 3)



		pygame.display.update()
		#content_to_write = myfont.render(content, 1, color)

		#self._screen.blit(content_to_write, final_position)


	def set_array(self,array,screen_number):

		position = (0,0)

		if array.shape[0] != self._resolution[1] or array.shape[1] != self._resolution[0]: 

			array = scipy.misc.imresize(array,[self._resolution[1],self._resolution[0]])

		#print array.shape, self._resolution

		final_position = (position[0] + self._resolution[0]*(self._scale*(screen_number%3)),\
			position[1] + (self._resolution[1]*(self._scale*(screen_number/3))))

		pygame.surfarray.blit_array( self._camera_surfaces[screen_number], array.swapaxes(0,1))

		camera_scale = pygame.transform.scale(self._camera_surfaces[screen_number],(self._resolution[0]*self._scale,self._resolution[1]*self._scale))

		self._screen.blit(camera_scale, final_position)


	def plot_image(self,image_data,screen_number=1):

		self.set_array(image_data,screen_number)
		#pygame.surfarray.blit_array(activation_surface, img_act)
		pygame.display.flip()


	def plot3camrc(self,capture_time,sensor_data,\
		action,speed,orientation,\
		screen_number=0):

		start_to_print = time.time()
		steer = action.steer
		steer_noisy = action.steer
		acc =action.gas
		brake = action.brake
		size_x,size_y,size_z = sensor_data.shape

		# Define our fonts

		#print '******in plot3camrc******'
		#draw_path_on(img, 10, -angle_steers*40.0)
		
		draw_path_on(sensor_data, 20, -steer*20.0, (0, 255, 0))

		draw_bar_on(sensor_data,acc,int(1.5*sensor_data.shape[0]/8),(0,255,0))
		draw_bar_on(sensor_data,brake,int(2*sensor_data.shape[0]/8),(255,0,0))


		self.set_array(sensor_data,screen_number)
		#pygame.surfarray.blit_array(activation_surface, img_act)

		#pygame.display.flip()

		'''if direction ==1.:
			text = "WRONG WAY ... Recalculating ..."
		elif direction ==4:
			text = "Right"
		elif direction == 3:
			text = "Left"
		elif direction == 5:
			text = "Straight"
		elif direction == 6:
			text = "6- UTurnLeft"
		elif direction == 7:
			text = "7 - Exit to the Right"
		elif direction == 8:
			text = "8 - Similar to 7"
		elif direction == 9:
			text = "9 - The misterious 9"
		else:
			text = 'Nothing

		direction_color = (255,0,0)
	
		if ((self._render_iter)/10) % 2 != 0 and direction !=2.0:
			direction_color = (0,255,0)

		if direction == 2:
			direction_pos = (0,10)
		else:
			direction_pos = (size_x/2 - 50,size_y/2 - 50)

		self.paint_on_screen(size_x/20,text,direction_color,direction_pos,screen_number)'''

		self.paint_line_screen(size_x/20,(255,0,0),[[size_x/2,100],\
			[size_x/2 +10*orientation[0] ,100 +10*orientation[1]]],screen_number)

	

		#if speed > self._speed_limit:

		#	self.paint_on_screen(size_x/10,'SLOW DOWN',(255,0,0),(size_x/2,100),screen_number)



		self.paint_on_screen(size_x/20,"%.2f" % speed,(0,255,0),(size_x/2,30),screen_number)



		pygame.display.flip()


		self._render_iter +=1


	#speed is giver by carla, calc_speed is given by driver/network
	def plot_driving_interface(self,capture_time,sensor_data,\
		action,action_noisy,recording,drifting_time,will_drift,speed,calc_speed,posx,\
		posy,screen_number=0):

		start_to_print = time.time()
		steer = action.steer
		steer_noisy = action_noisy.steer
		acc =action.gas
		brake = action.brake
		#print len(sensor_data)
		#a = sensor_data.shape
		#print a
		#print len(a)
		no_of_cameras,size_x,size_y,size_z = sensor_data.shape		#returns (1, 300, 400, 3)
		#print sensor_data
		#print '************'
		# Define our fonts


		#draw_path_on(img, 10, -angle_steers*40.0)
		
		draw_path_on(sensor_data[0], 20, -steer_noisy*20.0, (255, 0, 0))
		draw_path_on(sensor_data[0], 20, -steer*20.0, (0, 255, 0))

		draw_bar_on(sensor_data[0],acc,int(1.5*sensor_data.shape[0]/8),(0,255,0))
		draw_bar_on(sensor_data[0],brake,int(2*sensor_data.shape[0]/8),(255,0,0))


		self.set_array(sensor_data[0],screen_number)
		#pygame.surfarray.blit_array(activation_surface, img_act)

		#pygame.display.flip()

		'''if direction ==1.:
			text = "WRONG WAY ... Recalculating ..."
		elif direction ==4:
			text = "Right"
		elif direction == 3:
			text = "Left"
		elif direction == 5:
			text = "Straight"
		elif direction == 6:
			text = "6- UTurnLeft"
		elif direction == 7:
			text = "7 - Exit to the Right"
		elif direction == 8:
			text = "8 - Similar to 7"
		elif direction == 9:
			text = "9 - The misterious 9"
		else:
			text = 'Nothing'

		direction_color = (255,0,0)
	
		if ((self._render_iter)/10) % 2 != 0 and direction !=2.0:
			direction_color = (0,255,0)

		if direction == 2:
			direction_pos = (0,10)
		else:
			direction_pos = (size_x/2 - 50,size_y/2 - 50)

		self.paint_on_screen(size_x/20,text,direction_color,direction_pos,screen_number)'''



		#if speed > self._speed_limit:

		#	self.paint_on_screen(size_x/10,'SLOW DOWN',(255,0,0),(size_x/2,100),screen_number)


		if recording:

			self.paint_on_screen(size_x/20,'REC',(255,0,0),(size_x-250,30),screen_number)


		if math.fabs(steer_noisy - steer) > 0.01:

			self.paint_on_screen(size_x/20,'NOISE',(255,0,0),(size_x/2 - 70,size_y/2 -70),screen_number)


		#### CARLA SPEED PRINTED ON SCREEN HERE ####
		self.paint_on_screen(size_x/20,"Carla speed: %.2f" % speed,(0,255,0),(size_x/2 -30,60),screen_number)

		#### NETWORK SPEED PRINTED ON SCREEN HERE ####
		self.paint_on_screen(size_x/20,"speed from driver/network: %.2f" % calc_speed,(0,255,0),(size_x/2 -30,30),screen_number)


		pygame.display.flip()


		self._render_iter +=1



	def plot_driving_interface_game(self,capture_time,sensor_data,\
		action,action_noisy,direction,recording,drifting_time,will_drift,speed,posx,\
		posy,other_dist,episode,number_completions,dist_goal,screen_number=0):

		start_to_print = time.time()
		steer = action.steer
		steer_noisy = action_noisy.steer
		acc =action.gas
		brake = action.brake
		size_x,size_y,size_z = sensor_data.shape

		# Define our fonts


		#draw_path_on(img, 10, -angle_steers*40.0)
		
		draw_path_on(sensor_data, 20, -steer_noisy*20.0, (255, 0, 0))
		draw_path_on(sensor_data, 20, -steer*20.0, (0, 255, 0))

		draw_bar_on(sensor_data,acc,int(1.5*sensor_data.shape[0]/8),(0,255,0))
		draw_bar_on(sensor_data,brake,int(2*sensor_data.shape[0]/8),(255,0,0))


		self.set_array(sensor_data,screen_number)
		#pygame.surfarray.blit_array(activation_surface, img_act)

		#pygame.display.flip()
		if other_dist == 0:
			text = "STOP"
		elif direction ==1.:
			text = "WRONG WAY ... Recalculating ..."
		elif direction ==4:
			text = "Right"
		elif direction == 3:
			text = "Left"
		elif direction == 5:
			text = "Straight"
		elif direction == 6:
			text = "6- UTurnLeft"
		elif direction == 7:
			text = "7 - Exit to the Right"
		elif direction == 8:
			text = "8 - Similar to 7"
		elif direction == 9:
			text = "9 - The misterious 9"
		else:
			text = 'Nothing'

		direction_color = (255,0,0)
	
		if ((self._render_iter)/10) % 2 != 0 and direction !=2.0:
			direction_color = (0,255,0)

		if direction == 2:
			direction_pos = (0,10)
		else:
			direction_pos = (size_x/2 - 50,size_y/2 - 50)

		self.paint_on_screen(size_x/20,text,direction_color,direction_pos,screen_number)



		if speed > self._speed_limit:

			self.paint_on_screen(size_x/10,'SLOW DOWN',(255,0,0),(size_x/2,100),screen_number)




		if recording:

			self.paint_on_screen(size_x/20,'REC',(255,0,0),(size_x-100,30),screen_number)


		if math.fabs(steer_noisy - steer) > 0.01:

			self.paint_on_screen(size_x/20,'NOISE',(255,0,0),(size_x/2 - 70,size_y/2 -70),screen_number)



		self.paint_on_screen(size_x/20,"%.2f" % speed,(0,255,0),(size_x/2,30),screen_number)


		self.paint_on_screen(size_x/20,"GOAL: %.2f" % dist_goal,(0,255,0),(size_x/2,80),screen_number)


		self.paint_on_screen(size_x/20,"%d/%d" % (number_completions,episode),(0,0,255),(size_x/3,30),screen_number)


		pygame.display.flip()


		self._render_iter +=1

