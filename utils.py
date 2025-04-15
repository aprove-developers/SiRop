import sage.all
import sage.symbolic.expression as sym_expr

# Workaround for get() for dictionaries. This function also works for unhashable keys.
# The problem is that Python dictionaries generally require hashable keys.
# If unhashable values are used as keys, they cannot be found again in the dictionary.
# Therefore, the methods provided by Python to get a value corresponding to a key do not work and this workaround is used instead.
def get_helper(key, d):
  """
  Takes a possibly unhashable key and a dictionary.
  Returns the key and corresponding value if it is in the dictionary, None, None otherwise.
  """
  for k in d:
    if k == key:
      return k, d[k]
  return None, None


def zeta(val):
  """Takes a value and returns it divided by its absolute value."""
  return val / abs(val)


def to_complex_tuple(z):
  """Takes a number z and returns its real and imaginary part as a 2-tuple."""
  if z.is_real() or "x" in str(z) or "g" in str(z):
    return (z, 0)
  else:
    return (z.real(), z.imag())


def add_list_elts(ops):
  """Takes a list of operands, calls s_add on the operands and returns the result."""
  if(len(ops)==1):
    return ops[0]
  else:
    return s_add(ops[0], add_list_elts(ops[1::]))


def mult_list_elts(ops):
  """Takes a list of operands, calls s_mult on the operands and returns the result."""
  if(len(ops)==1):
    return ops[0]
  else:
    return s_mult(ops[0], mult_list_elts(ops[1::]))


def to_complex_tuples_expr(expr):
  """Takes an expression and returns it as an expression using complex tuples."""
  expr = sage.all.expand(expr)
  if("x" not in str(expr)): return to_complex_tuple(sym_expr.new_Expression(sage.all.SR, expr))

  def go(expr):
    ops = expr.operands()
    if len(ops) == 0:
        return to_complex_tuple(expr)
    for i in range(len(ops)):
      ops[i] = go(ops[i])

    res = None
    if expr.operator() == sage.symbolic.operators.mul_vararg:
      res = mult_list_elts(ops)
    if expr.operator() == sage.symbolic.operators.add_vararg:
      res = add_list_elts(ops)
    return res

  return go(expr)


def conj(z):
  """Takes a value z and returns its conjugate if z is not a variable x_i, otherwise it returns z."""
  if "x" in str(z):
    return z
  else:
    return sage.all.conjugate(z)


def s_add(x, y):
  """Takes two complex tuples and returns their sum as a complex tuple."""
  xr = x[0]
  xi = x[1]
  yr = y[0]
  yi = y[1]
  return (xr + yr, xi + yi)


def s_mult(x, y):
  """Takes two complex tuples and returns their product as a complex tuple."""
  xr = x[0]
  xi = x[1]
  yr = y[0]
  yi = y[1]
  return (xr * yr - xi * yi, xr * yi + xi * yr)


def s_eq(x, y):
  """
  Takes two 2-tuples.
  Returns a list of two Booleans where the nth value is True iff the nth component of x and y are equal, otherwise False.
  """
  return [x[0]==y[0], x[1]==y[1]]


def s_gr(x, y):
  """
  Takes two 2-tuples x and y.
  Returns True if the first component of x is greater than the first component of y, otherwise False.
  """
  if(x[1] != 0):
    print("value should be real")
    exit(-1)
  return (x[0] > y[0])


def coefficient_to_s_expr(coeff, var):
  """Takes a coefficient and variable name of a polynomial and returns it as an s-expression in form of a string."""
  exp = "1"
  if coeff[1] > 0:
    exp = "(* 1"
    for i in range(coeff[1]):
      exp += f" {var}"
    exp += ")"
  negative = False
  coeff_smt = coeff[0]
  if coeff[0] < 0:
    negative = True
    coeff_smt = abs(coeff[0])
  if not coeff[0].is_integer():
    fraction = str(coeff_smt).split("/")
    coeff_smt = f"(/ {fraction[0]} {fraction[1]})"
  if negative:
    return f"(* 1 (- {coeff_smt}) "+ exp +") "
  else:
    return f"(* 1 {coeff_smt} "+ exp + ") "


def polynomial_to_s_expr(pol, var):
  """Takes a polynomial and a variable name and returns the polynomial as an s-expression in form of a string."""
  res = "(+ 0 "
  coefficients = pol.coefficients()
  for c in coefficients:
    res += coefficient_to_s_expr(c, var)
  res += ")"
  return res


def num_to_s_expr(coeff):
  """Takes a value and returns it as an s-expression in form of a string."""
  negative = False
  coeff_smt = coeff
  if coeff_smt < 0:
    negative = True
    coeff_smt = abs(coeff_smt)
  if coeff_smt in sage.all.QQ:
    numerator, denominator = sage.all.QQ(coeff_smt).numerator(), sage.all.QQ(coeff_smt).denominator()
  else:
    denominator = 1
    numerator = sage.all.RR(coeff_smt).str(no_sci=2)
  abs_res = f"(/ {numerator} {denominator})"
  if negative:
    return f"(- {abs_res}) "
  else:
    return abs_res


def to_s_expr(exprList, operator):
  """Takes an expression list and an encoded arithmetic operator and returns these as an s-expression in form of a string."""
  res = "("
  match operator:
    case 0:
      res += "+ 0 "
    case 1:
      res += "-"
    case 2:
      res += "* 1 "
    case 3:
      res += "/"
  for e in exprList:
    res += " " + str(e)
  res += ")"
  return res


def get_str_arg_list(str):
  """
  Takes string of multiple values seperated by spaces.
  Returns list of values while respecting parentheses around values.
  E.g., '5 28 (+ 5 8)' -> ['5', '28', '(+ 5 8)']
  """
  start = 0
  parentheses_counter = 0
  arg_without_parantheses = False
  res = list()

  for i, char in enumerate(str):
    if char == '(':
      parentheses_counter += 1
      if (parentheses_counter == 1):
        start = i
    elif char == ')':
      parentheses_counter -= 1
      if (parentheses_counter == 0):
        res.append(str[start:i+1])
    elif char != ' ' and parentheses_counter == 0 and (str[i-1]==' ' or i==0):
      arg_without_parantheses = True
      start = i
    elif char == ' ' and parentheses_counter == 0 and arg_without_parantheses:
      res.append(str[start:i+1])
      arg_without_parantheses = False

  if (arg_without_parantheses):
    res.append(str[start:i+1])

  res = [arg.strip() for arg in res]
  return res


def s_expr_str_to_value(expr):
  """Takes an s-expression string and returns its corresponding value."""
  expr = expr.strip()
  if (not expr[0] == "("):
    if expr == "true":
      return True
    elif expr == "false":
      return False
    else:
      return eval("sage.all.QQbar("+expr+")")
  else:
    str_arg_list = get_str_arg_list(expr[1:-1])
    operator = str_arg_list[0]
    operands = [s_expr_str_to_value(x) for x in str_arg_list[1::]]

    value = 0
    match operator:
      case "+":
        for o in operands:
          value += o
      case "-":
        if len(operands) == 1:
          value = -operands[0]
        elif len(operands) > 1:
          value = operands[0]
          for o in operands[1:]:
            value -= o
      case "*":
        if len(operands) > 0: value = 1
        for o in operands:
          value *= o
      case "/":
        if len(operands) > 1:
          value = operands[0]
          for o in operands[1:]:
            value /= o
      case "^":
        if len(operands) > 1:
          value = operands[0]
          for o in operands[1:]:
            value = value ** o
  return value


def resolve_root_of_with_interval(val):
  """
  Takes a smtrat root-of-with-interval value and returns its value.
  A root-of-with-interval value has the form (root-of-with-interval (coeffs a_0 ... a_n) lower_bound upper_bound).
  E.g., (root-of-with-interval (coeffs (- 13) (- 14) 2) (/ 31 4) 8) -> 5/2*sqrt(3) + 7/2
  """
  root_obj_str_list = get_str_arg_list(val[1:-1]) # slicing to remove parentheses
  coeff_str_list = get_str_arg_list(root_obj_str_list[1][1:-1])

  # get polynomial
  x = sage.all.SR.var('x')
  polynomial = sym_expr.new_Expression(sage.all.SR, 0)
  for i, c in enumerate(coeff_str_list[1::]): # without first element "coeffs"
    coeff = s_expr_str_to_value(c)
    polynomial = sym_expr.new_Expression(sage.all.SR, polynomial + x**i * coeff)

  # get bounds
  lower_bound = s_expr_str_to_value(root_obj_str_list[2])
  upper_bound = s_expr_str_to_value(root_obj_str_list[3])

  # find root in interval
  res = None
  for r in polynomial.roots():
    if lower_bound <= r[0] <= upper_bound:
      res = r[0]

  if res == None:
    print("root object could not be resolved")
    exit(-1)

  return sage.all.QQbar(res)


def model_expression_to_value(expr):
  expr = expr.strip()
  """Takes a model value string and returns the corresponding value."""
  if "root-of-with-interval" in str(expr):
    return resolve_root_of_with_interval(expr)
  else:
    return s_expr_str_to_value(expr)


def mk_or(expr_list):
  """Takes a list of expressions and returns an s-expression as a string with logical or applied on expressions."""
  if len(expr_list) > 0:
    res = " (or"
    for e in expr_list:
      res += " " + str(e)
    res += ")"
    return res
  elif len(expr_list) == 1:
    return str(expr_list[0])
  else:
    return ""


def mk_and(expr_list):
  """Takes a list of expressions and returns an s-expression as a string with logical and applied on expressions."""
  if len(expr_list) > 0:
    res = " (and"
    for e in expr_list:
      res += " " + str(e)
    res += ")"
    return res
  elif len(expr_list) == 1:
    return str(expr_list[0])
  else:
    return ""
