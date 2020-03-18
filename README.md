# P2P bitcoin app

## How to run?
run the server.py script with a port argument
For example:
In windows: server.py 6000
In mac: python server.py 6000

## Protocol: Bitcoin
## Servers communicate each other via TCP sending HTTP requests

## How it works?
### Servers synchronize available peers
1. After running server.py script, it creates peers-<PORT>.json file cloning the peers-default.json file which contains default peers that are usually running.
2. Server is listening /getpeers?port=<PORT> requests. If peer who is requesting is not in peers-<PORT>.json then it is added there.
3. Server is sending /getpeers?port=<PORT> to peers in peers-<PORT>.json. Server is goint through response and adds new peers to peers-<PORT>.json.
### Servers can handle bitcoin blocks
1. Server listens HTTP GET request /getblocks?port=<PORT> where it returns all blocks from blocks-<PORT>.json file.
2. Server listens HTTP GET request /getblocks?port=<PORT>&id=<BLOCK_ID> where it returns all blocks since <BLOCK_ID> from blocks-<PORT>.json file.
3. Server listens HTTP GET request /getdata?port=<PORT>&id=<BLOCK_ID> where it returns a single block with <BLOCK_ID> as id from blocks-<PORT>.json file.
4. Server listens HTTP POST request /block with block data in json and adds it to blocks-<PORT>.json when it does not exist and will send it to all the peers known by the server. 
If the block exists then it will not send blocks to others and returns error message in json: {"errcode": 400, "errmsg": "Block already exists"}.
### Servers can handle bitcoin transactions
1. Server listens HTTP POST request /inv with transaction data in and adds it to blocks-<PORT>.json when it does not exist and will send it to all the peers known by the server. 
If the transaction exists then it will not send blocks to others and returns error message in json: {"errcode": 400, "errmsg": "Transaction already exists"}.
