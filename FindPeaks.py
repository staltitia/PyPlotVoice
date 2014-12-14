import numpy

def findPeaks ( inArray, mode="both" ): 
	#max for max peaks, min for min peaks, both for both
	if len(inArray) < 2:
		return inArray
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
#:	print toRet
	return numpy.array(toRet)

def findPeakVals ( inArray, mode="both" ): 
	#max for max peaks, min for min peaks, both for both
	toRet = []
	ascending = False
	if (inArray[1] > inArray[0]):
		ascending = True
	for i in range(len(inArray) - 1):
		if ( ascending and inArray[i+1] < inArray[i] ):
			if not (mode == "min"):
				toRet.append(inArray[i])
			ascending = False
		if ( not ascending and inArray[i+1] > inArray[i]):
			if not (mode == "max"):
				toRet.append(inArray[i])
			ascending = True
#:	print toRet
	return numpy.asarray(toRet)
