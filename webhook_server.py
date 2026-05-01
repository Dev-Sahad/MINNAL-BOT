# =============================================================================
#  webhook_server.py — Webhook Server for Bot ↔ Web Communication
#  Real-time updates between Discord bot and Netlify web panel
# =============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
import secrets
import threading

app = Flask(__name__)
CORS(app)  # Allow requests from Netlify

# Data files
DATA_DIR = 'data'
STATS_FILE = f'{DATA_DIR}/bot_stats.json'
CONFIG_FILE = f'{DATA_DIR}/web_config.json'
WEBHOOK_LOG = f'{DATA_DIR}/webhook_log.json'

# Security
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', secrets.token_urlsafe(32))

def ensure_data_files():
    """Create data directory and files if they don't exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    for file in [STATS_FILE, CONFIG_FILE, WEBHOOK_LOG]:
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump({}, f)

def load_json(filepath):
    """Load JSON data from file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_json(filepath, data):
    """Save JSON data to file"""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

def log_webhook(event_type, data):
    """Log webhook events"""
    logs = load_json(WEBHOOK_LOG)
    timestamp = datetime.utcnow().isoformat()
    
    if 'events' not in logs:
        logs['events'] = []
    
    logs['events'].append({
        'timestamp': timestamp,
        'type': event_type,
        'data': data
    })
    
    # Keep only last 100 events
    logs['events'] = logs['events'][-100:]
    save_json(WEBHOOK_LOG, logs)

# ══════════════════════════════════════════════════════════════════════════════
# WEBHOOK ENDPOINTS
# ══════════════════════════════════════════════════════════════════════════════

@app.route('/webhook/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'service': 'MINNAL Webhook Server',
        'timestamp': datetime.utcnow().isoformat()
    })

# ── Bot → Web: Send Stats ────────────────────────────────────────────────────
@app.route('/webhook/bot/stats', methods=['POST'])
def receive_bot_stats():
    """Receive bot statistics from Discord bot"""
    try:
        # Verify secret
        secret = request.headers.get('X-Webhook-Secret')
        if secret != WEBHOOK_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        
        # Save stats
        save_json(STATS_FILE, {
            'status': data.get('status', 'online'),
            'uptime': data.get('uptime'),
            'servers': data.get('servers'),
            'members': data.get('members'),
            'channels': data.get('channels'),
            'latency': data.get('latency'),
            'commands_today': data.get('commands_today'),
            'economy_users': data.get('economy_users', 0),
            'total_coins': data.get('total_coins', 0),
            'last_update': datetime.utcnow().isoformat()
        })
        
        log_webhook('bot_stats', data)
        
        return jsonify({
            'success': True,
            'message': 'Stats received'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Bot → Web: Send Event ────────────────────────────────────────────────────
@app.route('/webhook/bot/event', methods=['POST'])
def receive_bot_event():
    """Receive events from Discord bot (member join, command used, etc.)"""
    try:
        secret = request.headers.get('X-Webhook-Secret')
        if secret != WEBHOOK_SECRET:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        event_type = data.get('event_type')
        
        # Update counters based on event
        config = load_json(CONFIG_FILE)
        
        if event_type == 'member_join':
            config['new_members_today'] = config.get('new_members_today', 0) + 1
        
        elif event_type == 'command_used':
            config['commands_today'] = config.get('commands_today', 0) + 1
            
            # Track command usage
            if 'command_stats' not in config:
                config['command_stats'] = {}
            
            cmd_name = data.get('command_name')
            config['command_stats'][cmd_name] = config['command_stats'].get(cmd_name, 0) + 1
        
        elif event_type == 'member_leave':
            config['members_left_today'] = config.get('members_left_today', 0) + 1
        
        save_json(CONFIG_FILE, config)
        log_webhook(event_type, data)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Web → Bot: Get Stats ─────────────────────────────────────────────────────
@app.route('/webhook/web/stats', methods=['GET'])
def send_stats_to_web():
    """Web panel requests current bot stats"""
    try:
        # Verify token
        token = request.headers.get('Authorization')
        config = load_json(CONFIG_FILE)
        
        if token != f"Bearer {config.get('server_token')}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        stats = load_json(STATS_FILE)
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Web → Bot: Update Settings ───────────────────────────────────────────────
@app.route('/webhook/web/settings', methods=['POST'])
def receive_web_settings():
    """Receive settings updates from web panel"""
    try:
        token = request.headers.get('Authorization')
        config = load_json(CONFIG_FILE)
        
        if token != f"Bearer {config.get('server_token')}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        setting_type = data.get('type')
        
        # Update config based on setting type
        if setting_type == 'channel':
            channel_type = data.get('channel_type')
            channel_id = data.get('channel_id')
            config[f'{channel_type}_channel_id'] = channel_id
        
        elif setting_type == 'economy':
            if 'economy_settings' not in config:
                config['economy_settings'] = {}
            config['economy_settings'].update(data.get('settings', {}))
        
        elif setting_type == 'feature':
            feature_name = data.get('feature_name')
            enabled = data.get('enabled')
            if 'features' not in config:
                config['features'] = {}
            config['features'][feature_name] = enabled
        
        save_json(CONFIG_FILE, config)
        log_webhook('settings_update', data)
        
        return jsonify({
            'success': True,
            'message': 'Settings updated'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Web → Bot: Execute Command ───────────────────────────────────────────────
@app.route('/webhook/web/command', methods=['POST'])
def receive_web_command():
    """Receive command requests from web panel"""
    try:
        token = request.headers.get('Authorization')
        config = load_json(CONFIG_FILE)
        
        if token != f"Bearer {config.get('server_token')}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.json
        command = data.get('command')
        
        # Store command for bot to pick up
        if 'pending_commands' not in config:
            config['pending_commands'] = []
        
        config['pending_commands'].append({
            'command': command,
            'params': data.get('params', {}),
            'timestamp': datetime.utcnow().isoformat(),
            'id': secrets.token_urlsafe(8)
        })
        
        save_json(CONFIG_FILE, config)
        log_webhook('web_command', data)
        
        return jsonify({
            'success': True,
            'message': 'Command queued'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Get Webhook Logs ─────────────────────────────────────────────────────────
@app.route('/webhook/logs', methods=['GET'])
def get_webhook_logs():
    """Get recent webhook activity logs"""
    try:
        token = request.headers.get('Authorization')
        config = load_json(CONFIG_FILE)
        
        if token != f"Bearer {config.get('server_token')}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        logs = load_json(WEBHOOK_LOG)
        return jsonify(logs)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ── Get Command Stats ────────────────────────────────────────────────────────
@app.route('/webhook/web/command-stats', methods=['GET'])
def get_command_stats():
    """Get command usage statistics"""
    try:
        token = request.headers.get('Authorization')
        config = load_json(CONFIG_FILE)
        
        if token != f"Bearer {config.get('server_token')}":
            return jsonify({'error': 'Unauthorized'}), 401
        
        stats = {
            'commands_today': config.get('commands_today', 0),
            'command_breakdown': config.get('command_stats', {}),
            'new_members_today': config.get('new_members_today', 0),
            'members_left_today': config.get('members_left_today', 0)
        }
        
        return jsonify(stats)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ══════════════════════════════════════════════════════════════════════════════
# SERVER STARTUP
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    ensure_data_files()
    
    print("=" * 80)
    print("⚡ MINNAL WEBHOOK SERVER")
    print("=" * 80)
    print(f"🔐 Webhook Secret: {WEBHOOK_SECRET}")
    print(f"🌐 Server starting on port 5000...")
    print(f"📊 Health check: http://localhost:5000/webhook/health")
    print("=" * 80)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
