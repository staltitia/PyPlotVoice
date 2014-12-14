import numpy

def fftFilter( inArray, samplingRate, inFreq, filterType = "low" ):
	ftfreq = numpy.fft.fftfreq( inArray.size, d = 1.0/samplingRate )
	table = []
	if filterType == "high":
		table = abs( ftfreq ) < inFreq
	elif filterType == "low":
		table = abs( ftfreq ) > inFreq
	else:
		print "fftFilter: Invalid type. Please use either \'high\' or \'low\'"
		return numpy.array([])
	ft = numpy.fft.fft(inArray)
	ft[table] = 0
	ift = numpy.fft.ifft(ft)
	return ift

def centerClip ( inArray, threshPercentage ):
	#inArray is a numpy array

	C_l = float(threshPercentage) / 100 * max(abs(inArray))

	toSub = inArray >= C_l
	toZero = abs(inArray) < C_l
	toAdd = inArray <= -C_l

	toRet = inArray.copy()
	toRet[toSub] = toRet[toSub] - C_l
	toRet[toZero] = 0
	toRet[toAdd] = toRet[toAdd] + C_l

	return toRet

def removeHarmonics( inX, inY ):
	#TODO
	#given a list of troughs
	#determine lowest harmonic
	#usually small delta between harmonics
	pass
