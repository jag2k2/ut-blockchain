from PrivateKey import PrivateKey
from S256Point import S256Point

if __name__ == '__main__':
    print(PrivateKey(5002).wif(True, True))
    print(PrivateKey(2020**5).wif(False, True))
    print(PrivateKey(0x12345deadbeef).wif(True, False))