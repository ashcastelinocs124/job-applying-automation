import asyncio
import os
import sys
from kasa import SmartPlug
from openai import OpenAI

# --- CONFIGURATION ---
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
PLUG_IP = "192.168.6.130"

async def check_plug():
    print(f"Checking Kasa Plug at {PLUG_IP}...")
    try:
        plug = SmartPlug(PLUG_IP)
        await plug.update()
        print(f"✅ Kasa Connected: {plug.alias}")
        print(f"   State: {'ON' if plug.is_on else 'OFF'}")
        print(f"   Signal (RSSI): {plug.rssi} dBm")
        return True
    except Exception as e:
        print(f"❌ Kasa Connection Failed: {e}")
        return False

def check_openai():
    print("Checking OpenAI Connection...")
    try:
        client = OpenAI(api_key=OPENAI_KEY)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=5
        )
        print("✅ OpenAI Connected: Received response")
        return True
    except Exception as e:
        print(f"❌ OpenAI Connection Failed: {e}")
        return False

async def run_checks():
    print("=== SYSTEM STATUS CHECK ===\n")
    kasa_ok = await check_plug()
    print("-" * 30)
    openai_ok = check_openai()
    print("\n" + "=" * 30)
    
    if kasa_ok and openai_ok:
        print("ALL SYSTEMS NOMINAL ☕️")
    else:
        print("SOME CHECKS FAILED. Please check logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_checks())
