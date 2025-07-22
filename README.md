# PixTools Repository

A collection of utilities and tools for PixStor system administration, network visualization, and configuration management.

## Tools

### [Code Snippets](SNIPPETS.md)

A collection of useful code snippets for PixStor administration tasks, including building idrac/man0 hostfile entries and NVME reconnection commands without disconnecting existing drives.

### [Network Topology Generator](network-topo-generator/README.md)

A Python utility for generating visual network topology diagrams from switch interface data. Creates interactive visualizations of network connections by parsing switch interface information, producing SVG, HTML, PNG, PDF, and CSV outputs.

### [PixStor BIOS Configuration](pixstor-bios-conf/README.md)

Script for setting DELL iDRAC BIOS Configuration payloads for different PixStor configurations. Automates the process of configuring server BIOS settings to match PixStor requirements.

### [SaltState Visualizer](saltStateViz/README.md)

Python3-based SaltStack visualization application that creates ASCII or PNG/SVG visualizations of PixStor Salt States. Helps administrators understand complex Salt state relationships and dependencies (requires GraphViz for visual outputs).

### [setROCEPrio](setROCEPrio/README.md)

A utility script for configuring RDMA over Converged Ethernet (RoCE) priority settings on Mellanox network interfaces. Optimizes network performance for PixStor environments by setting appropriate priority masks and LLDP/DCBX parameters.

### [NetworkHostMap](NetworkHostMap/README.md)

A utility for generating comprehensive network interface to physical slot mapping tables for PixStor servers. Maps physical NIC slots to Linux interfaces and optionally identifies switch port connections with MLAG awareness. ** VERY EXPERIMENTAL AS OF 7/21/2025 **

### [Source Based Routing Rules Generator](sourceRulesGen/README.md)

A bash utility for generating source-based routing rules for network interfaces. Automatically extracts IP addresses and subnet information from interfaces and creates appropriate NetworkManager routing rules and routes for multi-homed configurations.

## Included Submodules

### [rdmaPerfMon](https://github.com/lordachoo/rdmaPerfMon)

A performance monitoring tool for RDMA (Remote Direct Memory Access) interfaces. Provides real-time statistics and metrics for RDMA connections, helping to diagnose performance issues and optimize network configurations for high-performance storage systems.

## Installation

To clone this repository with all submodules:

```bash
git clone --recursive https://github.com/lordachoo/pixTools.git
```

If you've already cloned the repository without the `--recursive` flag, you can fetch the submodules with:

```bash
git submodule update --init --recursive
```
