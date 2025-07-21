# setROCEPrio

A utility script for configuring RDMA over Converged Ethernet (RoCE) priority settings on Mellanox network interfaces.

## Overview

This script configures RoCE priority and related settings on Mellanox network interfaces using the `mstconfig` utility. It sets the appropriate priority mask, threshold values, and LLDP/DCBX parameters for optimal RoCE performance in PixStor environments.

## Usage

```bash
./setROCEPrio <PCI_ID1> [PCI_ID2] [PCI_ID3] ...
```

### Example

```bash
./setROCEPrio 37:00.0 37:00.1 8b:00.0 8b:00.1
```

## Prerequisites

- `mstconfig` utility (part of Mellanox OFED)
- `lshw` utility for hardware information

## Finding PCI IDs

The script will display Mellanox network interfaces when run. You can also find the PCI IDs manually:

```bash
lshw -c network | grep Mellanox -A 3 -B 3
```

## Configuration Applied

The script applies the following settings to both P1 and P2 ports:

- `ROCE_CC_PRIO_MASK`: Set to 8 (priority 3)
- `RPG_THRESHOLD`: Set to 1
- `DCE_TCP_G`: Set to 1019
- `LLDP_NB_DCBX`: Enabled (TRUE)
- `LLDP_NB_TX_MODE` and `LLDP_NB_RX_MODE`: Set to 2

These settings optimize the network interfaces for RoCE traffic in PixStor environments.
