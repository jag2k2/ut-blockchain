import json, requests, uuid

from .hash   import hash160
from .helper import decode_address
from lib.encoder import encode_tx

from shared.Tx import TxIn, TxOut
from shared.Utility import decode_base58
from shared.Script import Script

class RpcSocket:
    ''' Basic implementation of a JSON-RPC interface. '''
    def __init__(self, opt):
        #url  = opt.get('url', '127.0.0.1')
        url = opt.get('url', '169.254.122.179')  # for running in wsl
        #port = opt.get('port', 18443)
        port = opt.get('port', 18332)

        self.fullUrl  = f'http://{url}:{port}/'
        self.username = opt.get('username', 'jag2k2')
        self.password = opt.get('password', 'jeff1229')
        self.wallet   = opt.get('wallet', None)
        self.initFlag = False

    def init(self):
        ''' Initialize the RPC object. '''
        if self.wallet:
            self.loadWallet()
            self.fullUrl += f'wallet/{self.wallet}'
        

    def call(self, method, args = []):
        ''' Make an RPC call using the 
            specified method and arguments.
        '''
        # Make sure to initialize the RPC object first.
        if not self.initFlag:
            self.initFlag = True
            self.init()
        
        # Format the arguments before the call.
        args = args if type(args) is list else [ args ]

        # Construct the body of the reuqest.
        body = json.dumps({
            "jsonrpc": "1.0",
            "id": uuid.uuid4().urn.split(':')[-1],
            "method": method,
            "params": args
        })
        
        # Make the request to the server.
        response = requests.post(
            self.fullUrl,
            auth=(self.username, self.password),
            data=body
        )
        #print('done posted')

        # If the response code is not 200, fail here.
        if response.status_code != 200:
            raise Exception(f'Response failed with error: {response.status_code}')
        
        data = response.json()
        
        # If the data includes an error message, fail here.
        if data['error']:
            if data['error']['code'] == -1:
                raise Exception(f'RPC command {method} failed with syntax error. Please check your arguments.')
            else:
                err_msg = data["error"]["message"]
                raise Exception(f'RPC command {method} failed with error: {err_msg}')
        
        return data['result']

    def check(self):
        res = self.call('getblockchaininfo')
        return 'chain' in res


    def isWalletLoaded(self):
        wallets = self.call('listwallets')
        return self.wallet in wallets


    def isWalletExists(self):
        wallets = self.call('listwalletdir')
        return [ w['name'] for w in wallets['wallets'] if w['name'] == self.wallet ]

    
    def loadWallet(self):
        if self.isWalletLoaded():
            return True
        if not self.isWalletExists():
            raise f'Wallet "{self.wallet}" does not exist!'

        result = self.call('loadwallet', [ self.wallet ])

        if result['warning'] or result['name'] != self.wallet:
            raise 'Wallet failed to load cleanly: {}'.format(result['warning'])
        
        return True

    def get_all_utxos(self):
        all_utxos = []
        unspent_json = self.call('listunspent')
        for utxo in unspent_json:
            prev_tx = bytes.fromhex(utxo['txid'])
            vout = int(utxo['vout'])
            all_utxos.append(TxIn(prev_tx, vout))
        return all_utxos

    def get_total_unspent_sats(self):
        amount = 0.0
        unspent_json = self.call('listunspent')
        for utxo in unspent_json:
            amount += float(utxo['amount'])
        return int(amount * 100000000)

    def get_txout(self, amount):
        address = self.call('getnewaddress', ['', 'legacy'])
        #address = 'mnRsJs2nBBqMwb9jjUjxyht2meynnuLsF4'
        target_h160 = decode_base58(address)
        target_script = Script.p2pkh_script(target_h160)
        return TxOut(amount, target_script)

    def get_private_key(self, tx_id, tx_index):
        transaction = self.call('gettransaction', tx_id)
        details = transaction['details']
        for detail in details:
            if int(detail['vout']) == tx_index: 
                encoded_key = self.call('dumpprivkey', detail['address'])
        return decode_address(encoded_key)

    # def get_recv(self, address=None, fmt='bech32'):
    #     if address is None:
    #         if fmt == 'base58':
    #             address = self.call('getnewaddress', ['-format', 'legacy'])
    #         else:
    #             address = self.call('getnewaddress')
    #     encoded_key = self.call('dumpprivkey', address)
    #     public_key  = self.call('getaddressinfo', address)['pubkey']
    #     pubkey_hash = hash160(public_key).hex()
    #     return {
    #         'address': address,
    #         'priv_key': decode_address(encoded_key),
    #         'pub_key': public_key,
    #         'pubkey_hash': pubkey_hash,
    #         'redeem_script': f'1976a914{pubkey_hash}88ac',
    #     }

    def send_transaction(self, transaction):
        raw_tx = transaction.serialize().hex()
        self.call('sendrawtransaction', raw_tx)
        return transaction.id()
