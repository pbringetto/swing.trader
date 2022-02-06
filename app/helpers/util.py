def is_integer_num(n):
     if isinstance(n, int):
         return True
     if isinstance(n, float):
         return n.is_integer()
     return False