import numpy
from PyPlotPitch import *

arr1 = numpy.sin( numpy.linspace( 0, 2*numpy.pi, 10000 ) )
arr2 = numpy.sin( numpy.linspace( 0, 7*numpy.pi, 10000 ) )
arr3 = numpy.sin( numpy.linspace( 0, 3*numpy.pi, 10000 ) )
inArr = numpy.add( numpy.add(3*arr1, 5*arr2), arr3 )
out = AMDF( inArr )

import matplotlib.pyplot as plt

plt.plot( numpy.arange(out.size), out )
plt.show()

print out
