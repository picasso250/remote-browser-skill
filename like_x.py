import json
import requests
import sys
import time
from websocket import create_connection

def get_target_ws():
    resp = requests.get('http://localhost:9222/json')
    tabs = [t for t in resp.json() if 'x.com' in t.get('url', '') and t.get('type') == 'page']
    return tabs[0].get('webSocketDebuggerUrl') if tabs else None

def send_command(ws, method, params=None, id=1):
    ws.send(json.dumps({"id": id, "method": method, "params": params or {}}))
    while True:
        resp = json.loads(ws.recv())
        if resp.get("id") == id:
            if "error" in resp:
                print(f"Error in {method}: {resp['error']}")
                return None
            return resp.get("result", {})

def perform_like(keyword_author, keyword_content):
    ws_url = get_target_ws()
    if not ws_url:
        print("X tab not found.")
        return
    
    ws = create_connection(ws_url, suppress_origin=True)
    send_command(ws, "Accessibility.enable")
    tree = send_command(ws, "Accessibility.getFullAXTree")
    nodes = tree.get("nodes", [])

    target_article_id = None
    for node in nodes:
        if node.get("role", {}).get("value") == "article":
            name = node.get("name", {}).get("value", "")
            if keyword_author in name and keyword_content in name:
                target_article_id = node['nodeId']
                break

    if not target_article_id:
        print(f"Could not find tweet by {keyword_author} containing '{keyword_content}'.")
        ws.close()
        return

    def find_like_button(node_id):
        node = next((n for n in nodes if n['nodeId'] == node_id), None)
        if not node: return None
        role = node.get("role", {}).get("value")
        name = node.get("name", {}).get("value", "")
        if role == "button" and ("喜欢" in name or "Like" in name):
            return node
        for child_id in node.get("childIds", []):
            res = find_like_button(child_id)
            if res: return res
        return None

    like_button_node = find_like_button(target_article_id)
    if not like_button_node:
        print("Could not find Like button.")
        ws.close()
        return

    backend_id = like_button_node.get("backendDOMNodeId")
    box = send_command(ws, "DOM.getBoxModel", {"backendNodeId": backend_id})
    if not box:
        print("Could not get box model.")
        ws.close()
        return

    quad = box['model']['content']
    center_x = (quad[0] + quad[2] + quad[4] + quad[6]) / 4
    center_y = (quad[1] + quad[3] + quad[5] + quad[7]) / 4

    # Simulate physical click
    send_command(ws, "Input.dispatchMouseEvent", {"type": "mouseMoved", "x": center_x, "y": center_y})
    send_command(ws, "Input.dispatchMouseEvent", {"type": "mousePressed", "x": center_x, "y": center_y, "button": "left", "clickCount": 1})
    send_command(ws, "Input.dispatchMouseEvent", {"type": "mouseReleased", "x": center_x, "y": center_y, "button": "left", "clickCount": 1})
    
    print(f"Successfully liked tweet by {keyword_author} at ({center_x}, {center_y})")
    ws.close()

if __name__ == "__main__":
    author = sys.argv[1] if len(sys.argv) > 1 else "ruanyf"
    content = sys.argv[2] if len(sys.argv) > 2 else "知识付费"
    perform_like(author, content)
