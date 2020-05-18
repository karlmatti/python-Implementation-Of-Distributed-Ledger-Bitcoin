# P2P custom bitcoin app

## How to run?
run multiple MyCustomServer.py scripts with a port argument
For example:
In windows: MyCustomServer.py 6000
In mac: python MyCustomServer.py 6000

## Protocol: HTTP
## Servers communicate each other via TCP sending HTTP requests

## How it works?
### Servers synchronize available peers
1. After running server.py script, it creates peers-PORT.json file cloning the peers-default.json file which contains default peers that are usually running.
2. Server is listening /getpeers requests. If peer who is requesting is not in peers-PORT.json then it is added there.
3. Server is sending /getpeers to peers in peers-PORT.json. Server is going through response and adds new peers to peers-PORT.json.
### Servers can listen money requests
1. Ask money from server - POST request to /money with body:
{
  "to": "your-public-key",
  "sum": 2
}
### Servers can handle bitcoin blocks
1. Server listens HTTP GET request /getblocks where it returns all blocks from blocks-PORT.json file.
2. Server listens HTTP GET request /getblocks?id=BLOCK_ID where it returns all blocks since BLOCK_ID from blocks-PORT.json file.
3. Server listens HTTP GET request /getdata?id=BLOCK_ID where it returns a single block with BLOCK_ID as id from blocks-PORT.json file.
4. Server listens HTTP POST request /block with block data in json and adds it to blocks-PORT.json when it does not exist and will send it to all the peers known by the server. 
If the block exists then it will not send blocks to others and returns error message in json: {"errcode": 400, "errmsg": "Block already exists"}.
### Servers can handle bitcoin transactions
1. Server listens HTTP POST request /inv with transaction data in and adds it to blocks-PORT.json when it does not exist and will send it to all the peers known by the server. 
If the transaction exists then it will not send blocks to others and returns error message in json: {"errcode": 400, "errmsg": "Transaction already exists"}.
2. If server has enough transactions (variable n_transactions) then server starts to put together a block. Adds 1 bitcoin transaction to itself and calculates its nonce till hash has four zeros in the beginning. Also merkle root is calculated.


Example of transaction:
{"signature": "f7f0b9c45b93db7e70443e233cbca80fb42e59799719305284067a21a34e9ac669914671f8c3f6d213ead08223acb4bf",
"transaction": {"from": "d4a21b835c33ae3a853125d646837326a9faa543f866af13d02609b3de21c9706e37797569269eabe75dd0334da12e9f",
"to": "7709eab4a64db09ea6b3794618df49d636d9809bd998227cc7c184e7e237669c413aaf6a13ab48e354b8f220e69a1093",
"sum": 0.8,
"timestamp": "2020-05-14T09:19:10.338111"}}

Example of genesis block:
{"nr": 0,"previous_hash": "","timestamp": "01/01/2009","nonce": "VDEODFTZ041jHIZuIyEY",
"hash": "00008c26fa89c80d23ce0b98afb3bff429f828253c008b562ca8599606cb60e3","creator": "Satoshi Nakamoto",
"merkle_root": "563826313bf3d6ae2fc191f05f3eb08b60a3fb50704e8a89c4e0827ed663fdfb","count": 1,
"transactions": [
{"signature": "System",
"transaction": {"from": "System","to": "Satoshi Nakamoto","sum": 50,"timestamp": "01/01/2009"}}]}

