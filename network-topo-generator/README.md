# Network Topology Generator

A Python utility for generating visual network topology diagrams from switch interface data.

## Overview

Network Topology Generator creates interactive visualizations of network connections by parsing switch interface information. It produces SVG, HTML, PNG, PDF, and CSV outputs to help network administrators understand and document their network infrastructure.

## Features

- **Interactive Mode**: Guided prompts for easy configuration
- **Batch Processing**: Process multiple switch files at once
- **Multiple Output Formats**:
  - SVG (default, always generated)
  - HTML with embedded SVG (always generated)
  - PNG (optional)
  - PDF (optional)
  - CSV link table (optional)
- **Visual Customization**:
  - Dark/Light mode
  - Site/rack grouping
  - Color-coded connection status
- **Auto Browser Launch**: Automatically opens the generated HTML diagram

## Requirements

- Python 3.x
- Graphviz (must be installed on your system)
  - Download from: https://graphviz.org/download/

## Installation

1. Ensure Python 3.x is installed
2. Install Graphviz on your system
3. Install required Python packages:

```bash
pip install graphviz
```

## Usage

### Command Line Arguments

```bash
python network-topo-generator.py [options]
```

Options:
- `--dark`: Enable dark mode
- `--group`: Group nodes by site/rack prefix
- `--batch`: Process all *.txt files in the current directory
- `--pdf`: Generate PDF output
- `--png`: Generate PNG output
- `--csv`: Generate CSV link table

### Interactive Mode

If no command line arguments are provided, the script will run in interactive mode, prompting for:

1. Dark mode preference
2. Grouping preference
3. Batch processing preference
4. Output format preferences
5. Switch data input (paste or file processing)
6. Base filename for outputs

### Input Format

The script expects switch interface data in a tabular format similar to:

```
Interface  Admin  Oper  Speed  MTU  Type  Remote Host  Remote Port
Eth1/1     up     up    10G    1500  eth   switch2      Eth2/1
Eth1/2     up     down  1G     1500  eth   
```

For batch processing, place each switch's interface data in a separate .txt file. The filename (without extension) will be used as the switch name.

## Output Files

For a base name of "network_topology":

- `network_topology`: SVG file
- `network_topology.html`: HTML file with embedded SVG
- `network_topology_png`: PNG file (if enabled)
- `network_topology_pdf`: PDF file (if enabled)
- `network_topology.csv`: CSV link table (if enabled)

## Example

```bash
# Run with all options enabled
python network-topo-generator.py --dark --group --batch --pdf --png --csv

# Run in interactive mode
python network-topo-generator.py
```

## Visualization Features

- Nodes represent switches and interfaces
- Edges represent connections between devices
- Green nodes indicate "up" interfaces
- Red nodes indicate "down" interfaces
- Dashed boxes represent remote endpoints
- When grouped, nodes are clustered by site/rack prefix

## Version

Current version: v13
