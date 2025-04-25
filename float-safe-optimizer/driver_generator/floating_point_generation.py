from c_utils import sign_code

normal = "float val = (float)rand() / RAND_MAX;{sign_code}"
subnormal = "float val = (float)((rand() % 1000) * 1e-45);{sign_code}"
mixed = """float val;
    if (rand() % 2) {{
      val = (float)rand() / RAND_MAX;{sign_code}
    }} else {{
      val = (float)((rand() % 1000) * 1e-45);{sign_code}
    }}""" 
magnitude = """float exponent = (float)((rand() % 60) - 30);  // exponents from -30 to +30
float val = (float)((rand() % 1000) / 1000.0) * powf(10.0, exponent);{sign_code}"""

def get_float_value(type: str, include_negatives: bool) -> str:
  options = {
    "normal": normal,
    "subnormal": subnormal,
    "mixed": mixed,
    "magnitude": magnitude
  }
  return options[type].format(sign_code=sign_code(include_negatives))