from shared.Utility import decode_base58
from shared.Tx import Tx
from io import BytesIO

if __name__ == '__main__':
    raw_tx = ('0100000001813f79011acb80925dfe69b3def355fe914bd1d96a3f5f71bf830\
3c6a989c7d1000000006b483045022100ed81ff192e75a3fd2304004dcadb746fa5e24c5031ccf\
cf21320b0277457c98f02207a986d955c6e0cb35d446a89d3f56100f4d7f67801c31967743a9c8\
e10615bed01210349fc4e631e3624a545de3f89f5d8684c7b8138bd94bdd531d2e213bf016b278\
afeffffff02a135ef01000000001976a914bc3b654dca7e56b04dca18f2566cdaf02e8d9ada88a\
c99c39800000000001976a9141c4bc762dd5423e332166702cb75f40df79fea1288ac19430600')
    stream = BytesIO(bytes.fromhex(raw_tx))
    transaction = Tx.parse(stream)
    print(transaction.id())
    print(transaction.fee())
    print(transaction.sig_hash(0))

    print(transaction.verify_input(0))
    print(transaction.verify())

    print(decode_base58('mzx5YhAH9kNHtcN481u6WkjeHjYtVeKVh2').hex())