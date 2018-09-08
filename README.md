[http://cs.berry.edu/~nhamid/p2p/](http://cs.berry.edu/~nhamid/p2p/)

#### BTPeer class

Define the attributes and main event handle logic for a peer.

##### 1. Attributes：
* `_my_id`: string
* `server_host`: string
* `server_port`: int
* `peers`: list
* `max_peers`: int

Functions:
* `my_id`: get & set _my_id
* `add_peer`, `get_peer`, `remove_peer`, `add_peer_at`, `get_peer_at`, `remove_peer_at`, `get_all_peers`, `peer_nums`: operate on peers list
* `max_peers_reached`: max_peers


##### 2. Peer logic：
* `shut_down`: bool
* `handlers`: list
* `router`

Functions:
* `main_loop`: Listen connections on the server port, dispatch them to `_handle_peer`.
* `_handle_peer`: Dispatch requests to different API function according to message types.
* `send_to_peer`: Send message to the identified peer.
* `connect_and_send`: Connect to peers and wait for reply
* `check_live_peers`: Delete offline peers.

#### BTPeerConnection class

Encapsulates sockets, pack/unpack/chunk messages, catch exceptions

Attributes:

`id`, `sock`

Connection logic:

`make_msg`, `send_data`, `recv_data`, `close`





