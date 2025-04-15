# An example where a larger value for r has to be considered for the computd ENT witness (1,1).
# This example is almost identical to r_example but here we have to consider d = n instead of d = p.
# The reason is that we constraint groups for (2,1) and (2,4) and we have to make up for the -100 in the guard. So we have to scale down this coefficient with 0.25^r.

# Matrix C
c = sage.all.Matrix(sage.all.QQbar,[[1,-100],[0,1]])

# Matrix A
a = sage.all.Matrix(sage.all.QQbar,[[2,0], [0,4]])

# Matrix B
b = sage.all.Matrix(sage.all.QQbar,[[2,0],[0,1]])

# Probability p
p = sage.all.QQ(1/2)
