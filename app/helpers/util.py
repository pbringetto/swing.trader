def is_integer_num(n):
     if isinstance(n, int):
         return True
     if isinstance(n, float):
         return n.is_integer()
     return False

def convert_dict_vals_to_float(d):
    for k, v in d.items():
        d[k] = float(v) if v.isdigit() else v
    return d