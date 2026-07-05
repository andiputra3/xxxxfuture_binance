"""
ST_LMS Dashboard Server - VERSI LENGKAP
Menyajikan dashboard HTML dan menyediakan API data real-time dari seluruh sistem ST_LMS.
Mendukung Simulator, Testnet, dan Live Trading dengan pelacakan pipeline lengkap.
"""
import http.server
import socketserver
import json
import threading
import time
import argparse
import os
from pathlib import Path
from datetime import datetime

# Import sistem ST_LMS yang sebenarnya
try:
    from st_lms.core.telemetry import telemetry, PipelineStage
    from st_lms.pipeline import ST_LMS_Pipeline
    from st_lms.config.config_manager import ConfigManager
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    print("⚠️  Warning: ST_LMS modules not fully imported. Running in mock mode.")

# Konfigurasi Server
parser = argparse.ArgumentParser(description='ST_LMS Dashboard Server')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host address (default: 0.0.0.0)')
parser.add_argument('--port', type=int, default=8000, help='Port number (default: 8000)')
parser.add_argument('--mode', type=str, choices=['simulator', 'testnet', 'live'], default='simulator', 
                    help='Trading mode (default: simulator)')
args = parser.parse_args()

PORT = args.port
HOST = args.host
TRADING_MODE = args.mode
DIRECTORY = Path(__file__).parent

class BotState:
    """Menyimpan state bot secara global untuk diakses server"""
    def __init__(self):
        self.status = "INITIALIZING"
        self.mode = TRADING_MODE
        self.balance = 10000.0
        self.equity = 10000.0
        self.pnl_today = 0.0
        self.structural_state = "UNKNOWN"
        self.authorization = "PENDING"
        self.river_confidence = 0.0
        self.darwin_status = "Idle"
        self.active_position = None
        self.recent_trades = []
        self.pipeline_history = []
        self.market_structure = {}
        self.learning_summary = {
            "river_recommendation": "UNKNOWN",
            "opportunity_cost_tracked": 0,
            "total_learned_trades": 0,
            "darwin_improvements": 0
        }
        self.last_update = datetime.now().isoformat()
        self.current_cycle_id = None
        
bot_state = BotState()

class STLMSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

    def do_GET(self):
        if self.path == '/api/data':
            self.send_json_response(bot_state.__dict__)
        elif self.path == '/api/pipeline/current':
            if SYSTEM_AVAILABLE:
                cycle_log = telemetry.get_current_cycle_log()
                self.send_json_response({"cycle_id": bot_state.current_cycle_id, "steps": cycle_log})
            else:
                self.send_json_response({"cycle_id": None, "steps": []})
        elif self.path == '/api/pipeline/history':
            self.send_json_response({"history": bot_state.pipeline_history[-50:]})
        elif self.path == '/api/river/learning':
            if SYSTEM_AVAILABLE:
                river_summary = telemetry.get_river_learning_summary()
                self.send_json_response(river_summary)
            else:
                self.send_json_response(bot_state.learning_summary)
        elif self.path == '/api/darwin/status':
            if SYSTEM_AVAILABLE:
                darwin_status = telemetry.get_darwin_status()
                self.send_json_response(darwin_status)
            else:
                self.send_json_response({"status": bot_state.darwin_status, "improvements": 0})
        elif self.path == '/api/market/structure':
            self.send_json_response(bot_state.market_structure)
        elif self.path == '/api/trades/recent':
            self.send_json_response({"trades": bot_state.recent_trades[-20:]})
        elif self.path == '/api/system/info':
            self.send_json_response({
                "mode": bot_state.mode,
                "status": bot_state.status,
                "system_available": SYSTEM_AVAILABLE,
                "uptime": datetime.now().isoformat()
            })
        elif self.path == '/':
            self.path = '/st_lms_dashboard.html'
            return super().do_GET()
        else:
            return super().do_GET()
    
    def do_POST(self):
        content_length = int(self.headers['ContentLength'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        if self.path == '/api/control/start':
            bot_state.status = "RUNNING"
            self.send_json_response({"status": "success", "message": "Bot started"})
        elif self.path == '/api/control/stop':
            bot_state.status = "STOPPED"
            self.send_json_response({"status": "success", "message": "Bot stopped"})
        elif self.path == '/api/control/reset':
            bot_state.pipeline_history = []
            bot_state.recent_trades = []
            self.send_json_response({"status": "success", "message": "Data reset"})
        else:
            self.send_error(404)
    
    def send_json_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def update_bot_state_from_telemetry():
    global bot_state
    if not SYSTEM_AVAILABLE:
        return
    
    while True:
        time.sleep(1)
        try:
            recent_events = telemetry.get_recent_events(10)
            if recent_events:
                last_event = recent_events[-1]
                bot_state.pipeline_history.append(last_event)
                
                if "Execute" in last_event["stage"]:
                    bot_state.status = "EXECUTING"
                elif "Authorize" in last_event["stage"]:
                    bot_state.authorization = last_event["details"].get("decision", "PENDING")
                elif "Classify" in last_event["stage"]:
                    bot_state.structural_state = last_event["details"].get("state", "UNKNOWN")
            
            river_summary = telemetry.get_river_learning_summary()
            bot_state.learning_summary = {
                "river_recommendation": river_summary.get("last_recommendation", "UNKNOWN"),
                "river_confidence": river_summary.get("confidence", 0),
                "opportunity_cost_tracked": river_summary.get("opportunity_cost_tracked", False),
                "total_learned_trades": river_summary.get("total_learned_trades", 0)
            }
            
            darwin_status = telemetry.get_darwin_status()
            bot_state.darwin_status = darwin_status.get("status", "Idle")
            bot_state.learning_summary["darwin_improvements"] = darwin_status.get("improvements_made", 0)
            
            bot_state.last_update = datetime.now().isoformat()
            
        except Exception as e:
            print(f"[Dashboard] Error updating state: {e}")

def simulate_bot_activity():
    global bot_state
    import random
    
    while True:
        time.sleep(3)
        if bot_state.status != "RUNNING":
            continue
            
        change = random.uniform(-50, 50)
        if bot_state.active_position:
            bot_state.active_position["current"] += change
            bot_state.active_position["unrealized_pnl"] = (
                (bot_state.active_position["current"] - bot_state.active_position["entry"]) * 
                bot_state.active_position.get("quantity", 0.01)
            )
            bot_state.equity = bot_state.balance + bot_state.active_position["unrealized_pnl"]
        else:
            bot_state.equity = bot_state.balance
            
        bot_state.pnl_today = bot_state.equity - bot_state.balance
        
        stages = [
            "C001 - Observe", "C002 - Measure", "C003 - Multi-TF Structure",
            "C006 - Select", "C008 - Classify", "C009 - Trading Plan",
            "C010 - River Review", "C011 - Authorize"
        ]
        bot_state.pipeline_stage = random.choice(stages)
        
        if random.random() < 0.1 and not bot_state.active_position:
            entry_price = random.uniform(60000, 70000)
            bot_state.active_position = {
                "side": random.choice(["LONG", "SHORT"]),
                "entry": entry_price,
                "current": entry_price,
                "quantity": 0.01,
                "unrealized_pnl": 0
            }
            bot_state.status = "IN_POSITION"
            
        print(f"[Dashboard] Mode: {bot_state.mode} | Status: {bot_state.status} | Equity: ${bot_state.equity:.2f}")

if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"ST_LMS Dashboard Server - VERSI LENGKAP")
    print(f"{'='*60}")
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Mode: {TRADING_MODE.upper()}")
    print(f"Directory: {DIRECTORY}")
    print(f"System Integration: {'AVAILABLE' if SYSTEM_AVAILABLE else 'MOCK MODE'}")
    print(f"{'='*60}\n")
    
    if SYSTEM_AVAILABLE:
        telemetry_thread = threading.Thread(target=update_bot_state_from_telemetry, daemon=True)
        telemetry_thread.start()
        print("Telemetry integration active")
    
    sim_thread = threading.Thread(target=simulate_bot_activity, daemon=True)
    sim_thread.start()
    
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer((HOST, PORT), STLMSHandler) as httpd:
        print(f"\nDashboard ready at: http://{HOST}:{PORT}")
        print("API Endpoints:")
        print("   GET  /api/data              -> Full bot status")
        print("   GET  /api/pipeline/current  -> Detail pipeline cycle saat ini")
        print("   GET  /api/pipeline/history  -> Riwayat pipeline")
        print("   GET  /api/river/learning    -> Pembelajaran River")
        print("   GET  /api/darwin/status     -> Status Darwin")
        print("   GET  /api/market/structure  -> Market Structure detail")
        print("   GET  /api/trades/recent     -> Riwayat transaksi")
        print("   POST /api/control/start     -> Start bot")
        print("   POST /api/control/stop      -> Stop bot")
        print("   POST /api/control/reset     -> Reset data")
        print(f"\nPress Ctrl+C to stop\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nServer stopped by user.")
