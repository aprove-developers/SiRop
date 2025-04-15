import sage.all
import sage.symbolic.expression as sym_expr
import constraintTermGroups
import subprocess
import itertools
import functools
import utils

fresh_index = 0
def get_fresh_index():
  """Returns an unused index each time it is called."""
  global fresh_index
  fresh_index += 1
  return fresh_index


def sum_rctgs_gammas(constraint_number, io, rctg, gammas):
  """
  Takes a constraint number, and io pair, an rctg dictionary and a dictionary containing the gamma mapping.
  Returns the sum of the gammas of eigenvalue pairs in rctg.
  """
  res = sym_expr.new_Expression(sage.all.SR, 0)
  key, val = utils.get_helper(io, rctg)
  if(key == None): return 0
  for evs in val:
    res += gammas[(evs[0], evs[1], constraint_number)]
  return res


def sum_cctgs_abs_gammas(constraint_number, io, cctg, gammas):
  """
  Takes a constraint number, and io pair, a cctg dictionary and a dictionary containing the gamma mapping.
  Returns the sum of the absolute gammas of eigenvalue pairs in cctg.
  """
  res = sym_expr.new_Expression(sage.all.SR, 0)
  key, val = utils.get_helper(io, cctg)
  if(key == None): return 0
  for evs in val:
    res += abs(gammas[(evs[0], evs[1], constraint_number)])
  return res


def c_eq_0_sum_2(constraint_number, io, cctg, gammas, la, lb):
  """
  Takes a constraint number, and io pair, a cctg dictionary, a dictionary containing the gamma mapping and two eigenvalues.
  Returns the sum of
    the sum of gammas of eigenvalue pairs in cctg whose zeta valus are equal,
    and the sum of the conjugate of gammas of eigenvalue pairs in cctg whose zeta values are each others conjugate.
  """
  z_ia = utils.zeta(la)
  z_ib = utils.zeta(lb)
  res = sym_expr.new_Expression(sage.all.SR, 0)
  key, val = utils.get_helper(io, cctg)
  if (key == None): return 0
  for evs in val:
    if (utils.zeta(evs[0]) == z_ia and utils.zeta(evs[1]) == z_ib):
      res += gammas[(evs[0], evs[1], constraint_number)]
    if (utils.zeta(evs[0]) == sage.all.conjugate(z_ia) and utils.zeta(evs[1]) == sage.all.conjugate(z_ib)):
      res += utils.conj(gammas[(evs[0], evs[1], constraint_number)])
  return res


def c_eq_0(constraint_number, io, rctg, cctg, gammas):
  """
  Takes a constraint number, an io pair, an rctg dictionary, a cctg dictionary and a dictionary containing the gamma mapping.
  Returns the constraints belonging to C=0.
  """
  key, val = utils.get_helper(io, cctg)
  if(val != None): l = len(val)
  else: l = 0
  constraints = [0] * (2*(1 + l))
  tempConstr = utils.s_eq(utils.to_complex_tuples_expr(sum_rctgs_gammas(constraint_number, io, rctg, gammas)), (0,0))

  # Constraint that rctgs sum to 0
  constraints[0] = tempConstr[0]
  constraints[1] = tempConstr[1]

  # Constraints that cctgs sum to 0
  for k in range(2, 2*(l+1), 2):
    la = val[int(k/2-1)][0]
    lb = val[int(k/2-1)][1]
    tempConstr = utils.s_eq(utils.to_complex_tuples_expr(c_eq_0_sum_2(constraint_number, io, cctg, gammas, la, lb)), (0,0))
    constraints[k] = tempConstr[0]
    constraints[k+1] = tempConstr[1]
  return constraints


def c_gr_0_helper(constraint_number, io, cctg, gammas):
  """
  Takes a constraint number, an io pair, a cctg dictionary and a dictionary containing the gamma mapping.
  Returns a list of the gammas of eigenvalue pairs in cctg.
  """
  res = []
  key, val = utils.get_helper(io, cctg)
  if(key == None): return []
  for evs in val:
    gamma = gammas[(evs[0], evs[1], constraint_number)]
    res.append(gamma)
  return res


def c_gr_0(constraint_number, io, io_index, rctg, cctg, gammas):
  """
  Takes a constraint number, and io pair, a constraint tuple index, an rctg dictionary,
  a cctg dictionary, and a dictionary containing the gamma mapping.
  Returns the constraints belonging to C>0, a list of variable names that need to be declared, and a list of assertions.
  """
  left_side = sum_rctgs_gammas(constraint_number, io, rctg, gammas)
  if utils.to_complex_tuples_expr(left_side)[1] != 0:
    print("value should be real")
    exit(-1)
  addends = c_gr_0_helper(constraint_number, io, cctg, gammas)
  constraint = ""
  addend_string = " 0"
  declarations = []
  assertions = []
  left_side, declarations_temp, assertions_temp = expr_to_s_expr(left_side)
  declarations += declarations_temp
  assertions += assertions_temp

  if addends!=[]:
    for i in range(len(addends)):
      declarations.append(f"abs_{constraint_number}_{io_index}_{i+1}")
      assertions.append(f"(assert (>= abs_{constraint_number}_{io_index}_{i+1} 0))\n")

      z_re, declarations_temp, assertions_temp = expr_to_s_expr(addends[i].real_part())
      declarations += declarations_temp
      assertions += assertions_temp

      z_im, declarations_temp, assertions_temp = expr_to_s_expr(addends[i].imag_part())
      declarations += declarations_temp
      assertions += assertions_temp

      constraint += f" (= (* abs_{constraint_number}_{io_index}_{i+1} abs_{constraint_number}_{io_index}_{i+1}) (+ (* {z_re} {z_re}) (* {z_im} {z_im})))"
      addend_string += f" abs_{constraint_number}_{io_index}_{i+1}"
    constraint += f" (> {left_side} (+{addend_string}))"
  else: constraint =  f" (> {left_side} 0)"

  return constraint, declarations, assertions


def encode_value(coeff):
  """
  Takes a value and returns its assigned variable name, a list of variable names that need to be declared, and a list of assertions.
  """
  if "x" in str(coeff) or "g" in str(coeff):
    return str(coeff), [], []
  else:
    index = get_fresh_index()
    declarations = [f"c{index}"]

    minpoly = sym_expr.new_Expression(sage.all.SR, sage.all.QQbar(coeff).minpoly())

    assertions = ["(assert (= "+ utils.polynomial_to_s_expr(minpoly, f"c{index}") + " 0))"+"\n"]

    roots = [root for (root, _) in minpoly.roots(ring=sage.all.QQbar)]
    roots.sort()
    n = roots.index(coeff)

    equations = list()

    for i in range(len(roots)):
        declarations.append(f"c{index}i{i}")
        equations.append("(= "+ utils.polynomial_to_s_expr(minpoly, f"c{index}i{i}") + " 0)")

    equations += [f"(< c{index}i{i} c{index}i{i+1})" for i in range(len(roots)-1)]
    equations.append(f"(= c{index}i{n} c{index})")
    assertions.append(f"(assert{utils.mk_and(equations)})\n")

    return f"c{index}", declarations, assertions


def expr_to_s_expr(expr):
  """Takes a sub-expression. Returns the expression as an s-expression in form of a string, a list of variable names that need to be declared, and a list of assertions."""
  expr = sym_expr.new_Expression(sage.all.SR, expr)
  expr.simplify()
  if expr == 0:
    return str(0), [], []

  # dummy_var is used to aid with simplification (makes sure outer operand is addition)
  # Hence we get a sum of multiplications
  dummy_var = sage.all.var("dummy_var")

  expr = expr.add(dummy_var)
  expr = expr.expand()
  expr_list = expr.operands()
  expr_list.remove(dummy_var)
  ops = expr_list

  declarations = []
  assertions = []

  for i in range(len(ops)):
    m_ops = ops[i].operands()
    if len(m_ops) == 0:
      ops[i], declarations_temp, assertions_temp = encode_value(ops[i])
      declarations += declarations_temp
      assertions += assertions_temp
      continue
    for j in range(len(m_ops)):
      m_ops[j], declarations_temp, assertions_temp = encode_value(m_ops[j])
      declarations += declarations_temp
      assertions += assertions_temp
    if len(m_ops) > 1: ops[i] = utils.to_s_expr(m_ops, 2)
    else: ops[i] = m_ops
  if len(ops) > 1: res = utils.to_s_expr(ops, 0)
  else: res = ops[0]
  return res, declarations, assertions


def bool_expr_to_s_expr(expr):
  """Takes a boolean expression. Returns the expression as an s-expression in form of a string, a list of variable names that need to be declared, and a list of assertions."""
  if expr == True:
    return "true", [], []
  if expr == False:
    return "false", [], []

  res = "("

  # operator
  if "==" in str(expr):
    res += "="
  elif ">=" in str(expr):
    res += ">="
  elif "<=" in str(expr):
    res += "<="
  elif ">" in str(expr):
    res += ">"
  elif "<" in str(expr):
    res += "<"
  else:
    print("Unexpected operator in constraint")
    exit(-1)

  declarations = []
  assertions = []

  # left side of equation
  left_side, declarations_temp, assertions_temp = expr_to_s_expr(expr.left())
  res += " " + left_side
  declarations += declarations_temp
  assertions += assertions_temp

  # right side of equation
  right_side, declarations_temp, assertions_temp = expr_to_s_expr(expr.right())
  res += " " + right_side
  declarations += declarations_temp
  assertions += assertions_temp

  res += ")"
  return res, declarations, assertions


def both_dirs(f):
  """Takes a function and calls it with the correct filehandles."""
  functools.partial(f)(fh = smt_file_p)
  functools.partial(f)(fh = smt_file_n)


def declare_real_var(name, fh):
  """Takes a string and a filehandle and writes a Real variable declaration named by the string to according file."""
  fh.write(f"(declare-const {name} Real)\n")


def declare_bool_var(name, fh):
  """Takes a string and a filehandle and writes a Bool variable declaration named by the string to according file."""
  fh.write(f"(declare-const {name} Bool)\n")


def write_to_file(text, fh):
  """Takes a string and a filehandle and writes string to according file."""
  fh.write(text)


def find_witness(smtrat_cmd, ctg, gammas, m, n, x):
  """
  Takes
    the command to invoke the solver,
    a Constraint Term Group dictionary,
    a dictionary containting the gamma mapping,
    dimensions m and n,
    a vector x containing variables x_i.
  Returns
    a R (real positive) Constraint Term Group dictionary,
    a C (not R) Constraint Term Group dictionary,
    a list of dominating groups,
    a vector of the assigned value for each x_i,
    a boolean (or None if loop is terminating) indicating whether loop does not terminate for d=p (True) or d=n (False) .
  """
  global smt_file_p, smt_file_n, fresh_index

  rctg, cctg = constraintTermGroups.get_r_and_c_ctgs(ctg)
  s = list(ctg.keys())
  print("s", s)
  print("rctg", rctg)
  print("cctg", cctg)
  print()

  lexP = constraintTermGroups.lex_p(s)
  lexN = constraintTermGroups.lex_n(s)

  # create smt_file_p and smt_file_n
  smt_file_name_p = "proof_obligation_p"
  smt_file_p = open(f"{smt_file_name_p}.smt2", "w")
  smt_file_p.write("(set-option :produce-assignments true)\n")
  smt_file_p.write("(set-option :produce-models true)\n")
  smt_file_p.write("(set-logic QF_NRA)\n")

  smt_file_name_n = "proof_obligation_n"
  smt_file_n = open(f"{smt_file_name_n}.smt2", "w")
  smt_file_n.write("(set-option :produce-assignments true)\n")
  smt_file_n.write("(set-option :produce-models true)\n")
  smt_file_n.write("(set-logic QF_NRA)\n")

  print(f"smt2 filenames: {smt_file_name_p}, {smt_file_name_n}")
  print()

  # declare variables in smt_files
  for i in range(x.nrows()):
    both_dirs(functools.partial(declare_real_var, f"x{i+1}"))

  constraint_tuples = [c_f for c_f in itertools.product(s, repeat = m)]
  for i in range(len(constraint_tuples)):
    both_dirs(functools.partial(declare_bool_var, f"b{i+1}"))

  # add main constraints to smt_files
  for i in range(len(constraint_tuples)):
    constraint_list = list()
    for constraint_number in range(m):
      constraint, declarations, assertions = c_gr_0(constraint_number, constraint_tuples[i][constraint_number], i, rctg, cctg, gammas)
      for declaration in declarations: declare_real_var(declaration, smt_file_p)
      for assertion in assertions: smt_file_p.write(assertion)
      constraint_list.append(constraint)
      for io2 in s:
        # check if io2 is greater than constraint_tuples[i][constraint_number] regarding the order lex_p
        if lexP.index(io2) > lexP.index(constraint_tuples[i][constraint_number]):
          for e in c_eq_0(constraint_number, io2, rctg, cctg, gammas):
            constraint, declarations, assertions = bool_expr_to_s_expr(e)
            for declaration in declarations: declare_real_var(declaration, smt_file_p)
            for assertion in assertions: smt_file_p.write(assertion)
            constraint_list.append(constraint)
    smt_file_p.write(f"(assert (= b{i+1} {utils.mk_and(constraint_list)}))\n")

  for i in range(len(constraint_tuples)):
    constraint_list = list()
    for constraint_number in range(m):
      constraint, declarations, assertions = c_gr_0(constraint_number, constraint_tuples[i][constraint_number], i, rctg, cctg, gammas)
      for declaration in declarations: declare_real_var(declaration, smt_file_n)
      for assertion in assertions: smt_file_n.write(assertion)
      constraint_list.append(constraint)
      for io2 in s:
        # check if io2 is greater than constraint_tuples[i][constraint_number] regarding the order lex_n
        if lexN.index(io2) > lexN.index(constraint_tuples[i][constraint_number]):
          for e in c_eq_0(constraint_number, io2, rctg, cctg, gammas):
            constraint, declarations, assertions = bool_expr_to_s_expr(e)
            for declaration in declarations: declare_real_var(declaration, smt_file_n)
            for assertion in assertions: smt_file_n.write(assertion)
            constraint_list.append(constraint)
    smt_file_n.write(f"(assert (= b{i+1} {utils.mk_and(constraint_list)}))\n")

  constraint_tuples_list = [f"b{k+1}" for k in range(len(constraint_tuples))]
  both_dirs(functools.partial(write_to_file, f"(assert{utils.mk_or(constraint_tuples_list)})\n"))

  both_dirs(functools.partial(write_to_file, "(check-sat)\n"))

  both_dirs(functools.partial(write_to_file, f"(get-model)\n"))

  smt_file_p.close()
  smt_file_n.close()

  out_p = None
  out_n = None

  class NotSatException(Exception):
    """Raised if solver's exit code is not 2."""
    pass

  try:
    res_p = subprocess.run(f"{smtrat_cmd} {smt_file_name_p}.smt2", shell = True, capture_output = True)
    if res_p.returncode != 2: # not sat
      raise NotSatException()
    else:
      out_p = res_p.stdout.decode("UTF-8")
  except NotSatException:
    if res_p.returncode != 3:
      print(f"Subprocess exited with returncode {res_p.returncode}")
      exit(-1)

  try:
    res_n = subprocess.run(f"{smtrat_cmd} {smt_file_name_n}.smt2", shell = True, capture_output = True)
    if res_n.returncode != 2: # not sat
      raise NotSatException()
    else:
      out_n = res_n.stdout.decode("UTF-8")
  except NotSatException:
    if res_n.returncode != 3:
      print(f"Subprocess exited with returncode {res_n.returncode}")
      exit(-1)


  # output if unsat
  if (out_p == None and out_n == None):
    print("# The loop is terminating.")
    return None, None, None, None, None
  # output if sat
  else:
    print("# The loop is nonterminating.")
    print()

    if out_p != None:
      print("d=p")
      out = out_p.split("\n")
    else:
      print("d=n")
      out = out_n.split("\n")

    x_solved_entries = [0]*x.nrows()
    for i in range(x.nrows()):
      filtered = list(filter(lambda y: (f"(define-fun x{i+1}") in y, out))
      if len(filtered) > 0:
        index = out.index(filtered[0])+1
        x_solved_entries[i] = utils.model_expression_to_value(out[index])
    x_solved = sage.all.Matrix(sage.all.SR, n, 1, lambda i, j: x_solved_entries[i])

    print("# Computed eventually nonterminating input:")
    print(x_solved)
    print()


    b_solved_list = [0]*len(constraint_tuples)
    for i in range(len(constraint_tuples)):
      filtered = list(filter(lambda y: (f"(define-fun b{i+1}") in y, out))
      if len(filtered) > 0:
        index = out.index(filtered[0])+1
        b_solved_list[i] = utils.model_expression_to_value(out[index])

    group_index = None
    for i in range(len(b_solved_list)):
      if b_solved_list[i] == True:
        group_index = i
        break
    if group_index == None:
      print("no group could be found")
      exit(-1)
    groups = constraint_tuples[group_index]

    d_p = (out_p != None)
    return rctg, cctg, groups, x_solved, d_p
