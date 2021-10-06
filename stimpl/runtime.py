from . import *

"""
Interpreter State
"""
class State(object):
  def __init__(self):
    self.state = {}
    pass

  def set_value(self, variable_name, variable_value, variable_type):
    new_state = State()
    for k, v in self.state.items():
      new_state.state[k] = v

    new_state.state[variable_name] = (variable_value, variable_type)
    return new_state


  def get_value(self, variable_name):
    try:
      return self.state[variable_name]
    except KeyError:
      return None

  def __repr__(self):
    result = ""
    for k, v in self.state.items():
      result += f"\n{k}: {v}"
    return result

"""
Main evaluation logic!
"""
def evaluate(expression, state):
  match expression:
    case Ren():
      return (None, Unit(), state)

    case IntLiteral(literal=l):
      return (l, Integer(), state)

    case FloatingPointLiteral(literal=l):
      return (l, FloatingPoint(), state)

    case StringLiteral(literal=l):
      return (l, String(), state)

    case BooleanLiteral(literal=l):
      return (l, Boolean(), state)

    case Print(to_print=to_print):
      printable_value, printable_type, new_state = evaluate(to_print, state)

      if isinstance(printable_type,Unit):
        print("Unit")
      else:
        print(f"{printable_value}")

      return (printable_value, printable_type, new_state)

    case Variable(variable_name=variable_name):
      value = state.get_value(variable_name)
      if value == None:
        raise InterpSyntaxError(f"Cannot read from {variable_name} before assignment.")
      return (*value, state)

    case Sequence(exprs = exprs) | Program(exprs = exprs):
      new_state = state
      
      # Iterating through all statement of sequence to get the 2 properties of a expression and the program's state
      for e in exprs:
          value_res, value_type, new_state = evaluate(e, new_state)
      return (value_res, value_type, new_state) 

    case Assign(variable=variable, value=value):

      value_result, value_type, new_state = evaluate(value, state)

      variable_from_state = new_state.get_value(variable.variable_name)
      _, variable_type = variable_from_state if variable_from_state else (None, None)

      if value_type != variable_type and variable_type != None:
        raise InterpTypeError(f"""Mismatched types for Assignment: 
            Cannot assign {value_type} to {variable_type}""")

      new_state = new_state.set_value(variable.variable_name, value_result, value_type)
      return (value_result, value_type, new_state)

    case Add(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Add: 
            Cannot add {left_type} to {right_type}""")
      
      match left_type:
        case Integer() | String() | FloatingPoint():
          result = left_result + right_result
        case _:
          raise InterpTypeError(f"""Cannot add {left_type}s""")

      return (result, left_type, new_state)

    case Subtract(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Subtract: 
            Cannot subtract {left_type} to {right_type}""")
            
      match left_type: # upper condition allows no checking for both vars
        case Integer() | FloatingPoint(): # semantic .6
          result = left_result - right_result
        case _:
          raise InterpTypeError(f"""Cannot subtract {left_type}s""")   
      
      return (result, left_type, new_state)   

    case Multiply(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Multiply: 
            Cannot Multiply {left_type} with {right_type}""")
            
      match left_type: # upper condition allows no checking for both vars
        case Integer() | FloatingPoint(): # semantic .6
          result = left_result * right_result
        case _:
          raise InterpTypeError(f"""Cannot multiply {left_type}s""") 
          
      return (result, left_type, new_state) 

    case Divide(left=left, right=right):
      result = 0
      left_result, left_type, new_state = evaluate(left, state)
      right_result, right_type, new_state = evaluate(right, new_state)
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Divide: 
            Cannot divide {left_type} to {right_type}""")
            
      match left_type: # upper condition allows no checking for both vars
        case Integer() : # semantic .6 NOTE
          result = left_result // right_result
        case FloatingPoint(): # semantic .6
          result = left_result / right_result
        case _:
          raise InterpTypeError(f"""Cannot divide {left_type}s""") 
          
      return (result, left_type, new_state) 

    case And(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for And: 
            Cannot have and for {left_type} and {right_type}""")
      match left_type:
        case Boolean():
          result = left_value and right_value
        case _:
          raise InterpTypeError("Cannot perform logical and on non-boolean operands.")
 
      return (result, left_type, new_state)

    case Or(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Or: 
            Cannot have or for {left_type} and {right_type}""")
      match left_type:
        case Boolean(): # semantic .5
          result = left_value or right_value
        case _:
          raise InterpTypeError("Cannot perform logical and on non-boolean operands.")
 
      return (result, left_type, new_state)

    case Not(expr=expr):
      value, value_type, new_state = evaluate(expr, state)
      
      # not binary operator, so don't need to check for Rule 3
      
      match value_type:
        case Boolean(): # semantic .5
          result = not value
        case _:
          raise InterpTypeError("Cannot perform logical or on non-boolean operands.")
          
      return (result, value_type, new_state)
      

    case If(condition=condition, true=true, false=false):
      value, value_type, new_state = evaluate(condition, state)
      
      match value_type:
        case Boolean(): # Runtime type Rule 8
          if value: # semantic .11
            result, value_type, new_state = evaluate(true, new_state)
          else: # semantic .11
            result, value_type, new_state = evaluate(false, new_state)
        case _:
          raise InterpTypeError("Cannot perform logical if on non-boolean operands.")
          
      return (result, value_type, new_state)

    case Lt(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None

      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Lt: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value < right_value
        case Unit():
          result = False
        case _:
          raise InterpTypeError(f"Cannot perform < on {left_type} type.")

      return (result, Boolean(), new_state)

    case Lte(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Lte: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value <= right_value
        case Unit():
          result = True # semantic .4
        case _:
          raise InterpTypeError(f"Cannot perform <= on {left_type} type.")

      return (result, Boolean(), new_state)

    case Gt(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Gt: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value > right_value
        case Unit():
          result = False 
        case _:
          raise InterpTypeError(f"Cannot perform > on {left_type} type.")

      return (result, Boolean(), new_state)

    case Gte(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Gte: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value >= right_value
        case Unit():
          result = True # semantic .4
        case _:
          raise InterpTypeError(f"Cannot perform >= on {left_type} type.")

      return (result, Boolean(), new_state)

    case Eq(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Eq: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value <= right_value
        case Unit():
          result = True # semantic .4
        case _:
          raise InterpTypeError(f"Cannot perform == on {left_type} type.")

      return (result, Boolean(), new_state)

    case Ne(left=left, right=right):
      left_value, left_type, new_state = evaluate(left, state)
      right_value, right_type, new_state = evaluate(right, new_state)

      result = None
      
      # Runtime type Rule 3
      if left_type != right_type:
        raise InterpTypeError(f"""Mismatched types for Ne: 
            Cannot compare {left_type} to {right_type}""")

      match left_type:
        case Integer() | Boolean() | String() | FloatingPoint():
          result = left_value != right_value
        case Unit():
          result = False
        case _:
          raise InterpTypeError(f"Cannot perform != on {left_type} type.")

      return (result, Boolean(), new_state)

    case While(condition=condition, body=body):
      cond_value, cond_type, new_state = evaluate(condition, state)
      
      # not binary operator, so don't need to check for Rule 3
      
      match cond_type:
        case Boolean(): # Runtime type Rule 8
          while cond_value:
            result, value_type, new_state = evaluate(body, new_state)
            cond_value, cond_type, new_state = evaluate(condition, new_state) # evaluate next state/new state, then loop again
          return (result, value_type, new_state)
        case _:
            raise InterpTypeError("Cannot perform while loop on non-boolean operands.")
	  
      return (False, Boolean(), new_state)
      
    case _:
      raise InterpSyntaxError("Unhandled!")
  pass

def run_stimpl(program, debug=False):
  state = State()
  program_value, program_type, program_state = evaluate(program, state)

  if debug:
    print(f"program: {program}")
    print(f"final_value: ({program_value}, {program_type})")
    print(f"final_state: {program_state}")

  return program_value, program_type, program_state
