import json
import requests
import sys
from websocket import create_connection

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def get_target_ws():
    resp = requests.get('http://localhost:9222/json')
    tabs = [t for t in resp.json() if 'x.com' in t.get('url', '') and t.get('type') == 'page']
    return tabs[0].get('webSocketDebuggerUrl') if tabs else None

def send_command(ws, method, params=None, id=1):
    ws.send(json.dumps({"id": id, "method": method, "params": params or {}}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == id:
            return resp.get("result", {})

ws_url = get_target_ws()
if not ws_url:
    print("X tab not found.")
    sys.exit(1)

ws = create_connection(ws_url, suppress_origin=True)
send_command(ws, "Accessibility.enable")
result = send_command(ws, "Accessibility.getFullAXTree")
nodes = result.get("nodes", [])
node_map = {n['nodeId']: n for n in nodes}

def print_clean_tree(node_id, depth=0):
    node = node_map.get(node_id)
    if not node: return
    
    role = node.get("role", {}).get("value", "unknown")
    name = node.get("name", {}).get("value", "")
    
    # 1. Skip redundant InlineTextBox and LineBreak
    if role in ["InlineTextBox", "LineBreak"]:
        return
        
    # 2. Skip generic nodes that have no name or children (except articles)
    if role == "generic" and not name and not node.get("childIds"):
        return

    # 3. Handle StaticText: only print if it has content
    if role == "StaticText":
        if name.strip():
            print("  " * depth + name.strip())
        return # Don't recurse into InlineTextBox children

    indent = "  " * depth
    if name:
        print(f"{indent}[{role}] {name}")
    elif role in ["article", "button", "link", "heading", "navigation"]:
        print(f"{indent}[{role}]")

    for child_id in node.get("childIds", []):
        print_clean_tree(child_id, depth + 1)

root = next((n for n in nodes if n.get("role", {}).get("value") == "RootWebArea"), None)
if root:
    print("--- Optimized X Page View ---")
    print_clean_tree(root['nodeId'])
ws.close()
