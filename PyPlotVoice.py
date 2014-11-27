#Author: Daniel GHK Chong
#Date: 20 Nov 2014
#File: PyPlotVoice.py

#Python Version: 2.7.6
#Dependencies: scipy, numpy, matplotlib

#!/usr/bin/python
from scipy.io import wavfile as wavfile
from scipy import signal
import sys #to get command line arguments
import numpy
import matplotlib.pyplot as plt

WINDOW_WIDTH = 1 #in seconds
SIL_THRESH = 0.5 #in seconds
	
def findPeaks ( inArray, mode="both" ): 
	#max for max peaks, min for min peaks, both for both
	toRet = []
	ascending = False
	if (inArray[1] > inArray[0]):
		ascending = True
	for i in range(len(inArray) - 1):
		if ( ascending and inArray[i+1] < inArray[i] ):
			if not (mode == "min"):
				toRet.append(i)
			ascending = False
		if ( not ascending and inArray[i+1] > inArray[i]):
			if not (mode == "max"):
				toRet.append(i)
			ascending = True
	return numpy.asarray(toRet)

def windowRMS(a, window_size):
  a2 = numpy.power(a,2)
  window = numpy.ones(window_size)/float(window_size)
  return numpy.sqrt(numpy.convolve(a2, window, 'valid'))

def main():
	filename = ''

	if ( len(sys.argv) >= 2 ):
		filename = sys.argv[1]
	else:
		print("Please include a file as a command line argument")
		return
	try:
		 [ samplingRate, values ] =  wavfile.read(filename)
	except IOError:
		print( filename + " does not exist. Please try again.")
		return

	#getting this far means that the file is good, and has been opened
	
	#print "IO DONE"
	
	#first, we split the data into its four sections

	arrListY = numpy.split(values, [ 60*2*samplingRate, 60*10*samplingRate, 60*12*samplingRate ] )
	
	xaxis = numpy.arange( 0, float(len(values)) / samplingRate, 1.0 / samplingRate )

	arrListX = numpy.split(xaxis, [ 60*2*samplingRate, 60*10*samplingRate, 60*12*samplingRate ] )
	
	#testing convolution stuff, temporary removal
	'''	
	plt.plot( xaxis, values )
	plt.xlabel("Time (s)")
	#plt.show()
	
	if ( len(sys.argv) >= 3 ):
		plt.savefig(sys.argv[2])
	else:
		plt.savefig("out.png")

	print "OUT DONE"
	#plt.clf()
	#yaxisrms = windowRMS(values,samplingRate/2)  
	#xaxisrms = numpy.arange( 0, float(len(yaxisrms)) / samplingRate, 1.0 / samplingRate )
	#plt.plot( xaxisrms, yaxisrms )
	#plt.savefig("rms.png")
	colourArray = [ 'b', 'y', 'm', 'w', 'c', 'g', 'r', 'k' ] 
	plt.clf()
	for i in range(len(arrListY)):
		plt.plot( arrListX[i], arrListY[i], colourArray[-i] )
	plt.savefig("split.png")
	
	plt.hold(False)
	for i in range(len(arrListY)):
		xaxis = numpy.arange( 0, float(len(arrListY[i])) / samplingRate, 1.0 / samplingRate )
		plt.plot( xaxis, arrListY[i] )
		if ( i % 2 ):
			plt.savefig("answer_"+str((i+1)/2)+".png")
		else:
			plt.savefig("reading_"+str((i/2)+1)+".png")

	print "SPLIT SAVE DONE"
		
#define hard limit as half of peak

	#valThresh = numpy.max(values) / 4
	#valThresh = numpy.mean( numpy.abs(values) )
	#valThresh = numpy.mean( windowRMS(values,samplingRate/2) )
	#valThresh = 0.4 #arbitrary
	
	
	'''
	#end of conv test

	toPlotX = []
	toPlotY = []

	#convWin = numpy.ones( WINDOW_WIDTH * samplingRate )
	convWin = signal.triang( WINDOW_WIDTH * samplingRate )
	#starProduct0 = numpy.convolve( abs(values), convWin, 'same' )
	starProduct1 = numpy.convolve( abs(arrListY[1]), convWin, 'same' )
	starProduct1 = starProduct1 / max(starProduct1)
	starProduct2 = numpy.convolve( abs(arrListY[3]), convWin, 'same' )
	starProduct2 = starProduct2 / max(starProduct2)

	spThresh = 0.1
	#spThresh = numpy.mean( starProduct0 )

	silenceList = []
	holder = starProduct1 < spThresh
	silenceList.append(holder)
	holder = starProduct2 < spThresh
	silenceList.append(holder)		

	for i in range (2):
		silence = True
		period = i*2+1
		silList = []
		truthList = silenceList[i]
		for j in range(truthList.size):
			if (silence and not truthList[j]): #currently is silent
				silence = False
				silList.append(j)
			elif (not silence and truthList[j]):
				silence = True
				silList.append(j)
		#print silList
		#now we remove things in twos if they're too close
		threshold = SIL_THRESH * samplingRate
		j = 0
		while ( j < len(silList)-1 ):
			if ( silList[j+1] - silList[j] < threshold ):
				silList.pop(j)
				silList.pop(j)
			else:
				j = j + 1

		toPlotX.append( numpy.split(arrListX[period],silList) )
		toPlotY.append( numpy.split(arrListY[period],silList) )
		print "reading "+str(i+1)+" has "+str(len(silList)/2)+" pauses"
	'''
	for i in range (2):
		silence = True
		period = i*2+1
		toCheck = arrListY[period]
		extremaList = findPeaks(toCheck)
		yesList = []
		silList = []
		for j in extremaList:
			if (abs(toCheck[j]) >= valThresh):
				yesList.append(j)
			if (len(yesList)): 
				if (yesList[0] < j - samplingRate/2):
					yesList.pop(0)
			if (silence): #currently is silent
				if (len(yesList) >= UPPER_BOUND):
					silence = False
					silList.append(yesList[0])
			else:
				if (len(yesList) < LOWER_BOUND):
					silence = True
					silList.append(j)
		toPlotX.append( numpy.split(arrListX[period],silList) )
		toPlotY.append( numpy.split(toCheck,silList) )
	'''
	plt.clf()		
	plt.hold(True)
	plt.plot( arrListX[0], arrListY[0], 'g', arrListX[2], arrListY[2], 'g') #for the reading parts
	for i in range(len(toPlotX)):
		silence = True 
		xList = toPlotX[i]
		yList = toPlotY[i]
		for j in range(len(xList)):
			if (silence):
				plt.plot( xList[j], yList[j], 'r')
				silence = False
			else:
				plt.plot( xList[j], yList[j], 'b')
				silence = True
	plt.savefig( "silences.png" )

#colours: green for read, blue for speak, red for pause in answering

	for i in range(len(toPlotX)):
		plt.clf()
		silence = True 
		xList = toPlotX[i]
		yList = toPlotY[i]
		for j in range(len(xList)):
			if (silence):
				plt.plot( xList[j], yList[j], 'r')
				silence = False
			else:
				plt.plot( xList[j], yList[j], 'b')
				silence = True
		plt.savefig( "silences"+str(i+1)+".png" )
	
	#for debugging purposes
	#plt.hold(False)
	#plt.plot(arrListX[1], starProduct1)
	#plt.savefig( "Convolution 1.png" )
	#plt.plot(arrListX[3], starProduct2)
	#plt.savefig( "Convolution 2.png" )


if __name__ == "__main__":
	main()
