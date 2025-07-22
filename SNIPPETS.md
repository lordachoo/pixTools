# CODE SNIPPETS

## Build idrac/man0 hostfile entries

```bash
for i in $(mmlscluster | grep -E '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | awk '{print $3}' ); do ssh $i "/opt/dell/srvadmin/sbin/racadm get idrac.ipv4 | grep -i address " | sed 's/.*=//' >> hostfile_idrac.txt; ssh $i hostname >> hostfile_idrac.txt; done; sed -i "N;s/\n/ /" hostfile_idrac.txt; sed -i "s/\([^[:space:]]*\)[[:space:]]*$/\1-idrac.pixstor \1-idrac/" hostfile_idrac.txt

for i in $(mmlscluster | grep -E '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | awk '{print $3}' ); do ssh $i "ip -br -4 a | grep man" | awk '{print $3}' | sed 's/.\{3\}$//' >> hostfile_man.txt; ssh $i hostname >> hostfile_man.txt; done; sed -i "N;s/\n/ /" hostfile_man.txt ;sed -i "s/\([^[:space:]]*\)[[:space:]]*$/\1-man0.pixstor \1-man0/" hostfile_man.txt

# Example:

cat hostfile_* >> /etc/hosts 
```

## NVME Re-Connect (Without Disconnecting Existing Drives)

```bash
nvme list -v  | sed -n '/Express\ Controllers/,/Express\ Namespaces/p' | grep rdma| awk '{ if (!$11) {print $1} }' | xargs -I % bash -c 'nvme disconnect -d %' ; nvme connect-all
```
