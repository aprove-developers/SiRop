# An example which is terminating for d=p and d=n.
# The reason is that we have constraint term groups for (2,1), (2,4), and (2,0.25).
# This example combines ideas from r_example and r_example_n

# Matrix C
c = sage.all.Matrix(sage.all.QQbar,[[1,-1,-1],[0,1,0],[0,0,1]])

# Matrix A
a = sage.all.Matrix(sage.all.QQbar,[[2,0,0], [0,1,0],[0,0,4]])

# Matrix B
b = sage.all.Matrix(sage.all.QQbar,[[2,0,0],[0,4,0],[0,0,1]])

# Probability p
p = sage.all.QQ(1/2)
