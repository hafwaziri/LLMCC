import tempfile
import os
import subprocess
import shutil
from pathlib import Path
import networkx as nx
import re

def _with_super_entry(G):
    super_entry = "__super_entry__"
    H = G.copy()
    if super_entry in H:
        i = 0
        while f"{super_entry}{i}" in H:
            i += 1
        super_entry = f"{super_entry}{i}"
    
    entry_nodes = [n for n in H.nodes() if H.in_degree(n) == 0]
    H.add_node(super_entry)

    for n in entry_nodes:
        H.add_edge(super_entry, n)
    
    return H, super_entry

def norm_sim(a, b):
    denom = max(abs(a), abs(b), 1)
    return max(0.0, 1.0 - (abs(a-b) / denom))

def degree_histogram(G):
    if G.number_of_nodes() == 0:
        return [], []
    in_degs = [d for _, d in G.in_degree()]
    out_degs = [d for _, d in G.out_degree()]
    max_in = max(in_degs) if in_degs else 0
    max_out = max(out_degs) if out_degs else 0

    in_hist = [0] * (max_in + 1)
    out_hist = [0] * (max_out + 1)
    for d in in_degs:
        in_hist[d] += 1
    for d in out_degs:
        out_hist[d] += 1
    return in_hist, out_hist

def hist_similarity(h1, h2):
    if not h1 and not h2:
        return 1.0
    m = max(len(h1), len(h2))
    a = h1 + [0] * (m - len(h1))
    b = h2 + [0] * (m - len(h2))
    mass = max(sum(a), sum(b), 1)
    l1 = sum(abs(x - y) for x, y in zip(a, b))
    # Max possible L1 is 2*mass (all nodes shift bins)
    return max(0.0, 1.0 - (l1 / (2 * mass)))

def condensation_features(G):
    if G.number_of_nodes() == 0:
        return {"sccs": 0, "cond_nodes": 0, "cond_edges": 0, "cond_longest_path": 0}

    C = nx.condensation(G)
    try:
        longest = nx.dag_longest_path_length(C) if C.number_of_nodes() > 0 else 0
    except Exception:
        longest = 0

    return {
        "sccs": C.number_of_nodes(),
        "cond_nodes": C.number_of_nodes(),
        "cond_edges": C.number_of_edges(),
        "cond_longest_path": int(longest),
    }

def loop_scc_count(G):
    count = 0
    for scc in nx.strongly_connected_components(G):
        if len(scc) > 1:
            count += 1
        else:
            (u,) = tuple(scc)
            if G.has_edge(u, u):
                count += 1
    return count

def cyclomatic_complexity(G):
    n = G.number_of_nodes()
    e = G.number_of_edges()
    if n == 0:
        return 0
    p = nx.number_weakly_connected_components(G)
    return e - n + 2 * p

def dominator_tree_isomorphic(cfg1, cfg2):
    if cfg1.number_of_nodes() == 0 or cfg2.number_of_nodes() == 0:
        return None

    try:
        h1, start1 = _with_super_entry(cfg1)
        h2, start2 = _with_super_entry(cfg2)

        idom1 = nx.immediate_dominators(h1, start1)
        idom2 = nx.immediate_dominators(h2, start2)

        dom_g1 = nx.DiGraph()
        dom_g2 = nx.DiGraph()

        for node, idom in idom1.items():
            if node != idom:
                dom_g1.add_edge(idom, node)

        for node, idom in idom2.items():
            if node != idom:
                dom_g2.add_edge(idom, node)

        if start1 in dom_g1:
            dom_g1.remove_node(start1)
        if start2 in dom_g2:
            dom_g2.remove_node(start2)

        return nx.is_isomorphic(dom_g1, dom_g2)

    except Exception:
        return None

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

def compute_cfg_similarity_score(cfg1, cfg2, dominator_tree_match=None):
    n1, e1 = cfg1.number_of_nodes(), cfg1.number_of_edges()
    n2, e2 = cfg2.number_of_nodes(), cfg2.number_of_edges()

    cc1 = cyclomatic_complexity(cfg1)
    cc2 = cyclomatic_complexity(cfg2)

    loop1 = loop_scc_count(cfg1)
    loop2 = loop_scc_count(cfg2)

    in1, out1 = degree_histogram(cfg1)
    in2, out2 = degree_histogram(cfg2)

    cond1 = condensation_features(cfg1)
    cond2 = condensation_features(cfg2)

    sim_nodes = norm_sim(n1, n2)
    sim_edges = norm_sim(e1, e2)
    sim_complexity = norm_sim(cc1, cc2)
    sim_loops = norm_sim(loop1, loop2)
    sim_in_hist = hist_similarity(in1, in2)
    sim_out_hist = hist_similarity(out1, out2)

    sim_cond_sccs = norm_sim(cond1["sccs"], cond2["sccs"])
    sim_cond_edges = norm_sim(cond1["cond_edges"], cond2["cond_edges"])
    sim_cond_longest = norm_sim(cond1["cond_longest_path"], cond2["cond_longest_path"])
    sim_cond = (sim_cond_sccs + sim_cond_edges + sim_cond_longest) / 3.0

    dom_available = (dominator_tree_match is True) or (dominator_tree_match is False)
    sim_dom = 1.0 if dominator_tree_match is True else 0.0

    w = {
        "nodes": 0.10,
        "edges": 0.10,
        "complexity": 0.15,
        "loops_scc": 0.10,
        "degree_hist": 0.25,
        "condensation": 0.20,
        "dominators": 0.10,
    }

    if not dom_available:
        w["dominators"] = 0.0

    wsum = sum(w.values()) or 1.0
    w = {k: v / wsum for k, v in w.items()}

    score = (
        w["nodes"] * sim_nodes
        + w["edges"] * sim_edges
        + w["complexity"] * sim_complexity
        + w["loops_scc"] * sim_loops
        + w["degree_hist"] * ((sim_in_hist + sim_out_hist) / 2.0)
        + w["condensation"] * sim_cond
        + w["dominators"] * sim_dom
    )

    breakdown = {
        "sim_nodes": sim_nodes,
        "sim_edges": sim_edges,
        "sim_cyclomatic_complexity": sim_complexity,
        "sim_loops_scc": sim_loops,
        "sim_in_degree_hist": sim_in_hist,
        "sim_out_degree_hist": sim_out_hist,
        "sim_condensation": sim_cond,
        "sim_dominators": (sim_dom if dom_available else None),
        "features": {
            "nodes1": n1, "edges1": e1, "cc1": cc1, "loops_scc1": loop1, "cond1": cond1,
            "nodes2": n2, "edges2": e2, "cc2": cc2, "loops_scc2": loop2, "cond2": cond2,
        },
        "weights": w,
        "dominator_available": dom_available,
    }

    score = float(max(0.0, min(1.0, score)))
    return {"score": score, "breakdown": breakdown}

def compare_cfgs(cfg1, cfg2):

    is_isomorphic = nx.is_isomorphic(cfg1, cfg2)

    complexity1 = cyclomatic_complexity(cfg1)
    complexity2 = cyclomatic_complexity(cfg2)

    loops1 = loop_scc_count(cfg1)
    loops2 = loop_scc_count(cfg2)

    dom_match = dominator_tree_isomorphic(cfg1, cfg2)

    sim = compute_cfg_similarity_score(cfg1, cfg2, dominator_tree_match=dom_match)

    result = {
        'is_isomorphic': is_isomorphic,
        'graph1_nodes': cfg1.number_of_nodes(),
        'graph2_nodes': cfg2.number_of_nodes(),
        'graph1_edges': cfg1.number_of_edges(),
        'graph2_edges': cfg2.number_of_edges(),
        'cyclomatic_complexity_match': complexity1 == complexity2,
        'complexity1': complexity1,
        'complexity2': complexity2,
        'loop_count_match': loops1 == loops2,
        'loops1': loops1,
        'loops2': loops2,
        'dominator_tree_match': dom_match,
        'similarity_score': sim["score"],
        'similarity_breakdown': sim["breakdown"],
        'definitive_match': (
            is_isomorphic 
            and complexity1 == complexity2 
            and loops1 == loops2 
            and (dom_match if dom_match is not None else True)
        )
    }

    return result

def print_comparison_results(result):
    print(f"\n{'='*60}")
    print(f"CFG Comparison Results")
    print(f"{'='*60}")
    print(f"  Graph 1 - Nodes: {result['graph1_nodes']}, Edges: {result['graph1_edges']}")
    print(f"  Graph 2 - Nodes: {result['graph2_nodes']}, Edges: {result['graph2_edges']}")
    print(f"\n  Structural Isomorphism: {result['is_isomorphic']}")
    print(f"  Cyclomatic Complexity Match: {result['cyclomatic_complexity_match']}")
    print(f"    - Graph 1 Complexity: {result['complexity1']}")
    print(f"    - Graph 2 Complexity: {result['complexity2']}")
    print(f"  Loop Count Match: {result['loop_count_match']}")
    print(f"    - Graph 1 Loops (SCC): {result['loops1']}")
    print(f"    - Graph 2 Loops (SCC): {result['loops2']}")
    print(f"  Dominator Tree Match: {result['dominator_tree_match']}")

    if "similarity_score" in result:
        print(f"\n  Similarity Score (0..1): {result['similarity_score']:.3f}")

    print(f"\n  DEFINITIVE MATCH: {result['definitive_match']}")
    print(f"{'='*60}\n")

def compare_llvm_ir_cfgs(llvm_ir1, llvm_ir2):
    tmp_dir1 = None
    tmp_dir2 = None

    try:
        cfg_data1, tmp_dir1 = generate_cfg(llvm_ir1)
        cfg_data2, tmp_dir2 = generate_cfg(llvm_ir2)

        graphs1 = {name: parse_dot_to_graph(dot) for name, dot in cfg_data1.items()}
        graphs2 = {name: parse_dot_to_graph(dot) for name, dot in cfg_data2.items()}

        common_functions = set(graphs1.keys()) & set(graphs2.keys())

        comparison_results = {}
        for func_name in common_functions:
            comparison_results[func_name] = compare_cfgs(graphs1[func_name], graphs2[func_name])

        scores = [r.get("similarity_score") for r in comparison_results.values() if "similarity_score" in r]
        avg_score = (sum(scores) / len(scores)) if scores else None

        return {
            'comparisons': comparison_results,
            'only_in_ir1': list(set(graphs1.keys()) - set(graphs2.keys())),
            'only_in_ir2': list(set(graphs2.keys()) - set(graphs1.keys())),
            'all_match': all(r['definitive_match'] for r in comparison_results.values()) if comparison_results else False,
            'all_similarity_avg': avg_score,
        }

    finally:
        if tmp_dir1 and os.path.exists(tmp_dir1):
            shutil.rmtree(tmp_dir1)
        if tmp_dir2 and os.path.exists(tmp_dir2):
            shutil.rmtree(tmp_dir2)

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

    graphs = []
    for func_name, dot_content in cfg_data.items():
        G = parse_dot_to_graph(dot_content)
        print_graph_info(G)
        graphs.append(G)

    if len(graphs) >= 1:
        result = compare_cfgs(graphs[0], graphs[0])
        print_comparison_results(result)

    if tmp_dir and os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

