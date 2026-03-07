# -*- coding: utf-8 -*-
import networkx as nx
import json
from decimal import Decimal
import sys

# --- 1. Mock Data Generation ---
def generate_mock_data():
    """
    Construct a set of mock data consistent with SmartTrainingScheme models.
    """
    # Mock Course Data
    # Chinese names are unicode escaped to ensure ASCII file compatibility
    courses = [
        {"code": "CS101", "name": "\u8ba1\u7b97\u673a\u5bfc\u8bba", "credits": 2.0},
        {"code": "CS102", "name": "\u7a0b\u5e8f\u8bbe\u8ba1\u57fa\u7840", "credits": 4.0},
        {"code": "CS201", "name": "\u6570\u636e\u7ed3\u6784", "credits": 3.5},
        {"code": "CS202", "name": "\u79bb\u6563\u6570\u5b66", "credits": 3.0},
        {"code": "CS301", "name": "\u7b97\u6cd5\u5206\u6790\u4e0e\u8bbe\u8ba1", "credits": 3.0},
        {"code": "CS302", "name": "\u64cd\u4f5c\u7cfb\u7edf", "credits": 4.0},
        {"code": "CS303", "name": "\u8ba1\u7b97\u673a\u7f51\u7edc", "credits": 3.5},
        {"code": "CS499", "name": "\u6bd5\u4e1a\u8bbe\u8ba1", "credits": 8.0},
    ]

    # Mock Prerequisites (Pre -> Post)
    prerequisites = [
        ("CS101", "CS102"),
        ("CS102", "CS201"),
        ("CS202", "CS201"),
        ("CS201", "CS301"),
        ("CS202", "CS301"),
        ("CS201", "CS302"),
        ("CS102", "CS303"),
        ("CS301", "CS499"),
        ("CS302", "CS499"),
        ("CS303", "CS499"),
    ]

    # Mock Graduation Requirements (OBE Weight Validation)
    graduation_requirements = [
        {
            "id": 1,
            "content": "\u5de5\u7a0b\u77e5\u8bc6\uff1a\u80fd\u591f\u5c06\u6570\u5b66\u3001\u81ea\u7136\u79d1\u5b66\u3001\u5de5\u7a0b\u57fa\u7840\u548c\u4e13\u4e1a\u77e5\u8bc6\u7528\u4e8e\u89e3\u51b3\u590d\u6742\u5de5\u7a0b\u95ee\u9898\u3002",
            "indicator_points": [
                {"seq": 1, "content": "\u638c\u63e1\u6570\u5b66\u4e0e\u81ea\u7136\u79d1\u5b66\u77e5\u8bc6", "weight": 0.4},
                {"seq": 2, "content": "\u638c\u63e1\u5de5\u7a0b\u57fa\u7840\u77e5\u8bc6", "weight": 0.3},
                {"seq": 3, "content": "\u638c\u63e1\u4e13\u4e1a\u6838\u5fc3\u77e5\u8bc6", "weight": 0.3},
            ]
        },
        {
            "id": 2,
            "content": "\u95ee\u9898\u5206\u6790\uff1a\u80fd\u591f\u5e94\u7528\u6570\u5b66\u3001\u81ea\u7136\u79d1\u5b66\u548c\u5de5\u7a0b\u79d1\u5b66\u7684\u57fa\u672c\u539f\u7406\uff0c\u8bc6\u522b\u3001\u8868\u8fbe\u3001\u5e76\u901a\u8fc7\u6587\u732e\u7814\u7a76\u5206\u6790\u590d\u6742\u5de5\u7a0b\u95ee\u9898\u3002",
            "indicator_points": [
                {"seq": 1, "content": "\u80fd\u591f\u8bc6\u522b\u548c\u5224\u65ad\u590d\u6742\u5de5\u7a0b\u95ee\u9898\u7684\u5173\u952e\u73af\u8282", "weight": 0.6},
                {"seq": 2, "content": "\u80fd\u5bf9\u590d\u6742\u5de5\u7a0b\u95ee\u9898\u8fdb\u884c\u5efa\u6a21\u548c\u6c42\u89e3", "weight": 0.5},
            ]
        }
    ]
    
    return {
        "courses": courses,
        "prerequisites": prerequisites,
        "graduation_requirements": graduation_requirements
    }

# --- 2. Logic Validation ---

def build_course_graph(courses, prerequisites):
    G = nx.DiGraph()
    for course in courses:
        G.add_node(course["code"], **course)
    for u, v in prerequisites:
        if u in G and v in G:
            G.add_edge(u, v)
    return G

def check_circular_dependency(G):
    try:
        cycle = nx.find_cycle(G, orientation='original')
        return True, cycle
    except nx.NetworkXNoCycle:
        return False, []

def get_recommended_sequence(G):
    if not nx.is_directed_acyclic_graph(G):
        return None
    return list(nx.topological_sort(G))

# --- 3. OBE Validation ---

def validate_weight_completeness(requirement):
    points = requirement.get("indicator_points", [])
    total_weight = sum(Decimal(str(p["weight"])) for p in points)
    is_valid = abs(total_weight - Decimal("1.0")) < Decimal("0.0001")
    
    msg_valid = "\u6743\u91cd\u4e4b\u548c\u7b26\u5408\u8981\u6c42"
    msg_prefix = "\u6743\u91cd\u4e4b\u548c\u4e3a"
    msg_suffix = "\uff0c\u4e0d\u7b49\u4e8e 1.0"
    detail_msg = msg_valid if is_valid else f"{msg_prefix} {total_weight}{msg_suffix}"

    return {
        "requirement_id": requirement["id"],
        "content_preview": requirement["content"][:20] + "...",
        "total_weight": float(total_weight),
        "is_valid": is_valid,
        "details": detail_msg
    }

# --- 4. Service Layer ---

def run_core_logic_demo():
    data = generate_mock_data()
    G = build_course_graph(data["courses"], data["prerequisites"])
    
    has_cycle, cycle_data = check_circular_dependency(G)
    
    sequence_data = []
    if not has_cycle:
        raw_sequence = get_recommended_sequence(G)
        course_map = {c["code"]: c["name"] for c in data["courses"]}
        sequence_data = [
            {"order": idx + 1, "code": code, "name": course_map.get(code, "Unknown")}
            for idx, code in enumerate(raw_sequence)
        ]
    else:
        sequence_data = None

    obe_results = []
    for req in data["graduation_requirements"]:
        res = validate_weight_completeness(req)
        obe_results.append(res)
        
    summary_fail = "\u6743\u91cd\u6821\u9a8c\u5b8c\u6210\uff0c\u53d1\u73b0\u5f02\u5e38"
    summary_pass = "\u6240\u6709\u6743\u91cd\u6821\u9a8c\u901a\u8fc7"
    
    result_payload = {
        "meta": {
            "status": "success",
            "message": "Core logic validation completed"
        },
        "data": {
            "graph_validation": {
                "circular_dependency_detected": has_cycle,
                "cycle_details": cycle_data,
                "is_dag": not has_cycle
            },
            "course_sequence": {
                "can_generate_sequence": not has_cycle,
                "recommended_sequence": sequence_data
            },
            "obe_weight_validation": {
                "summary": summary_fail if any(not r["is_valid"] for r in obe_results) else summary_pass,
                "details": obe_results
            }
        }
    }
    return result_payload

if __name__ == "__main__":
    # Force UTF-8 for stdout
    if sys.platform.startswith('win'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    result = run_core_logic_demo()
    print(json.dumps(result, indent=2, ensure_ascii=False))
