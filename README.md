# Peer to Peer Chat system using UDP

---

## Plan

-   Server

    -   [x] Bind Server to static Port i.e. `55000`
    -   [x] Listen for `$HELLO$` Msg
        -   If client is in clients list:
            -   [x] Change last heartbeat to `t`
            -   [x] Update expiry to `exp` i.e. `heartbeat`\*3
        -   If new client:
            -   [x] Add it to the clients listen
                -   with name: that is at the after `$HELLO$`_name_
                -   `t` as current timestamp
            -   [x] Send all clients in clients list to `new Client`

-   Clients
    -   [x] Bind to random port in `45000-49000`
    -   [x] Get _name_ and send it to Server in `$HELLO$`_name_
    -   [x] Then listen for clients from server
    -   [x] Start timer for heartbeat
        -   [x] After `5` sec send heartbeat to server as well as all the current Clients
        -   [x] If some clients go pass `exp` then remove them from clients list
    -   [x] Send same `$HELLO$`_name_ to all Clients
    -   [x] check if we get hello from Client
    -   [x] Just send what ever we type to all in clients
