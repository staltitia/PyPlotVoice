import matplotlib.pyplot as plt
from subprocess import call

#this assumes a suitable version of avconv is installed

def MakeVid ( inArrX, inArrY, samp, sndfile, outfile ):
	#inArr(X/Y) is a sound wave, numpy array of numbers
	#samp is the sampling rate, int
	#sndfile and outfile are strings
	#note: this will overwrite file with name fileName

	if len(inArrX) != len(inArrY):
		
		print "X Array(%d) and Y Array(%d) dimensions must agree"%(len(inArrX),len(inArrY))
		return

	numFrames = int ( len(inArrX) * 24 / samp )
	#we assume 24fps

	#we generate a silent video then join the video with audio
	#we plot 1s worth of images and concatenate it
	fig = plt.figure()
	ax = fig.add_subplot(111)

	ax.plot( inArrX, inArrY )
	
	import numpy
	moverX = numpy.array( [0,0] )
	moverY = plt.ylim()

	basefile = False
	for i in range(numFrames):
		print ("frame number %d/%d is starting\033[A"%(i,numFrames))
		ax.plot( moverX + float(i)/30, moverY, 'r' )
		plt.savefig( "holder%d.png"%(i) )
		del ax.lines[-1]
	
	call( [ 'avconv', '-r','24','-i', 'holder%d.png', 'nosnd.avi'] )
	#now we join the video and audio
	call( ['avconv','-i','nosnd.avi','-i',sndfile,'-c','copy',outfile])

	#cleanup
	
	call( 'rm nosnd.avi', shell=True )
	call( 'rm holder*.png', shell=True  )

def main():
	#testing purposes
	import numpy
	toPlot = numpy.arange(20)
	fig = plt.figure()
	ax = fig.add_subplot(111)
	
	ax.plot(toPlot)
	moverY = plt.ylim()
	moverX = numpy.array( [1,1] )

	ax.plot(moverX, moverY)
	plt.savefig("mkVid0.png")
	
	movedX = moverX + 10
	del ax.lines[-1]
	
	ax.plot(movedX, moverY)
	plt.savefig("mkVid1.png")

if __name__ == "__main__":
	main()
	
