#! /usr/bin/env sage
import sys
from sage.all import *
import sage.all
import sage.misc.persist
import simDiag
import constraintTermGroups
import solver
import nt_solver
import test
import argparse


def random_linear_termination(smtrat_cmd, c, a, b, probability = sage.all.QQ(1/2)):
  """
  Takes
    the command to invoke the solver,
    a matrix c representing a program,
    update matrices a and b,
    and a probability.
  Computes whether c is terminating.
  If not, an eventually nonterminating input and a nonterminating input are given.
  """
  # Compute dimensions and initialize x
  m, n = c.nrows(), c.ncols()
  entries_x = sage.all.SR.var(["x%s"%(i+1) for i in range(n)], domain='real')
  x = sage.all.Matrix(sage.all.SR, n, 1, lambda i, j: entries_x[i])

  p = probability

  # Check if matrices have correct dimensions
  if((a.nrows(), b.nrows(), a.ncols(), b.ncols()) != (n, n, n, n)):
    print("Invalid matrix dimensions")
    exit(-1)

  print("# C")
  print(c)
  print()

  print("# A")
  print(a)
  print()

  print("# B")
  print(b)
  print()

  # Simultaneously diagonalize a and b
  ti, a_d, b_d, t = simDiag.sim_diag(a, b)

  if (t == None):
    print("Matrices A and B both have to be simultaneously diagonalizable", file=sys.stderr)
    exit(-1)

  eigValsA = a_d.diagonal()
  eigValsB = b_d.diagonal()

  print("# Diagonalized A")
  print(a_d)
  print()

  print("# Diagonalized B")
  print(b_d)
  print()

  print("# Diagonal Transformation S")
  print(t)
  print()

  print("# S⁻¹")
  print(ti)
  print()

  print("# Gamma Mapping")
  gammas = {}

  matCT = c * t
  vecTix = ti * x

  for constraint_number in range(m):
    for i in range(n):
      existing_gamma = gammas.get((eigValsA[i], eigValsB[i], constraint_number))
      new_gamma = matCT[constraint_number][i] * vecTix[i][0]
      if existing_gamma == None:
        gammas.update({(eigValsA[i], eigValsB[i], constraint_number): new_gamma})
      else:
        gammas.update({(eigValsA[i], eigValsB[i], constraint_number): existing_gamma + new_gamma})
      print(f"gamma({constraint_number}, {i}) = {gammas[(eigValsA[i], eigValsB[i], constraint_number)]} (evs: {eigValsA[i], eigValsB[i]})")
  print()

  distinct_ev_pairs = []

  for i in range(n):
    if eigValsA[i] != 0 and eigValsB[i] != 0 and [eigValsA[i], eigValsB[i]] not in distinct_ev_pairs:
      distinct_ev_pairs.append([eigValsA[i], eigValsB[i]])

  # Compute constraint term groups
  ctg = constraintTermGroups.get_constraint_term_groups(distinct_ev_pairs, p)
  print("# Constraint Term Groups:")
  print(ctg)
  print()

  # Solve whether c is terminating. If not, print ENT
  rctg, cctg, groups, x_solved, d_p = solver.find_witness(smtrat_cmd, ctg, gammas, m, n, x)

  # Compute nonterminating input
  if d_p != None:
    nt = nt_solver.compute_nt(ctg, p, rctg, cctg, gammas, a, b, c, groups, x, x_solved, d_p)
    print()
    print("# Computed nonterminating input:")
    print(nt)
  print()


def get_input_from_file(path):
  """
  Takes a file path to a .sage file, loads its data.
  If provided in the file, it returns matrices c, a, b, and a probability p.
  """
  sage.misc.persist.load(f"{path}")
  if c == None or a == None or b == None or p == None:
    print("incomplete input")
    exit(-1)
  return c, a, b, p


def run(path, smtrat_cmd):
  """
  Takes the file path of the input file and the command to invoke the solver.
  Runs random_linear_termination.
  """
  c, a, b, p = get_input_from_file(path)
  random_linear_termination(smtrat_cmd, c, a, b, p)


def run_tests(smtrat_cmd):
  """
  Takes the command to invoke the solver.
  Runs the program tests.
  """
  amount_tests = test.get_amount_tests()
  for i in range(amount_tests):
    c, a, b, p = test.test(i)
    random_linear_termination(smtrat_cmd, c, a, b, p)


def main():
  """
  Main function.
  Handles arguments and calls according function.
  """
  parser = argparse.ArgumentParser()
  parser.add_argument("input", help="specify path to file with input data, e.g.\"input.sage\", or set it to \"tests\" to run the tests")
  parser.add_argument("--smtrat_cmd", nargs="?", type=str, help="specify the path to the smtrat binary", default="smtrat")

  args = parser.parse_args()

  if args.input == "tests":
    run_tests(args.smtrat_cmd)
  else:
    run(args.input, args.smtrat_cmd)


if __name__ == "__main__":
  main()
