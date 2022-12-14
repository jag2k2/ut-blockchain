from S256Point import S256Point, N, G

if __name__ == '__main__':
    msg_hash = 0xbc62d4b80d9e36da29c16c5d4d9f11731f36052c72401a76c23c0fb5a9b74423
    sig_r = 0x37206a0610995c58074999cb9767b87af4c4978db68c06e8e6e81d282047a7c6
    sig_s = 0x8ca63759c1157ebeaec0d03cecca119fc9a75bf8e6d0fa65c841c8e2738cdaec
    pub_x = 0x04519fac3d910ca7e7138f7013706f619fa8f033e6ec6e09370ea38cee6a7574
    pub_y = 0x82b51eab8c27c66e26c858a079bcdf4f1ada34cec420cafc7eac1a42216fb6c4
    
    public_key = S256Point(pub_x, pub_y)
    s_inv = pow(sig_s, N-2, N)
    u = msg_hash * s_inv % N
    v = sig_r * s_inv % N
    print((u*G + v*public_key).x.num == sig_r)