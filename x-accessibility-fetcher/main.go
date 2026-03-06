package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"

	"github.com/gorilla/websocket"
)

type CDPRequest struct {
	ID     int         `json:"id"`
	Method string      `json:"method"`
	Params interface{} `json:"params,omitempty"`
}

type CDPResponse struct {
	ID     int             `json:"id"`
	Result json.RawMessage `json:"result"`
	Error  interface{}     `json:"error"`
}

type AXNode struct {
	NodeID   string    `json:"nodeId"`
	Role     AXValue   `json:"role"`
	Name     AXValue   `json:"name"`
	Value    AXValue   `json:"value"`
	Children []string `json:"childIds"`
}

type AXValue struct {
	Type  string      `json:"type"`
	Value interface{} `json:"value"`
}

func main() {
	targetURL := "ws://localhost:9222/devtools/page/4CBB600FC0229738FCC0C4F8DB94BF22"
	if len(os.Args) > 1 {
		targetURL = os.Args[1]
	}

	c, _, err := websocket.DefaultDialer.Dial(targetURL, nil)
	if err != nil {
		log.Fatalf("Failed to connect to WebSocket: %v", err)
	}
	defer c.Close()

	// 1. Enable Accessibility
	sendCommand(c, 1, "Accessibility.enable", nil)
	readResponse(c) // Read acknowledgement

	// 2. Get Full Accessibility Tree
	sendCommand(c, 2, "Accessibility.getFullAXTree", nil)
	
	for {
		_, message, err := c.ReadMessage()
		if err != nil {
			log.Fatalf("Error reading message: %v", err)
		}

		var resp CDPResponse
		if err := json.Unmarshal(message, &resp); err != nil {
			continue
		}

		if resp.ID == 2 {
			var result struct {
				Nodes []AXNode `json:"nodes"`
			}
			if err := json.Unmarshal(resp.Result, &result); err != nil {
				log.Fatalf("Error parsing AX tree result: %v", err)
			}

			fmt.Println("--- X Page Accessibility Tree Content ---")
			for _, node := range result.Nodes {
				if node.Name.Value != nil {
					nameStr := fmt.Sprintf("%v", node.Name.Value)
					if nameStr != "" {
						role := fmt.Sprintf("%v", node.Role.Value)
						if role == "InlineTextBox" || role == "StaticText" {
							fmt.Printf("%s\n", nameStr)
						} else {
							fmt.Printf("[%s] %s\n", role, nameStr)
						}
					}
				}
				if node.Value.Value != nil {
					valStr := fmt.Sprintf("%v", node.Value.Value)
					if valStr != "" {
						fmt.Printf("   Value: %s\n", valStr)
					}
				}
			}
			break
		}
	}
}

func sendCommand(c *websocket.Conn, id int, method string, params interface{}) {
	req := CDPRequest{
		ID:     id,
		Method: method,
		Params: params,
	}
	err := c.WriteJSON(req)
	if err != nil {
		log.Fatalf("Error sending command %s: %v", method, err)
	}
}

func readResponse(c *websocket.Conn) {
	_, _, err := c.ReadMessage()
	if err != nil {
		log.Fatalf("Error reading response: %v", err)
	}
}
