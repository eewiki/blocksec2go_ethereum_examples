import blocksec2go
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

def get_reader():
  reader = None
  reader_name = '5422CL'
  while(reader == None):
    try:
      reader = blocksec2go.find_reader(reader_name)
      print('Found the specified reader and a card!', end='\r')
    except Exception as details:
      if('No reader found' == str(details)):
        print('No card reader found!     ', end='\r')
      elif('No card on reader' == str(details)):
        print('Found reader, but no card!', end='\r')
      else:
        print('ERROR: ' + str(details))
        raise SystemExit
  return reader

def activate_card(reader):
  try:
    blocksec2go.select_app(reader)
    print('Found the specified reader and a Blockchain Security 2Go card!')
  except Exception as details:
    print('ERROR: ' + str(details))
    raise SystemExit
	
def get_public_key(reader, key_id):
  try:
    if(blocksec2go.is_key_valid(reader, key_id)):
      global_counter, counter, key = blocksec2go.get_key_info(reader, key_id)
      return key
    else:
      raise RuntimeError('Key_id is invalid!')
  except Exception as details:
    print('ERROR: ' + str(details))
    raise SystemExit
	
# connect to the Ethereum node
w3 = Web3( HTTPProvider( "http://127.0.0.1:8501" ) ) 

# check for successful connection
if not w3.isConnected():
	print( "Unable to connect to Ethereum node" )
	raise SystemExit()
	
# inject the POA compatibility middleware to the innermost layer (not neccessary if using PoW)
# https://web3py.readthedocs.io/en/stable/middleware.html#geth-style-proof-of-authority
w3.middleware_onion.inject( geth_poa_middleware, layer=0 )

# print address and balance of first account on ethereum node
print( f'Address of account 0 on full node: { w3.eth.accounts[0] }' )
print( f'Balance of account 0 on full node: { w3.fromWei( w3.eth.getBalance( w3.eth.accounts[0] ), "ether" ) }' )
print()

# derive and print address of an account on infineon card. Print account balance.
key_id = 1 
reader = get_reader()
activate_card( reader )
public_key = get_public_key( reader, key_id )
inf_card_addr = w3.toChecksumAddress( w3.keccak( public_key[1:] )[-20:].hex() )
print( f'Address of account {key_id} on Infineon card: { inf_card_addr }' )
print( f'Balance of account {key_id} on Infineon card: { w3.fromWei( w3.eth.getBalance( inf_card_addr ), "ether" ) }' )
print()

# NOTE: 'gasPrice', 'gas', and 'chainId' are filled in automatically
# NOTE: 'from' is included so the sendTransaction function knows which private/public key pair to use. It will not be included on the block chain explicitly as it can be recovered from the signature.
tx_hash = w3.eth.sendTransaction( { 'from': w3.eth.accounts[0], 'to': inf_card_addr, 'value': w3.toWei( 10, 'ether' ) } )
print( "Sending 10 ether from full node account to Infineon card account..." ) 

# wait for transaction to be included on a block
tx_receipt = w3.eth.waitForTransactionReceipt( tx_hash )
print()

# print account balances
print( f'Balance of account 0 on full node: { w3.fromWei( w3.eth.getBalance( w3.eth.accounts[0] ), "ether" ) }' )
print( f'Balance of account {key_id} on Infineon card: { w3.fromWei( w3.eth.getBalance( inf_card_addr ), "ether" ) }' )
print()