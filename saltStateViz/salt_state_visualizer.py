#!/usr/bin/env python3
"""
SaltStack State Visualizer

This script parses SaltStack states in a given directory and outputs an ASCII diagram
or graphical visualization showing the relationships between states, roles, systemd units,
and their dependencies.
"""

import os
import sys
import re
import subprocess
import argparse
import yaml
import graphviz
from collections import defaultdict

class SaltStateVisualizer:
    def __init__(self, salt_path):
        self.salt_path = salt_path
        self.states = []
        self.roles = defaultdict(list)
        self.systemd_units = defaultdict(set)
        self.includes = defaultdict(set)
        self.dependencies = defaultdict(list)
        self.role_dependencies = defaultdict(list)
        self.pillar_dependencies = defaultdict(set)

    def find_whole_states(self):
        """Find all directories containing init.sls files (whole states)"""
        try:
            cmd = f"find {self.salt_path} -name 'init.sls' -printf '%h\n' | xargs -n1 basename"
            result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
            unique_states = {state.strip() for state in result.stdout.split('\n') if state.strip()}
            self.states = sorted(list(unique_states))  # Convert back to sorted list for consistent ordering
            return self.states
        except subprocess.CalledProcessError as e:
            print(f"Error finding whole states: {e}", file=sys.stderr)
            return []

    def parse_state_files(self):
        """Parse all state files to extract roles and systemd units"""
        for state in self.states:
            state_dir = os.path.join(self.salt_path, state)
            
            # Parse init.sls for includes
            init_file = os.path.join(state_dir, 'init.sls')
            if os.path.exists(init_file):
                self._parse_includes(init_file, state)
            
            # Parse all .sls files in the state directory
            for root, _, files in os.walk(state_dir):
                for file in files:
                    if file.endswith('.sls'):
                        file_path = os.path.join(root, file)
                        self._parse_file(file_path, state)

    def _parse_includes(self, file_path, state):
        """Parse include statements from a state file"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Pre-process content to standardize templated variables
            content = re.sub(r'@\{\{\s*([^\}]+)\s*\}\}', r'@<\1>', content)
            # Make sure to standardize any remaining templated variables
            content = re.sub(r'\{\{\s*([^\}]+)\s*\}\}', r'<\1>', content)
                
            # Find include statements
            include_match = re.search(r'include:\s*\n((?:\s*-\s*.*\n)+)', content)
            if include_match:
                includes_block = include_match.group(1)
                includes = re.findall(r'-\s*(.*)', includes_block)
                
                includes_set = set(include.strip() for include in includes)
                includes_set = {include if not include.startswith('.') else f"{state}{include}" for include in includes_set}
                self.includes[state] = self.includes[state].union(includes_set)
        except Exception as e:
            print(f"Error parsing includes in {file_path}: {e}", file=sys.stderr)

    def _parse_file(self, file_path, state):
        """Parse a state file for roles and systemd units"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Try to parse as YAML if possible
            try:
                # Skip the first part if it's a comment block
                yaml_content = re.sub(r'^#.*?(?=^[^#])', '', content, flags=re.DOTALL | re.MULTILINE)
                data = yaml.safe_load(yaml_content)
                if data and isinstance(data, dict):
                    self._extract_from_yaml(data, state)
            except Exception:
                # Fallback to regex parsing if YAML parsing fails
                pass
            
            # Pre-process content to standardize templated variables
            content = re.sub(r'@\{\{\s*([^\}]+)\s*\}\}', r'@<\1>', content)
            # Make sure to standardize any remaining templated variables
            content = re.sub(r'\{\{\s*([^\}]+)\s*\}\}', r'<\1>', content)
            
            # Find roles defined in the state
            role_matches = re.findall(r'role\s*:\s*([^\n]+)', content)
            for role in role_matches:
                role = role.strip()
                if role not in self.roles[state]:
                    self.roles[state].append(role)
            
            # Find role dependencies (roles used in conditional blocks)
            role_dep_matches = re.findall(r'salt\.pixpillar\.nodehasrole\([\'"]([^\'"]+)[\'"]\)', content)
            for role in role_dep_matches:
                role = role.strip()
                if role not in self.role_dependencies[state]:
                    self.role_dependencies[state].append(role)
            
            # Find pillar dependencies (pillars accessed via salt.pillar.get)
            pillar_matches = re.findall(r'salt\.pillar\.get\([\'"]([^\'"]+)[\'"]\)', content)
            for pillar in pillar_matches:
                pillar = pillar.strip()
                self.pillar_dependencies[state].add(pillar)
            
            # Find systemd units - multiple patterns
            service_matches = re.findall(r'service\.running:\s*\n\s*-\s*name:\s*([^\n]+)', content)
            for service in service_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 2: Look for direct service.running declarations nested under other IDs
            service_nested_matches = re.findall(r'([^:\n]+):\s*\n\s*service\.running', content)
            for service in service_nested_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 3: Look for systemd.* states with name field
            systemd_matches = re.findall(r'systemd\.[^:]+:\s*\n\s*-\s*name:\s*([^\n]+)', content)
            for service in systemd_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 4: Look for service.disabled states
            disabled_matches = re.findall(r'service\.disabled:\s*\n\s*-\s*name:\s*([^\n]+)', content)
            for service in disabled_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 5: Look for service names in IDs with service.running
            service_id_matches = re.findall(r'([^:\n]+):\s*\n\s*service\.running', content)
            for service in service_id_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 6: Look for enable/disable service statements
            enable_matches = re.findall(r'systemctl\s+enable\s+([^\s&;]+)', content)
            for service in enable_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            disable_matches = re.findall(r'systemctl\s+disable\s+([^\s&;]+)', content)
            for service in disable_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 7: Look for specific timer patterns
            timer_matches = re.findall(r'(ap-analytics@\*\.timer)', content)
            for service in timer_matches:
                service = service.strip()
                self.systemd_units[state].add(service)
            
            # Pattern 8: Look for templated service names
            templated_service_matches = re.findall(r'([\w@\.-]+@<[^>]+>\.(timer|service))', content)
            for service_match in templated_service_matches:
                if isinstance(service_match, tuple):
                    service = service_match[0]
                else:
                    service = service_match
                service = service.strip()
                self.systemd_units[state].add(service)
            
        except Exception as e:
            print(f"Error parsing file {file_path}: {e}", file=sys.stderr)

    def _extract_from_yaml(self, data, state):
        """Extract information from parsed YAML data"""
        if not isinstance(data, dict):
            return
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Look for service.running states
                if 'service.running' in value:
                    name = value.get('service.running', {}).get('name', key)
                    if name:
                        self.systemd_units[state].add(name)
                
                # Look for systemd.* states
                for k in value:
                    if k.startswith('systemd.'):
                        name = value.get(k, {}).get('name', key)
                        if name:
                            self.systemd_units[state].add(name)
                
                # Recursively process nested dictionaries
                self._extract_from_yaml(value, state)
            elif isinstance(value, list):
                # Process list items
                for item in value:
                    if isinstance(item, dict):
                        self._extract_from_yaml(item, state)

    def generate_ascii_diagram(self, show_pillars=True, show_roles=True):
        """Generate ASCII diagram of states, roles, and systemd units"""
        diagram = []
        diagram.append("=" * 80)
        diagram.append("SaltStack State Visualization")
        diagram.append("=" * 80)
        diagram.append("")
        
        # Generate diagram for each state
        for state in sorted(self.states):
            diagram.append(f"State: {state}")
            diagram.append("-" * 40)
            
            # Add roles
            if state in self.roles and self.roles[state]:
                diagram.append("  Roles:")
                roles = sorted(self.roles[state])
                for i, role in enumerate(roles):
                    if i == len(roles) - 1:
                        diagram.append(f"    └── {role}")
                    else:
                        diagram.append(f"    ├── {role}")
            
            # Add role dependencies if enabled
            if show_roles and state in self.role_dependencies and self.role_dependencies[state]:
                # Filter out roles that are already in the roles list to avoid duplicates
                role_deps = [r for r in self.role_dependencies[state] if r not in self.roles.get(state, [])]
                if role_deps:
                    diagram.append("  Role Dependencies:")
                    role_deps = sorted(role_deps)
                    for i, role in enumerate(role_deps):
                        if i == len(role_deps) - 1:
                            diagram.append(f"    └── {role}")
                        else:
                            diagram.append(f"    ├── {role}")
            
            # Add pillar dependencies if enabled
            if show_pillars and state in self.pillar_dependencies and self.pillar_dependencies[state]:
                diagram.append("  Pillar Dependencies:")
                pillar_deps = sorted(list(self.pillar_dependencies[state]))
                for i, pillar in enumerate(pillar_deps):
                    if i == len(pillar_deps) - 1:
                        diagram.append(f"    └── {pillar}")
                    else:
                        diagram.append(f"    ├── {pillar}")
            
            # Add systemd units
            if state in self.systemd_units and self.systemd_units[state]:
                diagram.append("  Systemd Units:")
                units = sorted(list(self.systemd_units[state]))
                for i, unit in enumerate(units):
                    if i == len(units) - 1:
                        diagram.append(f"    └── {unit}")
                    else:
                        diagram.append(f"    ├── {unit}")
            
            # Add dependencies (includes)
            if state in self.includes and self.includes[state]:
                diagram.append("  Dependencies:")
                includes = sorted(list(self.includes[state]))
                for i, include in enumerate(includes):
                    if i == len(includes) - 1:
                        diagram.append(f"    └── {include}")
                    else:
                        diagram.append(f"    ├── {include}")
            
            diagram.append("")
        
        # Add summary statistics
        # Count unique roles
        all_roles = set()
        for roles in self.roles.values():
            all_roles.update(roles)
        
        # Count unique role dependencies
        all_role_deps = set()
        for deps in self.role_dependencies.values():
            all_role_deps.update(deps)
        
        # Count unique pillar dependencies
        all_pillar_deps = set()
        for deps in self.pillar_dependencies.values():
            all_pillar_deps.update(deps)
        
        # Count unique systemd units
        all_systemd_units = set()
        for units in self.systemd_units.values():
            all_systemd_units.update(units)
        
        diagram.append("=" * 80)
        diagram.append(f"Total States: {len(self.states)}")
        diagram.append(f"Total Roles: {len(all_roles)}")
        if show_roles:
            diagram.append(f"Total Role Dependencies: {len(all_role_deps)}")
        if show_pillars:
            diagram.append(f"Total Pillar Dependencies: {len(all_pillar_deps)}")
        diagram.append(f"Total Systemd Units: {len(all_systemd_units)}")
        diagram.append("=" * 80)
        
        return "\n".join(diagram)

    def generate_graphviz(self, output_file=None, show_pillars=True, show_roles=True, show_systemd=True, format='svg'):
        """Generate a graphical visualization using graphviz with a card-based layout

        Args:
            output_file: Path to save the output file (without extension)
            show_pillars: Whether to show pillar dependencies
            show_roles: Whether to show role dependencies
            show_systemd: Whether to show systemd units
            format: Output format (svg, png, pdf, etc.)

        Returns:
            Path to the generated file
        """
        # Create a new graph with HTML-like labels for better formatting
        dot = graphviz.Digraph(
            comment='SaltStack State Visualization',
            format=format,
            engine='dot',
            node_attr={
                'shape': 'plaintext',  # Use plaintext for HTML-like labels
                'fontname': 'Arial',
                'margin': '0',
            },
            graph_attr={
                'rankdir': 'TB',       # Top to bottom layout
                'ranksep': '0.75',     # Separation between ranks
                'nodesep': '0.5',      # Separation between nodes
                'splines': 'ortho',    # Use orthogonal lines
                'concentrate': 'true',  # Concentrate edges
                'ratio': 'fill',       # Fill the available space
                'compound': 'true',     # Allow edges between clusters
                'newrank': 'true',     # Better ranking
            }
        )
        
        def sanitize_id(text):
            """Sanitize text to be used as a node ID"""
            # Replace characters that could cause issues in DOT syntax
            return re.sub(r'[^a-zA-Z0-9_]', '_', text)
        
        def sanitize_html(text):
            """Sanitize text to be used in HTML-like labels"""
            # Escape HTML special characters
            return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        
        # Define colors
        state_color = '#ADD8E6'  # Light blue
        role_color = '#90EE90'   # Light green
        pillar_color = '#FFFFE0' # Light yellow
        systemd_color = '#FFB6C1' # Light red
        
        # Filter out states with no roles, role dependencies, pillars, or systemd units
        filtered_states = []
        for state in sorted(self.states):
            has_roles = show_roles and state in self.roles and self.roles[state]
            has_role_deps = show_roles and state in self.role_dependencies and self.role_dependencies[state]
            has_pillars = show_pillars and state in self.pillar_dependencies and self.pillar_dependencies[state]
            has_systemd = show_systemd and state in self.systemd_units and self.systemd_units[state]
            
            if has_roles or has_role_deps or has_pillars or has_systemd:
                filtered_states.append(state)
        
        # Create a grid layout with states in a 3-column grid
        states_per_row = 3
        
        # Use a completely different approach with HTML-like tables for layout
        dot = graphviz.Digraph(
            comment='SaltStack State Visualization',
            format=format,
            engine='dot',
            node_attr={
                'shape': 'plaintext',
                'fontname': 'Arial',
            },
            graph_attr={
                'rankdir': 'TB',
                'ranksep': '0.5',
                'nodesep': '0.5',
            }
        )
        
        # Create a main table for the entire layout
        main_label = '<'
        main_label += '<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="10" CELLPADDING="10">'
        
        # Calculate how many rows we need
        rows_needed = (len(filtered_states) + states_per_row - 1) // states_per_row
        
        # Generate the table rows
        for row in range(rows_needed):
            main_label += '<TR>'
            
            # Add cells for this row
            for col in range(states_per_row):
                idx = row * states_per_row + col
                if idx < len(filtered_states):
                    state = filtered_states[idx]
                    
                    # Create a nested table for each state card
                    main_label += '<TD>'
                    main_label += f'<TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="4" BGCOLOR="white">'
                    
                    # State header
                    main_label += f'<TR><TD BGCOLOR="{state_color}" COLSPAN="2"><B>{sanitize_html(state)}</B></TD></TR>'
                    
                    # Role dependencies section - only show this section, not regular roles
                    if show_roles and state in self.role_dependencies and self.role_dependencies[state]:
                        main_label += f'<TR><TD BGCOLOR="{role_color}" COLSPAN="2"><B>Role Dependencies</B></TD></TR>'
                        for role in sorted(self.role_dependencies[state]):
                            main_label += f'<TR><TD COLSPAN="2" ALIGN="LEFT">{sanitize_html(role)}</TD></TR>'
                    
                    # Pillar dependencies section
                    if show_pillars and state in self.pillar_dependencies and self.pillar_dependencies[state]:
                        main_label += f'<TR><TD BGCOLOR="{pillar_color}" COLSPAN="2"><B>Pillar Dependencies</B></TD></TR>'
                        for pillar in sorted(list(self.pillar_dependencies[state])):
                            main_label += f'<TR><TD COLSPAN="2" ALIGN="LEFT">{sanitize_html(pillar)}</TD></TR>'
                    
                    # Systemd units section
                    if show_systemd and state in self.systemd_units and self.systemd_units[state]:
                        main_label += f'<TR><TD BGCOLOR="{systemd_color}" COLSPAN="2"><B>Systemd Units</B></TD></TR>'
                        for unit in sorted(list(self.systemd_units[state])):
                            main_label += f'<TR><TD COLSPAN="2" ALIGN="LEFT">{sanitize_html(unit)}</TD></TR>'
                        
                    # Close the card table
                    main_label += '</TABLE>'
                    main_label += '</TD>'
                else:
                    # Empty cell for padding
                    main_label += '<TD></TD>'
            
            main_label += '</TR>'
        
        # Close the main table
        main_label += '</TABLE>'
        main_label += '>'
        
        # Create a single node with the entire HTML table
        dot.node('salt_states', label=main_label, shape='plaintext')
        
        # Render the graph
        if output_file:
            return dot.render(output_file, cleanup=True, format=format)
        else:
            return dot.render(cleanup=True, format=format)

def check_graphviz_installed():
    """Check if graphviz executables are installed"""
    try:
        subprocess.run(['dot', '-V'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def main():
    parser = argparse.ArgumentParser(description='SaltStack State Visualizer')
    parser.add_argument('salt_path', help='Path to the SaltStack states directory')
    parser.add_argument('-o', '--output', help='Output file path (default: stdout)')
    parser.add_argument('-p', '--pillars', action='store_true', help='Include pillar dependencies in the output')
    parser.add_argument('-r', '--roles', action='store_true', help='Include role dependencies in the output')
    parser.add_argument('--no-pillars', action='store_true', help='Exclude pillar dependencies from the output')
    parser.add_argument('--no-roles', action='store_true', help='Exclude role dependencies from the output')
    parser.add_argument('--no-systemd', action='store_true', help='Exclude systemd units from the output')
    parser.add_argument('-g', '--graphical', action='store_true', help='Generate graphical output (SVG) instead of ASCII')
    parser.add_argument('-f', '--format', default='svg', help='Output format for graphical output (svg, png, pdf, etc.)')
    args = parser.parse_args()
    
    salt_path = args.salt_path
    if not os.path.isdir(salt_path):
        print(f"Error: {salt_path} is not a directory", file=sys.stderr)
        sys.exit(1)
    
    visualizer = SaltStateVisualizer(salt_path)
    
    print(f"Finding whole states in {salt_path}...", file=sys.stderr)
    states = visualizer.find_whole_states()
    print(f"Found {len(states)} whole states", file=sys.stderr)
    
    print("Parsing state files...", file=sys.stderr)
    visualizer.parse_state_files()
    
    # Process command line flags
    show_pillars = not args.no_pillars
    show_roles = not args.no_roles
    show_systemd = not args.no_systemd
    
    # Determine output type and generate appropriate visualization
    if args.graphical:
        # Check if graphviz is installed
        if not check_graphviz_installed():
            print("Error: Graphviz executables not found. Please install graphviz and ensure 'dot' is in your PATH.", file=sys.stderr)
            print("On Ubuntu/Debian: sudo apt-get install graphviz", file=sys.stderr)
            print("On CentOS/RHEL: sudo yum install graphviz", file=sys.stderr)
            print("On macOS: brew install graphviz", file=sys.stderr)
            print("Falling back to ASCII output...", file=sys.stderr)
            args.graphical = False
        else:
            output_file = args.output
            if output_file and '.' in output_file:
                # Strip extension if present as graphviz will add it
                output_file = os.path.splitext(output_file)[0]
                
            print(f"Generating graphical visualization in {args.format} format...", file=sys.stderr)
            try:
                output_path = visualizer.generate_graphviz(
                    output_file=output_file,
                    show_pillars=show_pillars,
                    show_roles=show_roles,
                    show_systemd=show_systemd,
                    format=args.format
                )
                print(f"Graphical visualization written to {output_path}", file=sys.stderr)
                return
            except Exception as e:
                print(f"Error generating graphical output: {e}", file=sys.stderr)
                print("Falling back to ASCII output...", file=sys.stderr)
    else:
        print("Generating ASCII diagram...", file=sys.stderr)
        diagram = visualizer.generate_ascii_diagram(show_pillars=show_pillars, show_roles=show_roles)
        
        if args.output:
            try:
                with open(args.output, 'w') as f:
                    f.write(diagram)
                print(f"Diagram written to {args.output}", file=sys.stderr)
            except Exception as e:
                print(f"Error writing to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(diagram)

if __name__ == "__main__":
    main()
