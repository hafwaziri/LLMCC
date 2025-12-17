import tempfile
import os
import subprocess
import shutil
from pathlib import Path
import networkx as nx
import re

def generate_cfg(llvm_ir):
    tmp_dir = None
    tmp_file_path = None

    try:
        tmp_dir = tempfile.mkdtemp()
        tmp_file_path = os.path.join(tmp_dir, "input.ll")

        with open(tmp_file_path, 'w') as f:
            f.write(llvm_ir)

        subprocess.run([
            'opt', '-disable-output',
            '-passes=dot-cfg',
            tmp_file_path
        ], check=True, cwd=tmp_dir)

        dot_files = list(Path(tmp_dir).glob('*.dot'))

        cfg_data = {}
        for dot_file in dot_files:
            with open(dot_file, 'r') as f:
                cfg_data[dot_file.name] = f.read()
        
        return cfg_data, tmp_dir

    except Exception:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise

def print_cfg_details(llvm_ir):
    cfg_data, tmp_dir = generate_cfg(llvm_ir)

    try:
        print("=== CFG Details ===\n")
        for filename, dot_content in cfg_data.items():
            print(f"Function: {filename}")
            print(f"DOT file content:\n{dot_content}\n")

            lines = dot_content.split('\n')
            print("Nodes (Basic Blocks):")
            for line in lines:
                if 'label=' in line and 'Node' in line:
                    print(f" {line.strip()}")
            
            print("\nEdges (Control Flow):")
            for line in lines:
                if '->' in line:
                    print(f" {line.strip()}")
            print("-" * 50)
        
        return cfg_data, tmp_dir
    except Exception:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
        raise

def parse_dot_to_graph(dot_content):
    G = nx.DiGraph()

    node_pattern = r'(Node0x[0-9a-f]+)\s*\[.*?label="(\{[^}]+\})'
    for match in re.finditer(node_pattern, dot_content, re.DOTALL):
        node_id = match.group(1)
        label = match.group(2)
        block_name_match = re.search(r'\{([^:\\]+)(?::|\\l)', label)
        block_name = block_name_match.group(1).strip() if block_name_match else node_id
        G.add_node(node_id, label=label, block_name=block_name)
    
    edge_pattern = r'(Node0x[0-9a-f]+)(?::\w+)?\s*->\s*(Node0x[0-9a-f]+)'
    for match in re.finditer(edge_pattern, dot_content):
        source = match.group(1)
        target = match.group(2)
        G.add_edge(source, target)
    
    return G

def print_graph_info(G):
    print(f"\n{'='*60}")
    print(f"Graph Information")
    print(f"{'='*60}")

    print(f"\nGraph Statistics:")
    print(f"  Nodes: {G.number_of_nodes()}")
    print(f"  Edges: {G.number_of_edges()}")
    print(f"  Is DAG: {nx.is_directed_acyclic_graph(G)}")

    print(f"\nNodes (Basic Blocks):")
    for node, attrs in G.nodes(data=True):
        block_name = attrs.get('block_name', 'unknown')
        print(f"  {node} -> Block: {block_name}")

    print(f"\nEdges (Control Flow):")
    for source, target in G.edges():
        source_block = G.nodes[source].get('block_name', 'unknown')
        target_block = G.nodes[target].get('block_name', 'unknown')
        print(f"  {source_block} -> {target_block}")

    print(f"\nGraph Properties:")
    if G.number_of_nodes() > 0:
        print(f"  Entry nodes (in-degree 0): {[G.nodes[n].get('block_name') for n in G.nodes() if G.in_degree(n) == 0]}")
        print(f"  Exit nodes (out-degree 0): {[G.nodes[n].get('block_name') for n in G.nodes() if G.out_degree(n) == 0]}")

    print(f"{'='*60}\n")

if __name__ == "__main__":
    test_ir = """
    define i32 @factorial(i32 %n) {
    entry:
      %cmp = icmp sgt i32 %n, 1
      br i1 %cmp, label %recurse, label %base
    
    base:
      ret i32 1
    
    recurse:
      %sub = sub i32 %n, 1
      %call = call i32 @factorial(i32 %sub)
      %mul = mul i32 %n, %call
      ret i32 %mul
    }
    """

    cfg_data, tmp_dir = print_cfg_details(test_ir)

    for func_name, dot_content in cfg_data.items():
        G = parse_dot_to_graph(dot_content)
        print_graph_info(G)
