import constraintTermGroups
import solver
import math
import utils


def scaling_factor(eps, i_max, i_max2, o_max, o_max_prime):
  """Takes values eps, i_max, i_max2, o_max and o_max_prime and returns the corresponding scaling factor."""
  return ((i_max2 * o_max_prime**eps)/(i_max * o_max**eps))


def find_second_largest_pairs(keys, i_max, o_max, d_p):
  """
  Takes a list keys which are io pairs, values i_max and o_max and the boolean d_p.
  Returns both second largest pairs in keys.
  """
  first_pair = [0, 0]
  first_pair[0] = max([0]+[i for (i, o) in keys if i < i_max])
  first_pair[1] = max([o for (i, o) in keys])

  second_pair = [i_max, 0]
  if d_p:
    second_pair[1] = max([0]+[o for (i, o) in keys if i == i_max and o < o_max])
  elif not d_p:
    o_list = [o for (i, o) in keys if i == i_max and o > o_max]
    if len(o_list) == 0: second_pair[1] = 0
    else: second_pair[1] = min(o_list)

  return first_pair, second_pair


def find_eps(curr_eps, i_max, i_max2, o_max, o_max_prime, d_p):
  """
  Takes a current value for epsilon, values for i_max, i_max2, o_max, o_max_prime and the boolean d_p.
  Recursively computes and returns epsilon.
  """
  s = None
  if d_p:
    s = scaling_factor(curr_eps, i_max, i_max2, o_max, o_max_prime)
  else:
    s = scaling_factor(-curr_eps, i_max, i_max2, o_max, o_max_prime)
  if s>=1:
    return find_eps(curr_eps/2, i_max, i_max2, o_max, o_max_prime, d_p)
  else:
    return curr_eps


def find_r(r, t, o_max, o_max2, concrete_summed_gammas, d_p):
  """
  Takes a current r, t, o_max, o_max2, a sum of absolute values of gammas and the boolean d_p.
  Recursively computes and returns r.
  """
  if o_max2 == 0: return 0
  if d_p:
    val1, val2 = o_max, o_max2
  else:
    val1, val2 = 1 / o_max, 1 / o_max2
  if t * val1**r > val2**r * concrete_summed_gammas:
    return r
  else:
    return find_r(r*2, t, o_max, o_max2, concrete_summed_gammas, d_p)


def substitute_solved_into_x(term, x, x_solved):
  """
  Takes a term, a vector of variables and a vector of their assigned values.
  Substitues the variables with their assigned values and returns the resulting term.
  """
  for i in range(x_solved.nrows()):
    term = term.subs(x[i][0] == x_solved[i][0])
  return term


def compute_constants(p, rctg, cctg, ctg, gammas, group, x, x_solved, d_p, s, constraint_number):
  """
  Takes
    a probability,
    an rctg dictionary,
    a cctg dictionary,
    a Constraint Term Group dictionary,
    a dictionary containting the gamma mapping,
    a dominating group,
    a vector x containing variables x_i,
    a vector x_solved containting the assigned values to each x_i,
    the boolean d_p,
    the list s of io pairs,
    and a constraint number.
  Returns the constants epsilon, r and l for the constraint number.
  """
  eps, r, l = None, None, None

  firstPair, secondPair = find_second_largest_pairs(s, group[0], group[1], d_p)

  # epsilon
  eps = find_eps(min(p, 1-p), group[0], firstPair[0], group[1], firstPair[1], d_p)

  # rho
  rho = solver.sum_rctgs_gammas(constraint_number, group, rctg, gammas) - solver.sum_cctgs_abs_gammas(constraint_number, group, cctg, gammas)
  rho = substitute_solved_into_x(rho, x, x_solved)
  if rho <= 0:
    print("Error: rho out of range")
    exit(-1)

  # r
  t = rho / 2 # choose t = rho / 2
  summed_gammas = sum_gammas_abs_all_io(gammas, ctg, constraint_number)
  concrete_summed_gammas = substitute_solved_into_x(summed_gammas, x, x_solved)
  r = find_r(1, t, group[1], secondPair[1], concrete_summed_gammas, d_p)

  # l
  if d_p:
    sf = scaling_factor(eps, group[0], firstPair[0], group[1], firstPair[1])
  else:
    sf = scaling_factor(-eps, group[0], firstPair[0], group[1], firstPair[1])
  l = 1
  while rho - t - sf**l * concrete_summed_gammas <= 0:
    l *= 2

  return eps, r, l


def sum_gammas_abs_all_io(gammas, ctg, constraint_number):
  """
  Takes a dictionary containting the gamma mapping, a ctg dictionary and a constraint number.
  Returns the sum of gammas of eigenvalues belonging to the constraint number in the ctg over all io pairs.
  """
  res = 0
  for k in ctg.keys():
    res += sum_gammas_abs(gammas, ctg, k, constraint_number)
  return res

def sum_gammas_abs(gammas, ctg, io, constraint_number):
  """
  Takes a dictionary containting the gamma mapping, a ctg dictionary, an io pair and a constraint number.
  Returns the sum of absolute values of gammas of eigenvalues belonging to the io pair and the constraint number in the ctg.
  """
  res = 0
  key, value = utils.get_helper(io, ctg)
  for ev_pair in value:
    res += abs(gammas[(ev_pair[0], ev_pair[1], constraint_number)])
  return res

def sum_gammas(gammas, ctg, io, constraint_number):
  """
  Takes a dictionary containting the gamma mapping, a ctg dictionary, an io pair and a constraint number.
  Returns the sum of gammas of eigenvalues belonging to the io pair and the constraint number in the ctg.
  """
  res = 0
  key, value = utils.get_helper(io, ctg)
  for ev_pair in value:
    res += gammas[(ev_pair[0], ev_pair[1], constraint_number)]
  return res


def compute_nt(ctg, p, rctg, cctg, gammas, a, b, c, groups, x, x_solved, d_p):
  """
  Takes
    a Constraint Term Group dictionary,
    a probability,
    an rctg dictionary,
    a cctg dictionary,
    a dictionary containting the gamma mapping,
    the two update matrices a and b,
    a matrix c,
    a list of dominating groups,
    a vector x containing variables x_i,
    a vector x_solved containting the assigned values to each x_i.
  Returns a nonterminating input.
  """
  eps, r, l = {}, {}, {}

  if d_p:
    lex = constraintTermGroups.lex_p(list(ctg.keys()))
  else:
    lex = constraintTermGroups.lex_n(list(ctg.keys()))

  for constraint_number in range(c.nrows()):
    s = list()
    for io in ctg.keys():
      if substitute_solved_into_x(sum_gammas(gammas, ctg, io, constraint_number), x, x_solved) != 0:
        s.append(io)


    res = compute_constants(p, rctg, cctg, ctg, gammas, groups[constraint_number], x, x_solved, d_p, s, constraint_number)
    eps[constraint_number], r[constraint_number], l[constraint_number] = res

  eps_c = min(eps.values())
  r_c = max(r.values())
  l_c = max(l.values())

  print("Constants:", "eps =", eps_c, ", r =", r_c, ", l =",l_c)

  while eps_c * l_c < r_c + 2:
    l_c *= 2

  if d_p:
    f_a = math.ceil(r_c + p * l_c)
  elif not d_p:
    f_a = math.floor(p * l_c - r_c)

  f_b = l_c - f_a
  print("f_A =",f_a,", f_B =",f_b)

  nt = a**f_a * b**f_b * x_solved

  return nt
