#!/usr/bin/env python3
"""
Clear chat conversation context with Cascade agent
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def clear_chat_context():
    """Clear chat conversation context"""
    # Clear any stored conversation history
    clear_patterns = [
        "~/.cascade/conversation_history.json",
        "~/.cascade/session_data.json",
        "~/.cascade/context_cache.json"
    ]
    
    cleared_count = 0
    for pattern in clear_patterns:
        path = Path(pattern).expanduser()
        if path.exists():
            try:
                path.unlink()
                cleared_count += 1
                print(f"Cleared: {path}")
            except Exception as e:
                print(f"Failed to clear {path}: {e}")
    
    # Create a clear marker file
    marker_path = Path.home() / ".cascade" / "last_cleared.txt"
    marker_path.parent.mkdir(exist_ok=True)
    marker_path.write_text(f"Cleared at: {datetime.now().isoformat()}")
    
    print(f"\n✅ Chat context cleared successfully!")
    print(f"📁 Cleared {cleared_count} context files")
    print(f"⏰ Clear timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n💡 Start fresh with your next message!")

if __name__ == "__main__":
    clear_chat_context()
