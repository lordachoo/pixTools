import os
import re
import sys
import glob
import csv
import argparse
import webbrowser
from datetime import datetime
from shutil import which
from graphviz import Digraph

VERSION = "13"

def check_graphviz_installed():
    if which("dot") is None:
        print("\n❗ Graphviz executable 'dot' not found in PATH.")
        print("👉 Download & install from https://graphviz.org/download/")
        sys.exit(1)

check_graphviz_installed()

def extract_site(name: str) -> str:
    return name.split("-")[0] if "-" in name else "default"



def parse_interfaces(text: str):
    interfaces = []
    lines = text.strip().splitlines()
    data_lines = [line for line in lines if not re.match(r'-{5,}', line) and not line.strip().startswith("Interface")]
    for line in data_lines:
        fields = re.split(r'\s{2,}', line.strip())
        if len(fields) >= 6:
            iface = {
                "interface": fields[0],
                "admin": fields[1],
                "oper": fields[2],
                "speed": fields[3] if len(fields) > 3 else "",
                "mtu": fields[4] if len(fields) > 4 else "",
                "type": fields[5] if len(fields) > 5 else "",
                "remote_host": fields[6] if len(fields) > 6 else "",
                "remote_port": fields[7] if len(fields) > 7 else "",
            }
            interfaces.append(iface)
    return interfaces


def escape_label(text: str) -> str:
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\"')
    return text

def build_outputs(switch_data: dict, base: str, dark: bool, grouped: bool,
                  save_pdf: bool, save_png: bool, save_csv: bool):
    dot = Digraph(comment="Network Topology", format='svg')
    if dark:
        dot.attr(bgcolor="#1e1e1e")
        dot.attr('node', fontcolor='white', color='#888888',
                 style='filled', fillcolor='#2e2e2e')
        dot.attr('edge', color='white', fontcolor='white')
    else:
        dot.attr('node', style='filled', fillcolor='#2a2a2a')

    csv_rows = []

    for sw, iface_list in switch_data.items():
        site = extract_site(sw)
        cluster_id = re.sub(r"[^a-zA-Z0-9_]", "_", f"cluster_{site}")  # Safe ID for Graphviz"
        with dot.subgraph(name=cluster_id) as sub:
            if grouped:
                sub.attr(label=site)
            for iface in iface_list:
                speed = iface.get("speed", "") or ""
                mtu = iface.get("mtu", "") or ""
                label_parts = [f"{sw}", f"[{iface['interface']}]", f"Speed: {speed}" if speed else "", f"MTU: {mtu}" if mtu else ""]
                local_label = escape_label("\n".join(part for part in label_parts if part))
                local_id = re.sub(r"[^a-zA-Z0-9_]", "_", f"{sw}_{iface['interface']}")
                color = "green" if iface["oper"].lower() == "up" else "red"
                sub.node(local_id, label=local_label, color=color, fontcolor=color)
                
                csv_entry = [sw, iface['interface'], iface['speed'],
                             iface['remote_host'], iface['remote_port']]
                csv_rows.append(csv_entry)

                if iface["remote_host"]:
                    remote_node = escape_label(f"{iface['remote_host']}\n[{iface['remote_port']}]")
                    remote_label = escape_label(f"{iface['remote_host']}\n[{iface['remote_port']}]")
                    remote_id = re.sub(r"[^a-zA-Z0-9_]", "_", f"{iface['remote_host']}_{iface['remote_port']}")
                    dot.node(remote_id, label=remote_label, shape='box', style='dashed')
                    dot.edge(local_id, remote_id)

    svg_path = dot.render(base, view=False)
    print(f"✅ SVG saved: {svg_path}")

    if save_png:
        dot.format = 'png'
        png_path = dot.render(base + "_png", view=False)
        print(f"🖼️ PNG saved: {png_path}")

    if save_pdf:
        dot.format = 'pdf'
        pdf_path = dot.render(base + "_pdf", view=False)
        print(f"📄 PDF saved: {pdf_path}")

    with open(svg_path, 'r') as f:
        svg_content = f.read()

    html_path = base + ".html"
    with open(html_path, 'w') as html:
        html.write("<html><head><title>Network Topology</title>")
        if dark:
            html.write("<style>body{background:#1e1e1e;color:white;}</style>")
        html.write("</head><body>")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html.write(f"<h2>Network Topology — {timestamp}</h2>")
        html.write(svg_content)
        html.write("</body></html>")
    print(f"✅ HTML saved: {html_path}")

    if save_csv:
        csv_path = base + ".csv"
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Switch", "Interface", "Speed", "Remote Host", "Remote Port"])
            writer.writerows(csv_rows)
        print(f"✅ CSV saved: {csv_path}")

    try:
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
    except Exception:
        pass

def interactive_toggle(prompt_msg):
    return input(prompt_msg).strip().lower().startswith('y')

def main():
    parser = argparse.ArgumentParser(description="Generate network topology diagram")
    parser.add_argument('--dark', action='store_true', help="Dark mode")
    parser.add_argument('--group', action='store_true', help="Group by site/rack prefix")
    parser.add_argument('--batch', action='store_true', help="Process *.txt files in current dir")
    parser.add_argument('--pdf', action='store_true', help="Export PDF")
    parser.add_argument('--png', action='store_true', help="Export PNG")
    parser.add_argument('--csv', action='store_true', help="Export CSV")
    args = parser.parse_args()

    if not any(vars(args).values()):
        print("\n✨ No toggles supplied. Example usage for future:")
        print("   python generate_network_topology_v4.py --dark --group --batch --pdf --png --csv\n")
        args.dark = interactive_toggle("🌙 Enable dark mode? (y/n): ")
        args.group = interactive_toggle("🗂️  Group by site/rack prefix? (y/n): ")
        args.batch = interactive_toggle("📂 Process multiple switch files (*.txt) in folder? (y/n): ")
        args.pdf = interactive_toggle("📄 Generate PDF output? (y/n): ")
        args.png = interactive_toggle("🖼️  Generate PNG output? (y/n): ")
        args.csv = interactive_toggle("📑 Generate CSV link table? (y/n): ")

    switch_data = {}
    if args.batch:
        txt_files = glob.glob("*.txt")
        if not txt_files:
            print("❗ No .txt files found for batch mode.")
            sys.exit(1)
        for txt_file in txt_files:
            with open(txt_file, 'r') as f:
                content = f.read()
            sw = os.path.splitext(os.path.basename(txt_file))[0]
            switch_data[sw] = parse_interfaces(content)
    else:
        print("\n📋 Paste switch interface output. End with an empty line:")
        lines = []
        while True:
            line = input()
            if not line.strip():
                break
            lines.append(line)
        content = "\n".join(lines)
        sw = input("🖋️  Enter switch name: ").strip() or "Switch1"
        switch_data[sw] = parse_interfaces(content)

    base_name = input("💾 Base name for output files (no extension): ").strip() or "network_topology"
    build_outputs(switch_data, base_name, dark=args.dark, grouped=args.group,
                  save_pdf=args.pdf, save_png=args.png, save_csv=args.csv)

if __name__ == "__main__":
    main()
