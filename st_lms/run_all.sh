#!/bin/bash

# ST_LMS Run All Script
# Default Port: 8085 (Bot), 3000 (Dashboard)
# Menjalankan Bot Server dan Dashboard secara bersamaan

echo "🚀 Starting ST_LMS System..."

# Configuration
BOT_PORT=${BOT_PORT:-8085}
DASHBOARD_PORT=${DASHBOARD_PORT:-3000}
MODE=${MODE:-simulator}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}Warning: Port $1 is already in use.${NC}"
        return 1
    else
        return 0
    fi
}

# Kill existing processes on target ports (optional cleanup)
cleanup_ports() {
    echo "Cleaning up existing processes on ports $BOT_PORT and $DASHBOARD_PORT..."
    fuser -k ${BOT_PORT}/tcp 2>/dev/null || true
    fuser -k ${DASHBOARD_PORT}/tcp 2>/dev/null || true
    sleep 1
}

# Start Bot Server
start_bot() {
    echo -e "${GREEN}Starting ST_LMS Bot Server on port ${BOT_PORT} (${MODE} mode)...${NC}"
    cd /workspace/st_lms
    
    # Run in background
    python main_server.py --port ${BOT_PORT} --mode ${MODE} &
    BOT_PID=$!
    echo "Bot PID: $BOT_PID"
    
    # Wait a moment for startup
    sleep 2
    
    if ps -p $BOT_PID > /dev/null; then
        echo -e "${GREEN}✅ Bot Server started successfully.${NC}"
    else
        echo -e "${RED}❌ Failed to start Bot Server.${NC}"
        exit 1
    fi
}

# Start Dashboard Server
start_dashboard() {
    echo -e "${GREEN}Starting ST_LMS Dashboard on port ${DASHBOARD_PORT}...${NC}"
    cd /workspace/st_lms/dashboard
    
    # Check if dashboard_server.py exists, otherwise suggest static mode
    if [ -f "dashboard_server.py" ]; then
        python dashboard_server.py --port ${DASHBOARD_PORT} &
        DASH_PID=$!
        echo "Dashboard PID: $DASH_PID"
        sleep 2
        if ps -p $DASH_PID > /dev/null; then
            echo -e "${GREEN}✅ Dashboard Server started successfully.${NC}"
        else
            echo -e "${YELLOW}⚠️ Dashboard server failed, try opening st_lms_dashboard.html directly.${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️ dashboard_server.py not found. Please open st_lms/dashboard/st_lms_dashboard.html in your browser manually.${NC}"
    fi
}

# Main Execution
echo "----------------------------------------"
echo "ST_LMS Configuration:"
echo "  Bot Port:      ${BOT_PORT}"
echo "  Dashboard Port: ${DASHBOARD_PORT}"
echo "  Mode:          ${MODE}"
echo "----------------------------------------"

# Optional: Cleanup previous runs
# cleanup_ports

# Start Services
start_bot
start_dashboard

echo ""
echo "========================================"
echo -e "${GREEN}🎉 ST_LMS System is Running!${NC}"
echo "========================================"
echo ""
echo "Access Points:"
echo "  🤖 Bot API:      http://localhost:${BOT_PORT}"
echo "  📊 Dashboard:    http://localhost:${DASHBOARD_PORT}"
echo "  📄 Static Dash:  file:///workspace/st_lms/dashboard/st_lms_dashboard.html"
echo ""
echo "To Stop the system:"
echo "  kill $BOT_PID  (Bot)"
echo "  kill $DASH_PID (Dashboard)"
echo "  Or press Ctrl+C in this terminal if running in foreground mode."
echo ""
echo "Logs will appear below..."
echo "----------------------------------------"

# Keep script running to show logs (optional)
# If you want to detach completely, remove the 'wait' command
wait
