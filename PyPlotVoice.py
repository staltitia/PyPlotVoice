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
NORM_CONV_THRESH = 0.1 #normalised

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
	
	#first, we split the data into its four sections

	arrListY = numpy.split(values, [ 60*2*samplingRate, 60*10*samplingRate, 60*12*samplingRate ] )
	
	xaxis = numpy.arange( 0, float(len(values)) / samplingRate, 1.0 / samplingRate )

	arrListX = numpy.split(xaxis, [ 60*2*samplingRate, 60*10*samplingRate, 60*12*samplingRate ] )
	
	toPlotX = []
	toPlotY = []

	#convWin = numpy.ones( WINDOW_WIDTH * samplingRate )
	convWin = signal.triang( WINDOW_WIDTH * samplingRate )
	starProduct1 = numpy.convolve( abs(arrListY[1]), convWin, 'same' )
	starProduct1 = starProduct1 / max(starProduct1)
	starProduct2 = numpy.convolve( abs(arrListY[3]), convWin, 'same' )
	starProduct2 = starProduct2 / max(starProduct2)

	silenceList = []
	silenceList.append(starProduct1 < NORM_CONV_THRESH)
	silenceList.append(starProduct2 < NORM_CONV_THRESH)		

	threshold = SIL_THRESH * samplingRate
	for i in range (2):
		silence = True
		period = i*2+1
		silList = []
		truthList = silenceList[i]
		for j in range(truthList.size):
			risingEdge = silence and not truthList[j]
			fallingEdge = not silence and truthList[j]
			if (risingEdge or fallingEdge):
				silence = not silence
				if ( j - silList[-1] < threshold ):
					silList.pop()
				else:
					silList.append(j)

		toPlotX.append( numpy.split(arrListX[period],silList) )
		toPlotY.append( numpy.split(arrListY[period],silList) )
		print "reading "+str(i+1)+" has "+str(len(silList)/2)+" pauses"
	
	plt.clf()		
	plt.hold(True)
	#for the reading parts
	#colours: green for read, blue for speak, red for pause in answering
	plt.plot( arrListX[0], arrListY[0], 'g', arrListX[2], arrListY[2], 'g')
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

	#individual answer plots
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
