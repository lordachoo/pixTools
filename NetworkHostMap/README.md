# Network Host Map

A utility for generating comprehensive network interface to physical slot mapping tables for PixStor servers.

## Overview

The Network Host Map tool creates detailed mappings between physical server NIC slots, their hardware identifiers (FQDD), MAC addresses, and corresponding Linux interfaces. It can optionally query network switches to identify which switch ports each NIC is connected to, making it particularly useful for MLAG configurations.

## Features

- Maps physical NIC slots to Linux interface names
- Shows hardware details from racadm (FQDD, MAC address)
- Displays interface status (UP/DOWN)
- Identifies alternative interface names
- Optional switch port mapping with MLAG awareness
- Automatic traffic generation to help identify inactive interfaces
- Summarizes NIC card types and port counts

## Requirements

- `racadm` command-line utility
- `ip` command
- SSH access to switches (optional, for switch port mapping)

## Usage

Basic usage:

```bash
./network-host-map
```

With options:

```bash
./network-host-map [options] [hostname]
```

### Options

- `-s, --switches IP1,IP2`: Comma-separated switch IPs for port mapping
- `-u, --user USERNAME`: Switch SSH username (default: admin)
- `-h, --help`: Show help

### Examples

Generate mapping for the local host:

```bash
./network-host-map
```

Generate mapping with switch port information:

```bash
./network-host-map -s 10.0.0.1,10.0.0.2
```

Generate mapping for a specific host with custom switch user:

```bash
./network-host-map -s 10.0.0.1,10.0.0.2 -u switchadmin PIXSTOR01
```

## Output

The tool generates a formatted table with the following columns:

- Physical Slot: Human-readable slot and port identifier
- RACADM FQDD: Dell hardware identifier
- MAC Address: NIC MAC address
- Linux Interface: Corresponding Linux interface name
- Status: Interface status (UP/DOWN)
- Switch Port(s): Connected switch ports (when using -s option)

Additionally, it provides a summary of card types and port counts.

## Troubleshooting

If no NIC data is found, verify that racadm is working:

```bash
racadm hwinventory | grep -A 5 'NIC\.'
```
