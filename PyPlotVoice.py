#Author: Daniel GHK Chong
#Date: 20 Nov 2014
#File: PyPlotVoice.py

#Python Version: 2.7.6
#Dependencies: scipy

#!/usr/bin/python
from scipy.io import wavfile as wavfile
import sys #to get command line arguments
import numpy
import matplotlib.pyplot as plt

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
	
	plt.plot( xaxis, values )
	plt.xlabel("Time (s)")
	#plt.show()
	
	if ( len(sys.argv) >= 3 ):
		plt.savefig(sys.argv[2])
	else:
		plt.savefig("out.png")

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

if __name__ == "__main__":
	main()
