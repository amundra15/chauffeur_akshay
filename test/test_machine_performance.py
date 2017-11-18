from numpy.linalg import norm
import matplotlib.pyplot as plt

class PerformanceTester(object):


	def __init__(self):
		#list of tuples of location,inclination
		#from VirtualElektraData2, first entries of files 2,5,10,15,20...60
		self.waypoints = [[[299.41556,	-1493.6473], [0.77082264,	-0.6365625,	0.024910014]], \
			[[1086.2275,-2127.1917],[0.820242,	-0.5720079,	0.0031751338]], \
			[[1433.2361,	-1447.9193], [-0.8153821,	0.57891476,	0.0031164829]], \
			[[2445.1501,	-675.2262], [0.9969097,	0.078495696,	0.0030796477]], \
			[[3670.5571,	-1251.7913],[-0.8790623,	-0.47670677,	-1.2623332E-4]], \
			[[3661.0168,	-1708.6515], [0.9164787,	0.4000695,	0.003349298]], \
			[[5399.214,	-947.0054], [0.804814,	0.5935191,	0.0030871578]], \
			[[7185.687,	-540.9656], [0.7776693,	0.6286638,	-0.0034929942]], \
			[[5972.315,	9.68889], [-0.9999969,	7.4362545E-4,	0.0023726204]], \
			[[4062.1975,	9.93446], [-0.999995,	-5.9604336E-4,	0.0031883665]], \
			[[2152.0166,	9.924861], [-0.9999951,	-5.0246465E-4,	0.00317728]], \
			[[246.9734,	-31.691128], [-0.96771574,	-0.25203297,	0.002410648]], \
			[[199.28828,	-1436.1365], [0.7492446,	-0.6622882,	0.002628084]] \
			]



	def plot_map(self):
		a = zip(*self.waypoints)	#* gives all arguments as a single tuple
		'''print a
		print '************'
		print a[0]'''
		b = zip(*a[0])
		#print b
		plt.ion()

		ax = plt.gca()
		#ax.invert_yaxis()
		ax.invert_xaxis()

		plt.plot(b[0], b[1])
		plt.show()



	def in_proximity(self,location,inclination):
		#checking for location
		location_matched = False
		for i in range(len(self.waypoints)):
			#print self.waypoints[i][0]
			#print location
			if (norm(map(float.__sub__, self.waypoints[i][0], location))) < 10:		#numpy.array((xa ,ya, za))
				location_matched = True
				break

		if location_matched == True:
			#checking for inclination
			if (norm(map(float.__sub__, self.waypoints[i][1], inclination))) < 10:
				del self.waypoints[i]		#if entirely matched,delete that item from list
				return True

		return False


	def plot_point(self,location):
		plt.plot([location[0]],[location[1]],marker='o', color='r')

		while True:
			plt.pause(0.05)



	def evaluate(self,location,inclination):
		if self.in_proximity(location,inclination):
			self.plot_point(location)
			return 1
		else:
			return 0












