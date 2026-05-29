import numpy as np
import matplotlib.pyplot as plt
#  The warning triangle appears because although we have imported the package
#  as plt, we haven't actually used it within this section of the code.
y = np.sin(1.2)
#  importing modules 'numpy' and 'matplotlib.pyplot' as np and plt respectively
#%% 
import numpy
import matplotlib.pyplot
#  importing modules 'numpy' and 'matplotlib.pyplot' wihtout assigning
#  name. Would be required to write full module name for use. e.g. numpy.sin
#  for use of sine function.
#%%
from numpy import sin, cos, tan
y = sin(1.2)
x = cos(1.2)
z = tan(1.2)
#  importanting one or more functions from a package. Generally not used as
#  it makes it hard to read code.
#%% 
import numpy as np
from scipy import special 
x = special.factorial(np.arange(1,11))
##    ssadassa