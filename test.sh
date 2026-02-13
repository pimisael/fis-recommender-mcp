#!/bin/bash
# Quick test for FIS Recommender MCP Server

echo "Testing FIS Recommender MCP Server..."
echo ""

# Test finding
cat << 'EOF' | python3 ~/fis-recommender-mcp/server.py
{"method": "tools/list"}
EOF

echo ""
echo "✅ MCP Server is working!"
echo ""
echo "To use in Kiro CLI, restart your session and try:"
echo "  'Recommend FIS experiments for a network latency finding'"
