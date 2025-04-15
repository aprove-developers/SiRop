import sage.all
import utils

def i_helper(a, b, p):
  """
  Takes two values a and b, and a probability p.
  Returns the value i, i.e. |a|^p / |b|^(p-1).
  """
  return abs(a) ** p * 1 / (abs(b) ** (p-1))


def o_helper(a, b):
  """
  Takes two values a and b.
  Returns the value o, i.e. |a| / |b|.
  """
  return abs(a) / abs(b)


def lex_p(tuplelist):
  """
  Takes a list of 2-tuples (i, o) and returns the sorted list according to lex_p,
  i.e. (i_1, o_1) <= (i_2, o_2) iff i_1 <= i_2 or (i_1 = i_2 and o_1 <= o_2).
  """
  l = tuplelist.copy()
  l.sort(key = lambda x: (x[0], x[1]))
  return l


def lex_n(tuplelist):
  """
  Takes a list of 2-tuples (i, o) and returns the sorted list according to lex_n,
  i.e. (i_1, o_1) <= (i_2, o_2) iff i_1 <= i_2 or (i_1 = i_2 and o_2 <= o_1).
  """
  l = tuplelist.copy()
  l.sort(key = lambda x: (x[0], -x[1]))
  return l


def get_max_p(tuplelist):
  """Takes a list of 2-tuples and returns their maximum according to lex_p."""
  return lex_p(tuplelist)[-1]


def get_max_n(tuplelist):
  """Takes a list of 2-tuples and returns their maximum according to lex_n."""
  return lex_n(tuplelist)[-1]


def get_constraint_term_groups(distinct_ev_pairs, p):
  """
  Takes a list of lists of eigenvectors [ev_a, ev_b] and a probability p.
  Returns a dictionary of the Constraint Term Groups with (i, o)-tuples as keys and lists of eigenvalue pairs as values.
  """
  ctg = dict()
  for evs in distinct_ev_pairs:
    i_temp = i_helper(evs[0], evs[1], p)
    o_temp = o_helper(evs[0], evs[1])
    io = (i_temp, o_temp)
    k = utils.get_helper(io, ctg)[0]
    if k == None:
      ctg[io] =  [(evs[0], evs[1])]
    else:
      ctg[k] =  list(ctg[k] + [(evs[0], evs[1])])
  return ctg


def is_positive_real(num):
  """Takes a number and returns True if it is a positive real, otherwise False."""
  return num>0 and num in sage.all.RR


def get_r_and_c_ctgs(ctg):
  """
  Takes a Constraint Term Groups dictionary.
  Returns one dictionary with all the positive real values and one dictionary with the other values.
  """
  rctg = dict()
  cctg = dict()
  for (i,o) in ctg.keys():
    rtemp, ctemp = [], []
    for v in ctg.get((i,o)):
      rtemp.append(v) if is_positive_real(v[0]) and is_positive_real(v[1]) else ctemp.append(v)
    if rtemp != []: rctg.update({(i,o): rtemp})
    if ctemp != []: cctg.update({(i,o): ctemp})
  return rctg, cctg
