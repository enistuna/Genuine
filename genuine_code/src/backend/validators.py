def validate_tckn(tckn: str) -> bool:
    if not tckn or len(tckn) != 11 or not tckn.isdigit():
        return False
    
    digits = [int(d) for d in tckn]
    
    if digits[0] == 0:
        return False

    odd = digits[0:9:2]
    even = digits[1:8:2]
    
    sum_odd = sum(odd)
    sum_even = sum(even)
    
    d10 = ((sum_odd * 7) - sum_even) % 10
    d11 = sum(digits[:10]) % 10
    
    return digits[9] == d10 and digits[10] == d11
