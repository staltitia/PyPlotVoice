import threading
import numpy
from FindPeaks import *

import matplotlib.pyplot as plt

writeLock = threading.Lock()
outArr = numpy.array([])
#drawLock = threading.Lock()

def fundFreqBlocksThreaded ( inArray, samplingRate, win, toConv, concurrent=10 ):
	#inArray is a numpy array
	#samplingRate is an int
	#win is window length in seconds
	#toConv is the smoothening colvolution array
	#concurrent is the number of concurrent threads allowed

	#returns fundamental frequencies in numpy array

	import time
	
	window = win*samplingRate
	splitArr = numpy.arange( window, inArray.size, window )	
	toProcess = numpy.split( inArray, splitArr )
	
	global outArr
	outArr = numpy.zeros( len(toProcess) )

	for i in range( len(toProcess) ):
		if threading.active_count() > concurrent:
			time.sleep(0.1)
		else:		
			if i < 1:
				left = numpy.zeros( len(toProcess[i])/2 )
			else:
				left = toProcess[i-1][len(toProcess[i])/2:]
			if i+1 >= len(toProcess):
				right = numpy.zeros( len(toProcess[i])/2 )
			else:
				right = toProcess[i+1][:len(toProcess[i])/2]
			
			inArr = numpy.concatenate((left, toProcess[i], right))	
			myThrd = AMDFThread( inArr, i, toConv )
			myThrd.start()
		print "%d/%d made!\033[A" % (i+1, len(toProcess) )
	
	while threading.active_count() > 1:
		print "%d/%d left!\033[A" % (threading.active_count()-1, len(toProcess) )
		time.sleep(0.1)	#waits for threads to be done

	return numpy.array(outArr)

class AMDFThread( threading.Thread ):
	def __init__( self, inArray, outInd, toConv):
		threading.Thread.__init__(self)
		self.inArray = inArray
		self.outInd = outInd
		self.toConv = toConv

	def run(self):
		#inArray is a numpy array, samplingRate is an int
				
		toRoll = self.inArray.copy()
		curve = [] #array of scalars

		for i in range( len(self.inArray) ):
			rolled = numpy.roll( toRoll, -i )
			holder = abs( numpy.add( toRoll, (-1)*rolled ) )
			truncated = holder[:toRoll.size-i]
			curve.append( numpy.mean(truncated) )

		curve = numpy.array( curve )
		curve = numpy.convolve( curve, self.toConv, mode='same' ) 
		
		#now we have the AMDF results, we extract f0

		maxPeaks = findPeaks( curve, 'max' )
		
		truncIndHead = 0
		truncIndTail = len(curve)
		if len(maxPeaks) > 1:
			truncIndHead = maxPeaks[0]
			truncIndTail = maxPeaks[-1]
		trunc = curve[truncIndHead:truncIndTail]
		f0 = numpy.argmin( trunc )

		toWrite = ( f0+truncIndHead )
		'''
		global drawLock
		drawLock.acquire()
		plt.clf()
		plt.plot(curve)
		plt.savefig("AMDFOUT%d.png"%self.outInd)
		drawLock.release()
		'''
		global writeLock, outArr
		writeLock.acquire()
		outArr[self.outInd] = toWrite
		writeLock.release()
