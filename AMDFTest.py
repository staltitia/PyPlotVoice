import numpy
from PyPlotPitch import *
from Filters import *
from AMDF import AMDF


arr1 = numpy.sin( numpy.linspace( 0, 2*numpy.pi, 10000 ) )
arr2 = numpy.sin( numpy.linspace( 0, 7*numpy.pi, 10000 ) )
arr3 = numpy.sin( numpy.linspace( 0, 3*numpy.pi, 10000 ) )
inArr = numpy.add( numpy.add(3*arr1, 5*arr2), arr3 )
#out = AMDF( inArr )

import matplotlib.pyplot as plt

#out = centerClip ( inArr )

myObj = AMDF( inArr, 100, 0.1 )
out = myObj.process()

print out

#plt.subplot(211)
#plt.plot( numpy.arange(out.size), out )
#plt.subplot(212)
#plt.plot( numpy.arange(inArr.size), inArr )
#plt.show()
#plt.savefig( "pureSig.png" )
#print out
