


def int_to_bin(a):
    res = []
    while a > 0:
        a,mod = divmod(a,2)
        res.append(str(mod))
    return int(''.join(res))

def bin_to_int(a):
    n = len(str(a))
    a = list(map(int, str(a)))
    res = 0
    for idx in range(n-1, -1, -1):
        res += a[idx] * (2**idx)
    return res

def net_mask(a,b):
    a = int_to_bin(a)
    b = int_to_bin(b)
    net_mask = a & b 
    return bin_to_int(net_mask)


if __name__ == "__main__":
    res = int_to_bin(127)
    print('binary:', res)
    res = bin_to_int(res)
    print('decimal:', res)
