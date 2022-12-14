from shared.Tx import SIGHASH_ALL, Tx, TxIn, TxOut
from shared.Utility import decode_base58, little_endian_to_int, hash256
from shared.Script import Script
from shared.PrivateKey import PrivateKey

if __name__ == '__main__':
    passphrase1 = b'jeff.tipps@utexas.edu my secret'
    secret1 = little_endian_to_int(hash256(passphrase1))
    private_key1 = PrivateKey(secret1)
    testnet_address = private_key1.public_key.address(testnet=True)
    print(testnet_address + ": " + decode_base58(testnet_address).hex())  # mhyswzw7rLN8ij8e8DCFVgydb2Rt5pdJ3t

    passphrase2 = b'jeff.tipps@utexas.edu practice address'
    secret2 = little_endian_to_int(hash256(passphrase2))
    private_key2 = PrivateKey(secret2)
    practice_address = private_key2.public_key.address(testnet=True)
    print(practice_address + ": " + decode_base58(practice_address).hex()) # miTVw9CvEPnQ4Z4ZTTFQ1jm4X47PqYghgB

    passphrase3 = b'jeff.tipps@utexas.edu change address'
    secret3 = little_endian_to_int(hash256(passphrase3))
    private_key3 = PrivateKey(secret3)
    change_address = private_key3.public_key.address(testnet=True)
    print(change_address + ": " + decode_base58(change_address).hex()) # mpd4shwkfpDyNiNgDAm4G6u1jZiiT6F8iU
    
    amount = 0.0005
    sats_per_btc = 100000000
    funding_tx_from_testnet = 'b2186a8fd2adaff0172e27fe28c6bd060a5a3583a167c3563001b8d06bb4baa5'
    prev_tx = bytes.fromhex(funding_tx_from_testnet)
    prev_index = 1
    tx_in = TxIn(prev_tx, prev_index)
       
    target_amount = int(amount * sats_per_btc * 0.6)
    target_h160 = decode_base58('miTVw9CvEPnQ4Z4ZTTFQ1jm4X47PqYghgB')
    target_script = Script.p2pkh_script(target_h160)
    target_output = TxOut(target_amount, target_script)

    change_amount = int(amount * sats_per_btc * 0.3)  # number of satoshi
    change_h160 = decode_base58('mpd4shwkfpDyNiNgDAm4G6u1jZiiT6F8iU')
    change_script = Script.p2pkh_script(change_h160)
    change_output = TxOut(change_amount, change_script)

    tx_obj = Tx(1, [tx_in], [target_output, change_output], 0, True)
   
    print(tx_obj)

    z = tx_obj.sig_hash(0)
    tx_obj.sign_input(0, private_key1)
    
    print(tx_obj)
    print("tx_id: " + tx_obj.id())
    print(tx_obj.serialize().hex())

    # tx_id: 68ac91b864a2e833e8acb272db0be68e5bde52d346366a94762eb38350a83eba