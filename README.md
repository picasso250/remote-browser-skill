# Remote Browser Control Skill

A Gemini CLI skill to control a remote Chrome/Brave browser via WebSocket and Chrome DevTools Protocol (CDP). This skill uses the **Accessibility Tree** to understand page content and simulates physical interactions like mouse clicks.

## Features

- **Semantic Scraping**: Fetch page content using the Accessibility Tree (AX Tree) which is more stable than traditional CSS selectors.
- **Physical Interaction**: Simulate real mouse clicks using coordinates calculated from the AX Tree nodes.
- **Python-based**: Robust UTF-8 handling and easy integration with Gemini CLI.

## Requirements

- **Brave/Chrome Browser** with remote debugging enabled:
  `powershell
  & "brave.exe" --remote-debugging-port=9222
  `
- **Python 3.x**
- **Dependencies**:
  `ash
  pip install websocket-client requests
  `

## Scripts

### 1. etch_x.py
Fetches and displays an optimized, token-efficient view of the current X (Twitter) home timeline.
`ash
python fetch_x.py
`

### 2. like_x.py
Simulates a physical mouse click to "Like" a specific tweet by author and content keywords.
`ash
# Default: Like ruanyf's tweet about "知识付费"
python like_x.py

# Custom: Like a specific user's tweet
python like_x.py "elonmusk" "Grok"
`

## Why Accessibility Tree?
Unlike traditional DOM-based scraping, the AX Tree reflects the semantic structure of the page. It is resilient to React class name obfuscation and provides a clear hierarchy of interactive elements (articles, buttons, links) as perceived by assistive technologies.
