import blocksec2go
from web3 import Web3, HTTPProvider
	
# connect to the Ethereum node
w3 = Web3( HTTPProvider( "http://127.0.0.1:8501" ) ) 

# check for successful connection
if not w3.isConnected():
  print( "Unable to connect to Ethereum node" )
  raise SystemExit()

# get list of available readers
print( blocksec2go.readers() )
