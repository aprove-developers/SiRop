import sage.all

def get_amount_tests():
  """Return the number of test cases."""
  return 6

def test(i):
  """Exemplary test cases."""
  print()
  print("# Test", i, "\n")
  match i:
    case 0: # terminating
      c = sage.all.Matrix(sage.all.QQbar,[[-5, 0], [4, 2], [-5, 12]])
      a = sage.all.Matrix(sage.all.QQbar,[[-1, 2], [3, 1]])
      b = a.inverse()
      return c, a, b, 0.5
    case 1: # terminating
      c = sage.all.Matrix(sage.all.QQbar,[[-1, 2], [-1, 1], [8, -1]])
      a = sage.all.Matrix(sage.all.QQbar,[[6, 1], [0, 1]])
      b = a.inverse()
      return c, a, b, 0.5
    case 2: # terminating
      c = sage.all.Matrix(sage.all.QQbar,[[-1, -5], [11, 1], [-1, 2]])
      a = sage.all.Matrix(sage.all.QQbar,[[-3, 0], [-1, 51]])
      b = a.inverse()
      return c, a, b, 0.5
    case 3: # nonterminating
      c = sage.all.Matrix(sage.all.QQbar,[[7, 13], [8, -1], [-1, 4]])
      a = sage.all.Matrix(sage.all.QQbar,[[-24, 53], [2, 27]])
      b = a.inverse()
      return c, a, b, 0.5
    case 4: # nonterminating
      c = sage.all.Matrix(sage.all.QQbar,[[-5, -1], [-252, -2], [-4, 0]])
      a = sage.all.Matrix(sage.all.QQbar,[[-1, -1], [0, 1]])
      b = a.inverse()
      return c, a, b, 0.5
    case 5: # nonterminating
      c = sage.all.Matrix(sage.all.QQbar,[[2, 0], [1, 1]])
      a = sage.all.Matrix(sage.all.QQbar,[[2, 1], [1, 2]])
      b = sage.all.Matrix(sage.all.QQbar,[[1, 0], [0, 1]])
      return c, a, b, 0.5
    case _:
      print("Invalid test number")
      exit(-1)
