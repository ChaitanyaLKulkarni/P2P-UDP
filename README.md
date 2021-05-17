# Peer to Peer Chat system using UDP

---

## Plan

-   Server

    -   [ ] Bind Server to static Port i.e. `55000`
    -   [ ] Listen for `$HELLO$` Msg
        -   If client is in clients list:
            -   [ ] Change last heartbeat to `t`
            -   [ ] Update expiry to `exp` i.e. `heartbeat`\*3
        -   If new client:
            -   [ ] Add it to the clients listen
                -   with name: that is at the after `$HELLO$`_name_
                -   `t` as current timestamp
            -   [ ] Send all clients in clients list to `new Client`

-   Clients
    -   [ ] Bind to random port in `45000-49000`
    -   [ ] Get _name_ and send it to Server in `$HELLO$`_name_
    -   [ ] Then listen for clients from server
    -   [ ] Start timer for heartbeat
        -   [ ] After `5` sec send heartbeat to server as well as all the current Clients
        -   [ ] If some clients go pass `exp` then remove them from clients list
    -   [ ] Send same `$HELLO$`_name_ to all Clients
    -   [ ] check if we get hello from Client
    -   [ ] Just send what ever we type to all in clients
