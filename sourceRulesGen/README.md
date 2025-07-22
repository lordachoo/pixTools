# Source Rules Generator

A bash utility script for generating source-based routing rules for network interfaces using NetworkManager.

## Overview

This tool automatically generates NetworkManager CLI commands to set up source-based routing rules for multiple network interfaces. It extracts the actual IP addresses and subnet information from the interfaces and creates appropriate routing rules and routes.

## Features

- Automatically detects IP addresses and subnet masks from existing interfaces
- Generates appropriate routing table entries based on interface configuration
- Supports exactly 2 or 4 interfaces as required by the routing configuration
- Calculates network addresses from interface CIDR notation
- Outputs ready-to-use NetworkManager CLI commands

## Usage

```bash
./source_rules_gen.sh -I <interfaces>
```

### Parameters

- `-I <interfaces>`: Comma-separated list of interfaces (must be exactly 2 or 4)
  - Example: `-I 100g1,100g2,100g3,100g4`

### Example

```bash
./source_rules_gen.sh -I 100g1,100g2,100g3,100g4
```

This will generate output similar to:

```
nmcli con mod 100g1 +ipv4.routing-rules "priority 10 from 10.19.191.26 table 1001"
nmcli con mod 100g1 +ipv4.routes "10.19.191.0/24 table=1001"
nmcli con mod 100g2 +ipv4.routing-rules "priority 10 from 10.19.191.27 table 1002"
nmcli con mod 100g2 +ipv4.routes "10.19.191.0/24 table=1002"
nmcli con mod 100g3 +ipv4.routing-rules "priority 10 from 10.19.191.5 table 1003"
nmcli con mod 100g3 +ipv4.routes "10.19.191.0/24 table=1003"
nmcli con mod 100g4 +ipv4.routing-rules "priority 10 from 10.19.191.25 table 1004"
nmcli con mod 100g4 +ipv4.routes "10.19.191.0/24 table=1004"
nmcli con reload
nmcli dev reapply 100g1
nmcli dev reapply 100g2
nmcli dev reapply 100g3
nmcli dev reapply 100g4
```

## Implementation Details

The script performs the following operations:

1. Validates that exactly 2 or 4 interfaces are provided
2. For each interface:
   - Extracts the IP address and CIDR notation using `ip -4 addr show`
   - Calculates the network address based on the IP and subnet mask
   - Assigns a unique routing table number (1001, 1002, etc.)
3. Generates NetworkManager commands to:
   - Add source-based routing rules
   - Add routes to the appropriate routing tables
   - Reload connections and reapply device configurations

## Notes

- The script only prints the commands and does not execute them
- You can redirect the output to a file or pipe it to bash to execute the commands
- Requires root privileges to execute the generated commands
