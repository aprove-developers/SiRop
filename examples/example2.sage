# Simple terminating loop
# This loop models the following program:
# while (x > 0) { x = x or x = -(x + 1) }

# Matrix C
c = sage.all.Matrix(sage.all.QQbar,[[1, 0], [0, 1]])

# Matrix A
a = sage.all.Matrix(sage.all.QQbar,[[-1, -1], [0, 1]])

# Matrix B
b = sage.all.Matrix(sage.all.QQbar,[[1, 0], [0, 1]])

# Probability p
p = sage.all.QQ(1/4)
