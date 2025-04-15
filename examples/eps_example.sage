# An example where a smaller value for eps has to be considered for the ENT witness (1,1) computed by smtrat.
# The reason is that we have constraint term groups for (i,o) = (2,1) and (i,o) = (sqrt(3),sqrt(3)).

# Matrix C
c = sage.all.Matrix(sage.all.QQbar,[[1,-1],[0,1]])

# Matrix A
a = sage.all.Matrix(sage.all.QQbar,[[2,0], [0,3]])

# Matrix B
b = sage.all.Matrix(sage.all.QQbar,[[2,0],[0,1]])

# Probability p
p = sage.all.QQ(1/2)
