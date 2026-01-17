import asyncio
import os
from kasa import SmartPlug
from openai import OpenAI

# --- CONFIGURATION ---
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")
PLUG_IP = "192.168.6.130"  # Replace with the IP from Step 2
# ---------------------

client = OpenAI(api_key=OPENAI_KEY)

async def brew_coffee():
    plug = SmartPlug(PLUG_IP)
    await plug.update()
    
    # Turn on the machine
    await plug.turn_on()
    print("\n[AI] Brewing started! Smells like progress.")
    
    # SAFETY: Wait 10 minutes then turn off automatically
    # This prevents the machine from staying on all day.
    print("[System] Safety timer set: Power will cut in 10 minutes.")
    await asyncio.sleep(600) 
    await plug.turn_off()
    print("[System] Power off. Stay caffeinated!")

def get_ai_decision(user_prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a coffee machine controller. If the user wants coffee, needs energy, or explicitly says START, you MUST respond with the single word 'START'. For any other interaction, respond politely as a barista."},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

async def main():
    print("Coffee Agent is listening...")
    user_input = input("How are you feeling? ")
    
    decision = get_ai_decision(user_input)
    
    if "START" in decision.upper():
        await brew_coffee()
    else:
        print(f"AI: {decision}")

if __name__ == "__main__":
    asyncio.run(main())