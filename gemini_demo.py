import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure the local browser-use package is picked up
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environmental variables from .env file
load_dotenv()

# Check for API keys
gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")

if not gemini_key:
    print("=" * 80)
    print("⚠️  GEMINI_API_KEY / GOOGLE_API_KEY is not set!")
    print("To run this demo with the Gemini model, please set your API key:")
    print("1. Get a free API key from Google AI Studio:")
    print("   https://aistudio.google.com/")
    print("2. Set the environment variable in your terminal, or paste it in '.env' as:")
    print("   GEMINI_API_KEY=your_copied_api_key_here")
    print("=" * 80)
    sys.exit(1)

from browser_use import Agent, ChatGoogle, Browser
from browser_use.browser.events import SwitchTabEvent
import socket

def is_chrome_debugging_port_open(port=9222):
    """Check if Chrome's debugging port is open on localhost."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex(('127.0.0.1', port)) == 0
    except Exception:
        return False

async def main():
    # Use 'gemini-2.5-flash' – Google's flagship free-tier fast model
    model_name = 'gemini-2.5-flash'
    
    print(f"🤖 Initializing Gemini Agent with model: {model_name}...")
    llm = ChatGoogle(model=model_name)
    
    print("🔍 Checking if Google Chrome is listening on port 9222...")
    if not is_chrome_debugging_port_open(9222):
        print("=" * 80)
        print("❌ Port 9222 is CLOSED! Your Google Chrome is not configured for remote debugging.")
        print("\n💡 WHY THIS HAPPENED:")
        print("   If Google Chrome is already running on Windows (even in the background),")
        print("   simply opening a new shortcut ignores the '--remote-debugging-port' flag.")
        print("\n🔧 HOW TO FIX THIS (Choose ONE option below):")
        print("-" * 80)
        print("👉 OPTION 1: Fully close Chrome and restart it in debugging mode")
        print("   1. Completely close all Google Chrome windows.")
        print("   2. open Task Manager (Ctrl + Shift + Esc) and end ALL 'Google Chrome' tasks.")
        print("   3. Press Win + R, copy & paste the following command, and hit Enter:")
        print('      "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
        print("-" * 80)
        print("👉 OPTION 2: Open a separate debugging instance (Recommended)")
        print("   This lets you keep your regular Chrome window open!")
        print("   1. Create an empty folder at C:\\ChromeDebug (or similar).")
        print("   2. Press Win + R, copy & paste the following command, and hit Enter:")
        print('      "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\\ChromeDebug"')
        print("=" * 80)
        sys.exit(1)

    print("🔌 Connecting to your existing Google Chrome browser...")
    browser = Browser(cdp_url="http://localhost:9222")
    
    try:
        await browser.start()
    except Exception as e:
        print("=" * 80)
        print(f"⚠️  Failed to connect to the Chrome instance: {e}")
        print("Make sure you didn't close Chrome after launching it.")
        print("=" * 80)
        sys.exit(1)
        
    # Force creation of a brand new tab so we don't overwrite your current window/tabs
    print("✨ Creating a brand new tab in your existing Chrome browser...")
    new_target = await browser.cdp_client.send.Target.createTarget(params={'url': 'about:blank'})
    new_target_id = new_target['targetId']
    
    # Wait a split second for the SessionManager to discover the new tab target
    await asyncio.sleep(0.5)
    
    # Switch agent focus specifically to this new tab
    await browser.event_bus.dispatch(SwitchTabEvent(target_id=new_target_id))
    
    # Task: Navigate to Hackernews and find the top story and its points
    task = "Navigate to https://www.richmondphysio.co.uk/ and to the about page, read the content, and summarize it. Then paste the summary into a google spreadsheet. Read the spreadsheet to understand where to paste the summary. Then paste the summary into a google spreadsheet. Read the spreadsheet to understand where to paste the summary. url: https://docs.google.com/spreadsheets/d/14-tvWsttoIFNxcKSWQzQHkOXigVSUNaVByfPmQAMVkU/edit?usp=sharing"
    
    print(f"🚀 Running agent task: '{task}'")
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )
    
    history = await agent.run()
    
    print("\n🎉 Task Completed!")
    print("=" * 40)
    print("Execution History Summary:")
    print("=" * 40)
    final_result = history.final_result()
    if final_result:
        print(f"Result: {final_result}")
    else:
        print("No explicit final result was returned by the agent, but actions completed.")

if __name__ == '__main__':
    asyncio.run(main())
