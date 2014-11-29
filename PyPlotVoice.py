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
SIL_THRESH = 0.3 #in seconds
NORM_CONV_THRESH = 0.1 #normalised

def ConvSilence( inXArray, inYArray, samplingRate ):		

	if inXArray.size != inYArray.size:
		print "Error in ConvSilence: Dimensions must agree"
		return [ None, None, None, None ]

	#convWin = numpy.ones( WINDOW_WIDTH * samplingRate )
	convWin = signal.triang( WINDOW_WIDTH * samplingRate )
	
	starProduct = numpy.convolve( abs(inYArray), convWin, 'same' )
	starProduct = starProduct / max(starProduct)

	silenceList = starProduct < NORM_CONV_THRESH

	threshold = SIL_THRESH * samplingRate
		
	silence = True
	silList = []
	for i in range(silenceList.size):
		risingEdge = silence and not silenceList[i]
		fallingEdge = not silence and silenceList[i]
		if (risingEdge or fallingEdge):
			silence = not silence
			if ( len(silList) > 0 and i - silList[-1] < threshold ):
				silList.pop()
			else:
				silList.append(i)	

	toRetX = numpy.split(inXArray,silList)
	toRetY = numpy.split(inYArray,silList)

	#now we split between evens and odds
	#because we have silence=True to start,
	#the evens are silent, and the odds are not

	silentX = toRetX[::2]
	silentY = toRetY[::2]

	speakX = toRetX[1::2]
	speakY = toRetY[1::2]

	#print "reading "+str(i+1)+" has "+str(len(silList)/2)+" pauses"

	return [ silentX, silentY, speakX, speakY ]

def SilenceCounter( inXArray, inXSilentList, samplingRate ):
	
	arrListX = numpy.split( inXArray, numpy.arange(samplingRate*60, inXArray.size, samplingRate*60) )
	count = []
	silList = numpy.concatenate( inXSilentList )
	for xList in arrListX:
		count.append( numpy.intersect1d( xList, silList, assume_unique = True ).size )

	return numpy.array(count) 

def splitter( inX, inY, samplingRate, function ):
	return function( inX, inY, samplingRate )

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

	[ans1SilX, ans1SilY, ans1SpkX, ans1SpkY] = splitter( arrListX[1], arrListY[1], samplingRate, ConvSilence )
	[ans2SilX, ans2SilY, ans2SpkX, ans2SpkY] = splitter( arrListX[3], arrListY[3], samplingRate, ConvSilence )

	ans1Bucket = SilenceCounter( arrListX[1], ans1SilX, samplingRate )
	ans2Bucket = SilenceCounter( arrListX[3], ans2SilX, samplingRate ) 

	plt.clf()
	plt.hold(True)
	#for the reading parts
	#colours: green for read, blue for speak, red for pause in answering
	plt.plot( arrListX[0], arrListY[0], 'g', arrListX[2], arrListY[2], 'g')
	
	for i in range(len(ans1SilX)):
		plt.plot( ans1SilX[i], ans1SilY[i], 'r' )
	for i in range(len(ans1SpkX)):
		plt.plot( ans1SpkX[i], ans1SpkY[i], 'b' )
	for i in range(len(ans2SilX)):
		plt.plot( ans2SilX[i], ans2SilY[i], 'r' )
	for i in range(len(ans2SpkX)):
		plt.plot( ans2SpkX[i], ans2SpkY[i], 'b' )
	plt.savefig( "silences.png" )

	#minute by minute save

	for i in range(20):
		plt.xlim( [ i*60, (i+1)*60 ] )
		plt.savefig( "silences_minute_"+str(i+1)+".png" )

	#individual answer plots
	plt.xlim( [ 2*60, 10*60 ] )
	plt.savefig( "silences1.png" )
	
	plt.xlim( [ 12*60, 20*60 ] )
	plt.savefig( "silences2.png" )

	#for minute-based silence bar chart
	plt.clf()
	percentage =  ans1Bucket * 100 / ( samplingRate * 60 )
	plt.bar( numpy.arange(0.6,ans1Bucket.size+0.6, 1), percentage, color='r' )
	plt.ylim( [0, 120] )
	plt.ylabel( "Percentage of time silent" )
	plt.xlabel("Time (minutes)")
	plt.savefig( "silBarChart1.png" )

	plt.clf()
	percentage =  ans2Bucket * 100 / ( samplingRate * 60 )
	plt.bar( numpy.arange(0.6,ans2Bucket.size+0.6, 1), percentage, color='r' )
	plt.ylim( [0, 120] )
	plt.ylabel( "Percentage of time silent" )
	plt.xlabel("Time (minutes)")
	plt.savefig( "silBarChart2.png" )

if __name__ == "__main__":
	main()
