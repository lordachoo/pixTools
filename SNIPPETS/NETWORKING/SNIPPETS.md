# NETWORKING SNIPPETS

## Assign VLAN to Existing iface

```bash
$ nmcli con add type vlan con-name 100g5.1902 dev 100g5 id 1902 ip4 10.19.100.2/22 gw4 10.19.100.1
$ nmcli con reload
$ nmcli dev reapply 100g5.1902
```

## Change "NAME" in nmcli 

```bash
root@ladc-gw-04:~ # nmcli con show
NAME                UUID                                  TYPE      DEVICE
man0                b71161f4-869a-b108-a396-0c4d546ded38  ethernet  man0
backplane           8178f020-34a7-f35e-5248-7b236ab697a4  ethernet  backplane
Wired connection 1  cd368654-c232-38ce-ae6d-ad3ae117bdf2  ethernet  rdma0
Wired connection 2  924d02ec-961d-385b-a23c-56d8ef77a2ab  ethernet  rdma1
docker0             ce9d51c1-9b8d-40e1-900f-c3de3cdc1077  bridge    docker0
100g7               2ae2f343-9b86-3578-a774-80ca563b1f4f  ethernet  --
100g8               0aee57a4-fa82-370a-b2b0-799ed3b33491  ethernet  --
[Px] Staging mode     [Px]
 root@ladc-gw-04:~ # nmcli con mod cd368654-c232-38ce-ae6d-ad3ae117bdf2 connection.id rdma0
[Px] Staging mode     [Px]
 root@ladc-gw-04:~ # nmcli con mod 924d02ec-961d-385b-a23c-56d8ef77a2ab connection.id rdma1
[Px] Staging mode     [Px]
 root@ladc-gw-04:~ # nmcli con show
NAME       UUID                                  TYPE      DEVICE
man0       b71161f4-869a-b108-a396-0c4d546ded38  ethernet  man0
backplane  8178f020-34a7-f35e-5248-7b236ab697a4  ethernet  backplane
rdma0      cd368654-c232-38ce-ae6d-ad3ae117bdf2  ethernet  rdma0
rdma1      924d02ec-961d-385b-a23c-56d8ef77a2ab  ethernet  rdma1
docker0    ce9d51c1-9b8d-40e1-900f-c3de3cdc1077  bridge    docker0
100g7      2ae2f343-9b86-3578-a774-80ca563b1f4f  ethernet  --
100g8      0aee57a4-fa82-370a-b2b0-799ed3b33491  ethernet  --
```
