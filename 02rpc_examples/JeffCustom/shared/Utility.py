import hashlib

BASE58_ALPHABET = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

def encode_base58(s):
    count = 0
    for c in s:
        if c == 0:
            count += 1
        else:
            break
    num = int.from_bytes(s, 'big')
    prefix = '1' * count
    result = ''
    while num > 0:
        num, mod = divmod(num, 58)
        result = BASE58_ALPHABET[mod] + result
    return prefix + result

def decode_base58(s):
    num = 0
    for c in s:         # get the number encoded in Base58 address
        num *= 58
        num += BASE58_ALPHABET.index(c)
    combined = num.to_bytes(25, byteorder='big')   # convert the number to big-endian bytes
    checksum = combined[-4:]
    if hash256(combined[:-4])[:4] != checksum:
        raise ValueError('bad address: {} {}'.format(checksum, hash256(combined[:-4])[:4]))
    return combined[1:-4]  #  first byte is the network prefix.  The last 4 are the checksum.  We care about the 20 in the middle.

def hash160(s):
    '''sha256 followed by ripemd160'''
    return hashlib.new('ripemd160', hashlib.sha256(s).digest()).digest()


def hash256(s):
    '''two rounds of sha256'''
    return hashlib.sha256(hashlib.sha256(s).digest()).digest()

def encode_base58_checksum(b):
    return encode_base58(b + hash256(b)[:4])

def little_endian_to_int(b):
    return int.from_bytes(b, 'little')

def int_to_little_endian(n, length):
    return n.to_bytes(length, 'little')

def read_varint(s):
    i = s.read(1)[0]
    if i == 0xfd:
        return little_endian_to_int(s.read(2))
    elif i == 0xfe:
        return little_endian_to_int(s.read(4))
    elif i == 0xff:
        return little_endian_to_int(s.read(8))
    else:
        return i


def encode_varint(i):
    if i < 0xfd:
        return bytes([i])
    elif i < 0x10000:
        return b'\xfd' + int_to_little_endian(i, 2)
    elif i < 0x100000000:
        return b'\xfe' + int_to_little_endian(i, 4)
    elif i < 0x10000000000000000:
        return b'\xff' + int_to_little_endian(i, 8)
    else:
        raise ValueError('integer too large: {}'.format(i))