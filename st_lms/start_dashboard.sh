#!/bin/bash
#
# ST_LMS Dashboard Launcher
# Runs the Live Simulation Dashboard on 0.0.0.0:8083
#

# Go to project root
cd "$(dirname "$0")" || exit 1

echo "=========================================="
echo "  ST_LMS Dashboard - Live Simulation"
echo "=========================================="
echo ""
echo "Starting Streamlit on http://0.0.0.0:8083"
echo "Press Ctrl+C to stop"
echo ""

# Run Streamlit
streamlit run dashboard/app.py \
    --server.address 0.0.0.0 \
    --server.port 8083 \
    --server.headless true
