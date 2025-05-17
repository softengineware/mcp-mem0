import requests
import json
import os
import time
import threading
import atexit

# Configuration
MCP_URL = "http://localhost:8050/sse"
POLL_INTERVAL = 2  # seconds

class AutoMemoryPlugin:
    def __init__(self):
        self.last_conversation_id = None
        self.last_message_id = None
        self.running = True
        self.thread = None
        
    def start(self):
        """Start the polling thread to monitor conversations"""
        self.thread = threading.Thread(target=self._poll_conversations)
        self.thread.daemon = True
        self.thread.start()
        atexit.register(self.stop)
        print("Auto Memory Plugin started. All conversations will be saved automatically.")
    
    def stop(self):
        """Stop the polling thread"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)
        print("Auto Memory Plugin stopped.")
    
    def _poll_conversations(self):
        """Continuously poll for new messages in conversations"""
        while self.running:
            try:
                # This is a placeholder for how you would access Claude Code conversations
                # In practice, you would need to use an actual API or file monitoring
                new_messages = self._get_new_messages()
                
                for message in new_messages:
                    self._save_message(message["role"], message["content"])
                    
                    # Update tracking
                    self.last_message_id = message.get("id")
                    self.last_conversation_id = message.get("conversation_id")
                
            except Exception as e:
                print(f"Error polling conversations: {str(e)}")
            
            time.sleep(POLL_INTERVAL)
    
    def _get_new_messages(self):
        """Placeholder for getting new messages from Claude Code"""
        # In a real implementation, this would access messages via an API or file
        return []
    
    def _save_message(self, role, content):
        """Save a message to the MCP server"""
        try:
            payload = {
                "tool": "auto_save_message",
                "params": {
                    "role": role,
                    "content": content
                }
            }
            
            # Call the MCP server
            response = requests.post(
                MCP_URL,
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                print(f"Successfully saved {role} message")
            else:
                print(f"Failed to save message: {response.status_code} {response.text}")
        
        except Exception as e:
            print(f"Error saving message: {str(e)}")

# Usage
if __name__ == "__main__":
    plugin = AutoMemoryPlugin()
    plugin.start()
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        plugin.stop()