#Author: Daniel GHK Chong
#Date: 1st December 2014
#File: PyPlotPitch.py

# we refer to Tan and Karnjanadecha's paper on pitch detection
# in using an autocorrelation of the input wave to determine
# the fundamental frequency

import numpy
from scipy.io import wavfile as wavfile
import sys
import matplotlib.pyplot as plt
from FindPeaks import *

WIN_WIDTH = 0.5 #in seconds

def shrink ( inArray, factor ):
	values = inArray.copy()
	toPad = numpy.zeros( inArray.size % factor )
	if toPad.size > 0:
		values = numpy.concatenate( values, toPad )
	reshaped = values.reshape( ( values.size / factor, factor) )
	return numpy.mean( reshaped, axis=1 )

def readAudio( filename ):
	#returns list, [ samplingRate, values ]
	import os
	name, ext = os.path.splitext(filename)

	if ext == '.wav':	#reading a .wav
		return  wavfile.read(filename)
	else:
		#using numm to read a .webm
		values = numm.sound2np(filename)
		#average out stereo input
		#values = numpy.mean( values, axis=1 )
		#we use just the left channel
		values = numpy.split( values, [1], axis=1 )[0]
		#numm defaults to 44.1 kHz sampling rate
		#samplingRate = 44100

		#return [ samplingRate, values ]

		#dev machine is REALLY BAD, concessions made for test purposes
		values = shrink ( values, 5 )
		samplingRate = 44100 / 5
		return [ samplingRate, values ]

def fftFilter( inArray, samplingRate, inFreq, filterType = "low" ):
	ftfreq = numpy.fft.fftfreq( inArray.size, d = 1.0/samplingRate )
	table = []
	if filterType == "high":
		table = abs( ftfreq ) < inFreq
	elif filterType == "low":
		table = abs( ftfreq ) > inFreq
	else:
		print "fftFilter: Invalid type. Please use either \'high\' or \'low\'"
		return numpy.array()
	ft = numpy.fft.fft(inArray)
	print "FT complete"
	ft[table] = 0
	print "Filter complete"
	ift = numpy.fft.ifft(ft)
	print "IFT complete"
	return ift

def fundFreqCont ( inArray, win ):
	#returns fundamental frequencies in numpy array
	toRet = []
	toProcess = inArray.copy()
	gap = win/2
	toProcess = numpy.concatenate( [ numpy.zeros(gap),inArray,numpy.zeros(gap) ] )
	for i in range(len(inArray)):
		autoCorr = Autocorrelate( toProcess[i:i+win] )
		f0 = numpy.argmax( autoCorr )
		toRet.append(f0)

	return numpy.array(toRet)

def fundFreqBlocks ( inArray, samplingRate, win, method="AMDF" ):
	#inArray is a numpy array
	#samplingRate is an int
	#win is window length in seconds
	#method is either AMDF or ACF (autocorr)

	#returns fundamental frequencies in numpy array
	if method != "AMDF" and method != "ACF":
		print "Error in fundFreqBlocks: method must be either \'AMDF\' or \'ACF\'"
		return numpy.array([])

	toRet = []
	window = win*samplingRate
	splitArr = numpy.arange(window,inArray.size,window)	
	toProcess = numpy.split( inArray, splitArr )
	AMDFShift =  samplingRate / 300
	toPrint = ''	
	for i in range( len(toProcess) ):
		if method == "ACF":
			autoCorr = Autocorrelate( toProcess[i] )
			maxInd = numpy.argmax( autoCorr )
			f0 = maxInd / samplingRate
			toRet.append(f0)
		else:
			curve = AMDF( toProcess[i] )
			minPeaks = findPeaks( curve, 'min' )
			if len(minPeaks) > 2:
				f0 = minPeaks[1]
			else:
				f0 = 0
			toRet.append(f0)
		toPrint ="Block "+str(i+1)+"/"+str(len(toProcess))+" is done!"
		print toPrint
	return numpy.array(toRet)

def Autocorrelate ( inArray ):
	toRet = numpy.correlate( inArray, inArray, mode = 'same' )
	return toRet

def AMDF( inArray ):
	#inArray is a numpy array, samplingRate is an int

	pad = numpy.zeros( inArray.size )
	toRoll = numpy.concatenate( [pad, inArray] )
	D = [] #array of scalars

	for i in range( len(inArray) ):
		rolled = numpy.roll( toRoll, -i )
		holder = abs( numpy.add( toRoll, (-1)*rolled ) )
		truncated = holder[pad.size:toRoll.size-i]
		D.append( numpy.mean(truncated) )
	return numpy.array( D )

def main():
	filename = ''

	if ( len(sys.argv) >= 2 ):
		filename = sys.argv[1]
	else:
		print("Please include a file as a command line argument")
		return
	try:
		 [ samplingRate, values ] =  readAudio(filename)
	except IOError:
		print( filename + " does not exist. Please try again.")
		return

	#getting this far means that the file is good, and has been opened
	
	#first, we split the data into its four sections

	arrListY = numpy.split(values, [ 60*2*samplingRate, 60*10*samplingRate, 60*12*samplingRate ] )
	
	xaxis = numpy.arange( 0, float(len(values)) / samplingRate, 1.0 / samplingRate )

	arrListX = numpy.split(xaxis, [ 60*2*samplingRate, 60*10*samplingRate, 60*12*samplingRate ] )

	#the next step is to determine the fundamental frequencies
	#ans1Filtered = fftFilter( arrListY[1], samplingRate, 1000, 'low' )
	#ans1f0 = fundFreqBlocks(ans1Filtered, samplingRate, WIN_WIDTH, 'AMDF')
	ans1f0 = fundFreqBlocks( arrListY[1], samplingRate, WIN_WIDTH, 'AMDF' )
	
	plt.clf()
	plt.plot( ans1f0, '.' )
	plt.savefig( "ans1f0.png" )

	#ans1Filtered = fftFilter( arrListY[1], samplingRate, 1000, 'low' )
	#ans1f0 = fundFreqBlocks(ans1Filtered, samplingRate, WIN_WIDTH, 'AMDF')
	ans2f0 = fundFreqBlocks( arrListY[3], samplingRate, WIN_WIDTH, 'AMDF' )
	
	plt.clf()
	plt.plot( ans2f0, '.' )
	plt.savefig( "ans2f0.png" )

if __name__ == "__main__":
	main()
