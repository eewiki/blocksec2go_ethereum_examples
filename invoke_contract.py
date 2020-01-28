import blocksec2go
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from eth_account._utils.transactions import serializable_unsigned_transaction_from_dict, encode_transaction
import json
import sys

def get_reader():
	reader = None
	reader_name = '5422CL'
	while( reader == None ):
		try:
			reader = blocksec2go.find_reader( reader_name )
			print( 'Found the specified reader and a card!', end='\r' )
		except Exception as details:
			if( 'No reader found' == str( details ) ):
				print( 'No card reader found!     ', end='\r' )
			elif( 'No card on reader' == str( details ) ):
				print( 'Found reader, but no card!', end='\r' )
			else:
				print( 'ERROR: ' + str( details ) )
				raise SystemExit
	return reader

def activate_card(reader):
	try:
		blocksec2go.select_app( reader )
		print( 'Found the specified reader and a Blockchain Security 2Go card!' )
	except Exception as details:
		print( 'ERROR: ' + str( details ) )
		raise SystemExit
	
def get_public_key(reader, key_id):
	try:
		if( blocksec2go.is_key_valid( reader, key_id ) ):
			global_counter, counter, key = blocksec2go.get_key_info( reader, key_id )
			return key
		else:
			raise RuntimeError( 'Key_id is invalid!' )
	except Exception as details:
		print( 'ERROR: ' + str( details ) )
		raise SystemExit
	
def get_signature_components( der_encoded_signature ):
	# check signature lengthl
	if len( der_encoded_signature ) < 2:
		print( "Invalid signature!" )
		raise SystemExit
	# if does not start with signature DER TAG
	if not der_encoded_signature.startswith( b'\x30' ):
		print( "Invalid signature!" )
		raise SystemExit
	# get signature length
	sig_len = der_encoded_signature[1]
	if sig_len != len( der_encoded_signature[2:] ):
		print( "Signature length incorrect" )
		raise SystemExit
	
	pos = 2
	components = []
	while sig_len > 0:
		# if does not start with component DER TAG
		if der_encoded_signature[pos] != 0x02:
			print( "Expecting component DER TAG" )
			raise SystemExit
		pos += 1
		# get the component length
		component_len = der_encoded_signature[pos]
		pos += 1
		# get the component
		components.append( int.from_bytes( der_encoded_signature[pos:pos+component_len], byteorder='big' ) )
		pos += component_len
		sig_len = sig_len - component_len - 2
		
	return components
	
def get_signature_prefix( signature_rs, address, transaction_hash, chainId=-4 ):
	try: 
		r, s = signature_rs
	except:
		print( "Invalid signature argument!" )
		raise SystemExit()
		
	v = chainId * 2 + 35
	if w3.eth.account._recover_hash( bytes( transaction_hash ), vrs=( v, r, s ) ) != address:
		v = chainId * 2 + 36
		if w3.eth.account._recover_hash( bytes( transaction_hash ), vrs=( v, r, s ) ) != address:
			print( "Could not verify the signature" )
			raise SystemExit()
	
	return v

# check the command line arguments and print usage statement if incorrect
if len( sys.argv ) < 2:
	print( f"Usage: {sys.argv[0]} <new_message>" )
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

# derive and print address of an account on infineon card. Print account balance.
key_id = 1
reader = get_reader()
activate_card( reader )
public_key = get_public_key( reader, key_id )
inf_card_addr = w3.toChecksumAddress( w3.keccak( public_key[1:] )[-20:].hex() )
print( f'Address of account {key_id} on Infineon card: { inf_card_addr }' )
print( f'Balance of account {key_id} on Infineon card: { w3.fromWei( w3.eth.getBalance( inf_card_addr ), "ether" ) }' )
print()

# Set contract address and ABI
contract_address = "0xf7Bb1E956dC06C1804ec4788D5297BeB471a4397"
with open( 'solidity/helloworld_abi.json' ) as abi:
	contract_abi = json.load( abi )

# create the contract object for invocation
contract = w3.eth.contract( address=contract_address, abi=contract_abi )

# create the transaction dictionary for calling setMessage contract function
transaction = contract.functions.setMessage( sys.argv[1] ).buildTransaction( { 'nonce': w3.eth.getTransactionCount( inf_card_addr ), 'from': inf_card_addr } )
del transaction['from']

# serialize the transaction with the RLP encoding scheme
unsigned_encoded_transaction = serializable_unsigned_transaction_from_dict( transaction )

# sign the hash of the serialized transaction
global_counter, counter, signature = blocksec2go.generate_signature( reader, key_id, bytes( unsigned_encoded_transaction.hash() ) )
print( "Remaining signatures with card:", global_counter )
print( f"Remaining signatures with key {key_id}:", counter )
print( "Signature (hex):" + signature.hex() )
print()

# Extract r and s from the signature
try: 
	r, s = get_signature_components( signature )
except: 
	print( "Invalid signature components!" )
	raise SystemExit()
	
# determine the signature prefix value 
v = get_signature_prefix( ( r, s ), inf_card_addr, bytes( unsigned_encoded_transaction.hash() ), w3.eth.chainId )
		
# add the signature to the encoded transaction
signed_encoded_transaction = encode_transaction( unsigned_encoded_transaction, vrs=( v, r, s ) )

# send the signed, serialized transaction 
tx_hash = w3.eth.sendRawTransaction( signed_encoded_transaction )
print( "Updating message..." )

# wait for transaction to be included on a block
tx_receipt = w3.eth.waitForTransactionReceipt( tx_hash )
print()

# print account balance
print( f'Balance of account {key_id} on Infineon card: { w3.fromWei( w3.eth.getBalance( inf_card_addr ), "ether" ) }' )

# execute the getMessage() contract function and print the result 
message = contract.functions.getMessage().call()
print( "getMessage() returned:", f"\"{message}\"" )
print()
