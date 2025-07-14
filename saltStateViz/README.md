# SaltStack State Visualizer

A Python script that parses SaltStack states and generates visualizations (ASCII or graphical SVG) showing the relationships between states, roles, systemd units, role dependencies, and pillar dependencies.

## Features

- Identifies all states that can be applied as a whole (directories with `init.sls` files)
- Parses state files to extract:
  - Roles defined in each state
  - Role dependencies (roles used in conditional blocks)
  - Pillar dependencies (pillars accessed via `salt.pillar.get`)
  - Systemd units controlled by each state (with enhanced detection)
  - Dependencies between states (via include statements)
- Multiple visualization formats:
  - ASCII diagram for quick terminal viewing
  - Graphical SVG output using Graphviz (with color-coded nodes and edges)

## Requirements

- Python 3.6+
- PyYAML (`pip install pyyaml`)
- Graphviz (optional, for graphical output)
  - Python package: `pip install graphviz`
  - System binaries: 
    - Ubuntu/Debian: `sudo apt-get install graphviz`
    - CentOS/RHEL: `sudo yum install graphviz`
    - macOS: `brew install graphviz`

## Usage

```bash
# Basic usage (ASCII output)
./salt_state_visualizer.py /path/to/salt/states

# Output to a file
./salt_state_visualizer.py /path/to/salt/states -o visualization.txt

# Generate graphical output (SVG)
./salt_state_visualizer.py /path/to/salt/states -g -o visualization

# Specify output format for graphical visualization
./salt_state_visualizer.py /path/to/salt/states -g -f png -o visualization

# Control which dependencies are shown
./salt_state_visualizer.py /path/to/salt/states --no-pillars  # Hide pillar dependencies
./salt_state_visualizer.py /path/to/salt/states --no-roles    # Hide role dependencies
./salt_state_visualizer.py /path/to/salt/states --no-systemd  # Hide systemd units
```

### Command Line Options

```
usage: salt_state_visualizer.py [-h] [-o OUTPUT] [-p] [-r] [--no-pillars] [--no-roles] [--no-systemd] [-g] [-f FORMAT] salt_path

positional arguments:
  salt_path            Path to the SaltStack states directory

options:
  -h, --help           Show this help message and exit
  -o, --output OUTPUT  Output file path (default: stdout)
  -p, --pillars        Include pillar dependencies in the output
  -r, --roles          Include role dependencies in the output
  --no-pillars         Exclude pillar dependencies from the output
  --no-roles           Exclude role dependencies from the output
  --no-systemd         Exclude systemd units from the output
  -g, --graphical      Generate graphical output (SVG) instead of ASCII
  -f, --format FORMAT  Output format for graphical output (svg, png, pdf, etc.)
```

### Example

```
$ ./salt_state_visualizer.py /home/anelson/pixstor/imageprep/salt/states/
```

This will output an ASCII diagram showing the relationships between states, roles, and systemd units found in the specified directory.

## Output Format

The output is an ASCII diagram with the following structure:

```
================================================================================
SaltStack State Visualization
================================================================================

State: apache
----------------------------------------
  Roles:
    ├── webserver
  Role Dependencies:
    ├── admin
    └── monitoring
  Pillar Dependencies:
    ├── apache:config_path
    └── apache:log_level
  Systemd Units:
    └── httpd.service
  Dependencies:
    └── firewall

State: firewall
----------------------------------------
  Systemd Units:
    └── firewalld.service

...

================================================================================
Total States: 99
Total Roles: 42
Total Role Dependencies: 28
Total Pillar Dependencies: 134
Total Systemd Units: 156
================================================================================
```

## Enhanced Systemd Unit Detection

The script uses multiple detection patterns to identify systemd units in SaltStack states:

- Standard `service.running` with name field
- Direct `service.running` declarations nested under other IDs
- `systemd.*` states with name field
- `service.disabled` states
- Service names in IDs with `service.running`
- Enable/disable service statements
- Timer units (including templated ones like `ap-analytics@<filesystem>.timer`)
- Templated service names with Jinja variables

Templated variables in systemd unit names (e.g., `{{ filesystem }}`) are standardized to a more readable format (e.g., `<filesystem>`) in the visualization.

## Graphical Visualization

When using the `-g` or `--graphical` option, the script generates a card-based visualization using Graphviz. The visualization features:

### Card-Based Layout

- **Organized Grid**: States are arranged in a clean 3-column grid layout
- **Self-Contained Cards**: Each state is displayed as a self-contained card with all its related information
- **Filtered Content**: Empty states (with no role dependencies, pillar dependencies, or systemd units) are automatically filtered out

### Card Structure

Each card contains the following color-coded sections:

- **State Name Header** (Light blue): The name of the SaltStack state
- **Role Dependencies** (Light green): Roles that the state depends on
- **Pillar Dependencies** (Light yellow): Pillar values accessed by the state
- **Systemd Units** (Light red): Systemd services and timers managed by the state

### Visualization Benefits

- **Improved Readability**: No overlapping edges or cluttered connections between states
- **Focused Information**: Only shows relevant information for each state
- **Consistent Layout**: Uniform presentation makes it easy to scan and compare states
- **Scalable Design**: Works well with both small and large SaltStack deployments

The card-based visualization provides a clean, organized view of your SaltStack states, making it much easier to understand complex deployments at a glance.

### Output Formats

The script supports various output formats through the `-f` or `--format` option:

- `svg`: Scalable Vector Graphics (default)
- `png`: Portable Network Graphics
- `pdf`: Portable Document Format
- `jpg`: JPEG image
- And other formats supported by Graphviz

## Customization

You can modify the script to extract additional information or change the visualization format by editing the `SaltStateVisualizer` class methods.
