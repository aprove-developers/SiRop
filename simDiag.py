import sage.all
import numpy

def matrices_commute(a, b):
  """Takes two values and returns True if they commute, otherwise False."""
  return (a*b == b*a)

def get_diagonals_quantities(a):
  """Takes a matrix and returns a dictionary of the distinct values on the matrix diagonal and their quantities."""
  d = dict()
  for e in a.diagonal():
    if (e not in d):
      d.update({e: a.diagonal().count(e)})
  return d

def get_transformation_matrix(ev_dict, transformed_b):
  """
  Takes a dictionary with values and their quantities and a matrix.
  The matrix is a product S⁻¹ * B * S where S is the matrix transforming a matrix A to Jordan Normal Form.

  Returns the transformation matrix to simultaneously diagonalize A and B.
  """
  ts = []
  counter = 0
  for ei in range(len(ev_dict)):
    mi = list(ev_dict.values())[ei]
    b_block = sage.all.Matrix(sage.all.QQbar, mi, mi, lambda i, j: transformed_b[i+counter][j+counter])
    b_block_d, s_b_block = b_block.jordan_form(subdivide = False, transformation = True)
    ts.append(s_b_block)
    counter += mi
  return sage.all.block_diagonal_matrix(ts, subdivide=False)


def is_diagonal(a):
  """Takes a matrix and returns True if it is diagonal, otherwise False."""
  return ((a == numpy.diag(a.diagonal())).all())


def sim_diag(a, b):
  """
  Takes two matrices.
  Computes a transformation matrix T to simultaneously diagonalize them.
  Returns T⁻¹, the two diagonalized matrices, and T.
  """
  if (not matrices_commute(a, b)): return None, None, None, None

  # Compute JNF of a
  a_j, s_a = a.jordan_form(subdivide = False, transformation = True)

  # Perfrom this transformation on b
  b_j = s_a.inverse() * b * s_a

  # Create dictionary of distinct eigenvalues of a and their multiplicities
  dict_eig_vals_a = get_diagonals_quantities(a_j)

  # Compute transformation matrix to simultaneously diagonalize a_j and b_j as well as its inverse
  t = get_transformation_matrix(dict_eig_vals_a, b_j)
  ti = t.inverse()

  # Compute diagonal matrices
  a_d = ti * a_j * t
  b_d = ti * b_j * t

  # Compute transformation matrix to simultaneously diagonalize a and b and its (?) inverse
  r = s_a * t
  ri = r.inverse()

  # Check if simultaneous diagonalization was successful (fails if matrix A or B is not diagonalizable)
  if not (is_diagonal(a_d) and is_diagonal(b_d)): return None, None, None, None

  return ri, a_d, b_d, r
