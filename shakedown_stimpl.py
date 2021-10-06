from stimpl import *

if __name__=='__main__':
  program = Program(Assign(Variable("i"), IntLiteral(1)), Variable("i"))
  run_stimpl(program)
