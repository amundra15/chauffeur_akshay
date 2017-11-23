from numpy.linalg import norm
import matplotlib.pyplot as plt
import copy


class PerformanceTester(object):


	def __init__(self):
		#list of tuples of location,inclination
		#from VirtualElektraData2, first entries of files 2,5,7,10,12,15,17,20...60 (files 0-60 correspnd to one lap in circuit)
		self.checkpoints = [[[299.41556,	-1493.6473], [0.77082264,	-0.6365625,	0.024910014]], \
			[[1086.2275,-2127.1917],[0.820242,	-0.5720079,	0.0031751338]], \
			[[1759.389,	-2332.8557],[0.86239266,	0.50623494,	-0.002261554]], \
			[[1433.2361,	-1447.9193], [-0.8153821,	0.57891476,	0.0031164829]], \
			[[1310.9606,	-793.1035],[0.69780064,	0.71629196,	9.465031E-5]], \
			[[2445.1501,	-675.2262], [0.9969097,	0.078495696,	0.0030796477]], \
			[[3206.1875,	-656.8336],[0.9999557,	0.0088796625,	0.0031235164]], \
			[[3670.5571,	-1251.7913],[-0.8790623,	-0.47670677,	-1.2623332E-4]], \
			[[2965.7146,	-1423.3145],[-0.6894481,	-0.7243223,	-0.0042823516]], \
			[[3661.0168,	-1708.6515], [0.9164787,	0.4000695,	0.003349298]], \
			[[4375.927,	-1449.0364],[0.9556298,	0.29455173,	0.0033060245]], \
			[[5399.214,	-947.0054], [0.804814,	0.5935191,	0.0030871578]], \
			[[6065.681,	-628.008],[0.99842256,	0.05604264,	0.0034151012]], \
			[[7185.687,	-540.9656], [0.7776693,	0.6286638,	-0.0034929942]], \
			[[7106.0596,	25.690779],[-0.9715613,	0.23669566,	-0.0066157775]], \
			[[5972.315,	9.68889], [-0.9999969,	7.4362545E-4,	0.0023726204]], \
			[[5197.5825,	9.94546],[-0.9999945,	-5.454988E-4,	0.0032724084]], \
			[[4062.1975,	9.93446], [-0.999995,	-5.9604336E-4,	0.0031883665]], \
			[[3300.796,	9.916566],[-0.9999949,	-5.6838716E-4,	0.0030541369]], \
			[[2152.0166,	9.924861], [-0.9999951,	-5.0246465E-4,	0.00317728]], \
			[[1390.6162,	9.948008],[-0.99999416,	-4.522775E-4,	0.003337019]], \
			[[246.9734,	-31.691128], [-0.96771574,	-0.25203297,	0.002410648]], \
			[[-290.68918,	-488.79],[-0.30380237,	-0.9527334,	0.0017272234]], \
			[[199.28828,	-1436.1365], [0.7492446,	-0.6622882,	0.002628084]] \
			]	#24 points total

		self.checkpoints_copy = copy.copy(self.checkpoints)

		self.matched_checkpoints = []



	def plot_map(self):
		a = zip(*self.checkpoints_copy)	#* gives all arguments as a single tuple
		'''print a
		print '************'
		print a[0]'''
		b = zip(*a[0])
		#print b
		#plt.ion()

		ax = plt.gca()
		#ax.invert_yaxis()
		ax.invert_xaxis()


		'''x2 = -y1
    	y2 = x1'''

		plt.plot(b[0], b[1])

		#print "here"

		for i in range(len(self.matched_checkpoints)):
			self.plot_point(self.matched_checkpoints[i][0])
		
		plt.show()


	def in_proximity(self,location,inclination):
		#checking for location
		#print 'in prox function'
		location_matched = False
		for i in range(len(self.checkpoints)):
			#print self.checkpoints[i][0]
			#print location
			if (norm(map(float.__sub__, self.checkpoints[i][0], location))) < 100:		#numpy.array((xa ,ya, za))
				location_matched = True
				break

		if location_matched == True:
			#checking for inclination
			if (norm(map(float.__sub__, self.checkpoints[i][1], inclination))) < 100:
				print "CHECKPOINT CLEARED.  Co-ordinates:", self.checkpoints[i][0]
				self.matched_checkpoints.append(self.checkpoints[i])
				del self.checkpoints[i]		#if entirely matched,delete that item from list
				return True

		return False


	def plot_point(self,location):
		plt.plot([location[0]],[location[1]], marker='o', color='r')
		

	def evaluate(self,location,inclination):
		if self.in_proximity(location,inclination):
			#self.plot_point(location)
			return 1
		else:
			return 0



if __name__ == '__main__':

	tester = PerformanceTester()

	score = tester.evaluate([299.41556,	-1493.6473], [0.77082264,	-0.6365625,	0.024910014])
	score = score + tester.evaluate([1086.2275,-2127.1917],[0.820242,	-0.5720079,	0.0031751338])

	print 'score: ',score

	tester.plot_map()


