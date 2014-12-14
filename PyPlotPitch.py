#Author: Daniel GHK Chong
#Date: 1st December 2014
#File: PyPlotPitch.py

import numpy
from scipy.io import wavfile as wavfile
import sys
import matplotlib.pyplot as plt
from FindPeaks import *
from Filters import *

AMDF_TOPRINT = 0
WIN_WIDTH = 0.03 #in seconds
SMOOTH_WIDTH = 0.001 #in seconds

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
		return wavfile.read(filename)
	else:
		#using numm to read a .webm
		values = numm.sound2np(filename)
		#we use just the left channel
		values = numpy.split( values, [1], axis=1 )[0]
		#numm defaults to 44.1 kHz sampling rate
		#samplingRate = 44100

		#return [ samplingRate, values ]

		#dev machine is REALLY BAD, concessions made for test purposes
		values = shrink ( values, 5 )
		samplingRate = 44100 / 5
		return [ samplingRate, values ]

def fundFreqBlocks ( inArray, samplingRate, win, method="AMDF" ):
	#inArray is a numpy array
	#samplingRate is an int
	#win is window length in seconds
	#method is either AMDF or ACF (autocorr)

	#for testing
	global AMDF_TOPRINT

	#returns fundamental frequencies in numpy array
	if method != "AMDF" and method != "ACF":
		print "Error in fundFreqBlocks: method must be either \'AMDF\' or \'ACF\'"
		return numpy.array([])

	toRet = []
	window = win*samplingRate
	splitArr = numpy.arange(window,inArray.size,window)	
	toProcess = numpy.split( inArray, splitArr )
	toConv = numpy.ones(SMOOTH_WIDTH * samplingRate)
	for i in range( len(toProcess) ):
		if method == "ACF":
			autoCorr = Autocorrelate( toProcess[i] )
			maxInd = numpy.argmax( autoCorr )
			f0 = maxInd / samplingRate
			toRet.append(f0)
		else:
			#curve = AMDF( toProcess[i] )

			if i < 1:
				left = numpy.zeros( len(toProcess[i]) )
			else:
				left = toProcess[i-1]
			if i+1 >= len(toProcess):
				right = numpy.zeros( len(toProcess[i]) )
			else:
				right = toProcess[i+1]

			curve = EAMDF( left, toProcess[i], right )
			AMDF_TOPRINT = AMDF_TOPRINT + 1
			curve = numpy.convolve( curve, toConv, mode='same' ) 
			maxPeaks = findPeaks( curve, 'max' )
			truncIndHead = 0
			truncIndTail = len(curve)
			if len(maxPeaks) > 1:
				truncIndHead = maxPeaks[0]
				truncIndTail = maxPeaks[-1]
			trunc = curve[truncIndHead:truncIndTail]
			f0 = numpy.argmin( trunc )
			toRet.append( f0+truncIndHead )
				
			plt.hold(True)
			plt.clf()
			plt.plot(curve, 'b')
			plt.axvline(x=truncIndHead, color='k')
			plt.axvline(x=truncIndTail, color='k')
			plt.axvline(x=f0+truncIndHead, color='r')
			plt.savefig("AMDF%04d.png"%(AMDF_TOPRINT))
			
		toPrint ="Block %d/%d done\033[A" % ( i+1 , len(toProcess) )
		print toPrint
	return numpy.array(toRet)

def Autocorrelate ( inArray ):
	toRet = numpy.correlate( inArray, inArray, mode = 'same' )
	return toRet

def AMDF( inArray ):
	#inArray is a numpy array

	D = [] #array of scalars

	for i in range( len(inArray) ):
		rolled = numpy.roll( inArray, -i )
		holder = abs( numpy.add( inArray, (-1)*rolled ) )
		truncated = holder[:inArray.size-i]
		D.append( numpy.mean(truncated) )
	return numpy.array( D )

def EAMDF ( N0, N1, N2 ):
	#N1, N2, and N3 are  numpy arrays

	lPad = N0[ N0.size / 2 : ]
	rPad = N2[ : N2.size / 2 ]	
	return AMDF( numpy.concatenate( (lPad, N1, rPad) ) )

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

	import time

	startTime = time.time()

	#the next step is to determine the fundamental frequencies
	ans1LPS = fftFilter( arrListY[1], samplingRate, 900, 'low' )
	ans1Filtered = centerClip( ans1LPS, 30 )
	#ans1f0 = fundFreqBlocks(ans1Filtered, samplingRate, WIN_WIDTH, 'AMDF')
	#ans1f0 = fundFreqBlocks( arrListY[1], samplingRate, WIN_WIDTH, 'AMDF' )	
	toConv = numpy.ones(SMOOTH_WIDTH * samplingRate)
	from TaskThreading import fundFreqBlocksThreaded
	ans1f0 = fundFreqBlocksThreaded( ans1Filtered, samplingRate, WIN_WIDTH, toConv, concurrent = 25 )
	

	f0X = numpy.arange(ans1f0.size) * WIN_WIDTH
	toSave = ans1f0 > 0
	toPlotX = f0X[toSave]
	toPlotY = ans1f0[toSave]
	#from AMDF import AMDF

	#ans1 = AMDF( ans1Filtered, samplingRate, WIN_WIDTH )
	#toShow = ans1.process()

	#for i in range( len(toShow) ):	
	#	plt.clf()
	#	plt.plot( toShow[i] )
	#	plt.savefig( "ans1AMDF%03d.png" % i )

	plt.clf()
	plt.plot( toPlotX, toPlotY, '.' )
	plt.savefig( "ans1f0.png" )

#	ans2LPS = fftFilter( arrListY[3], samplingRate, 900, 'low' )
#	ans2Filtered = centerClip( ans2LPS, 30 )
#	ans2f0 = fundFreqBlocks(ans2Filtered, samplingRate, WIN_WIDTH, 'AMDF')
	#ans2f0 = fundFreqBlocks( arrListY[3], samplingRate, WIN_WIDTH, 'AMDF' 	

#	plt.clf()
#	plt.plot( ans2f0, '.' )
#	plt.savefig( "ans2f0.png" )

	endTime = time.time()
	print "time taken is %d seconds" % ( endTime - startTime )

if __name__ == "__main__":
	main()
