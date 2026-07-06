#!/bin/bash
# SuperBot Startup Script
# Starts both API server and Dashboard

echo "🤖 Starting SuperBot System..."
echo ""

# Check if running in virtual environment
if [ ! -d ".venv" ]; then
    echo "⚠️  No .venv found. Make sure dependencies are installed."
    echo "   Install with: pip install fastapi uvicorn streamlit requests pandas plotly python-multipart"
fi

# Start API server in background
echo "🚀 Starting API Server on port 8000..."
python -m st_lms.api.superbot_api &
API_PID=$!
echo "   API PID: $API_PID"

# Wait for API to start
sleep 3

# Start Dashboard
echo "📊 Starting Dashboard on port 8501..."
streamlit run st_lms/dashboard/superbot_dashboard.py --server.port 8501 &
DASHBOARD_PID=$!
echo "   Dashboard PID: $DASHBOARD_PID"

echo ""
echo "✅ SuperBot System Started!"
echo ""
echo "📍 API Server: http://localhost:8000"
echo "📍 Dashboard:  http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
wait
