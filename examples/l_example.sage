# An example where a larger value for l has to be considered for the computed ENT witness (1,1).
# The reason is that we have constraint term groups for (3,1) and (2,1) and we have to make up for the -100 in the guard. So we have to scale down this coefficient with (2/3)^l.

# Matrix C
c = sage.all.Matrix(sage.all.QQbar,[[1,-100],[0,1]])

# Matrix A
a = sage.all.Matrix(sage.all.QQbar,[[3,0], [0,2]])

# Matrix B
b = sage.all.Matrix(sage.all.QQbar,[[3,0],[0,2]])

# Probability p
p = sage.all.QQ(1/2)
