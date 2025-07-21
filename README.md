# PixTools Repository

A collection of utilities and tools for PixStor system administration, network visualization, and configuration management.

## Tools

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
