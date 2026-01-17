#!/usr/bin/env python3
"""
Debug workflow for generating debugging reports with model recommendations
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def generate_debug_report():
    """Generate debugging report with model recommendations"""
    
    debug_data = {
        "timestamp": datetime.now().isoformat(),
        "debug_id": f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "system_info": {},
        "environment": {},
        "model_recommendations": {},
        "issues_found": []
    }
    
    # Gather system information
    try:
        # Python version
        debug_data["system_info"]["python_version"] = sys.version
        
        # Current directory
        debug_data["system_info"]["current_dir"] = str(Path.cwd())
        
        # Environment variables (safe ones)
        safe_env_vars = ["PATH", "HOME", "USER", "SHELL"]
        debug_data["environment"] = {
            var: os.environ.get(var, "Not set") 
            for var in safe_env_vars
        }
        
        # Check for common debugging tools
        tools_check = {
            "gdb": subprocess.run(["which", "gdb"], capture_output=True).returncode == 0,
            "lldb": subprocess.run(["which", "lldb"], capture_output=True).returncode == 0,
            "python_debugger": True,  # Always available with Python
        }
        debug_data["system_info"]["debugging_tools"] = tools_check
        
    except Exception as e:
        debug_data["issues_found"].append(f"Error gathering system info: {e}")
    
    # Model recommendations based on task type
    debug_data["model_recommendations"] = {
        "code_debugging": {
            "primary": "Claude 3.5 Sonnet",
            "reasoning": "Excellent at understanding complex code patterns and identifying bugs",
            "alternative": "GPT-4o",
            "alternative_reasoning": "Fast and good for quick debugging"
        },
        "system_analysis": {
            "primary": "Claude 3.5 Sonnet", 
            "reasoning": "Strong analytical capabilities for system-level issues",
            "alternative": "GPT-4o-mini",
            "alternative_reasoning": "Cost-effective for simple system issues"
        },
        "performance_optimization": {
            "primary": "Claude 3.5 Sonnet",
            "reasoning": "Best for understanding performance bottlenecks",
            "alternative": "GPT-4o",
            "alternative_reasoning": "Good for quick optimization suggestions"
        }
    }
    
    # Generate report output
    print("🐛 Debug Report Generated")
    print("=" * 50)
    print(f"📅 Timestamp: {debug_data['timestamp']}")
    print(f"🆔 Debug ID: {debug_data['debug_id']}")
    
    print("\n💻 System Information:")
    for key, value in debug_data["system_info"].items():
        print(f"  {key}: {value}")
    
    print("\n🔧 Model Recommendations:")
    for task, models in debug_data["model_recommendations"].items():
        print(f"\n  {task.replace('_', ' ').title()}:")
        print(f"    Primary: {models['primary']}")
        print(f"    Reason: {models['reasoning']}")
        print(f"    Alternative: {models['alternative']}")
        print(f"    Alternative Reason: {models['alternative_reasoning']}")
    
    if debug_data["issues_found"]:
        print(f"\n⚠️  Issues Found: {len(debug_data['issues_found'])}")
        for issue in debug_data["issues_found"]:
            print(f"  - {issue}")
    else:
        print("\n✅ No issues detected")
    
    print(f"\n📊 Debug report complete!")
    return debug_data

if __name__ == "__main__":
    generate_debug_report()
