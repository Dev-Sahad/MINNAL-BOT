import os
import threading
import asyncio
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler


def run_web_server():
    """Web server for admin panel"""
    PORT = int(os.getenv('PORT', 8080))
    
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.path = '/advanced-admin-panel.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            super().end_headers()
        
        def log_message(self, format, *args):
            pass
    
    try:
        server = HTTPServer(('0.0.0.0', PORT), Handler)
        print(f'🌐 Web Panel running on port {PORT}', flush=True)
        server.serve_forever()
    except Exception as e:
        print(f'❌ Web server error: {e}', flush=True)


# Start web server in background thread BEFORE bot starts
print('🌐 Starting web server thread...', flush=True)
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()

# Give web server 3 seconds to start
time.sleep(3)
print('🌐 Web server should be running!', flush=True)

# Now start the Discord bot
print('🤖 Starting Discord bot...', flush=True)
import discord_bot
asyncio.run(discord_bot.main())