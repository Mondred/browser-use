import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure the local browser-use package is picked up
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environmental variables from .env file
load_dotenv()

from langchain_ollama import ChatOllama
from browser_use import Agent
from examples.models.langchain.chat import ChatLangchain

# Check for Ollama configuration, defaulting to user's exact address and model
ollama_host = os.environ.get("OLLAMA_HOST", "http://192.168.1.5:11434")
ollama_model = os.environ.get("OLLAMA_MODEL", "llama3:latest")

async def main():
	print(f"🤖 Initializing langchain-ollama ChatOllama model...")
	print(f"🔗 Ollama Host: {ollama_host}")
	print(f"📦 Ollama Model: {ollama_model}")

	# 1. Initialize your local Llama 3 model via langchain_ollama
	# Note: browser-use tasks take up significant context, 
	# so we explicitly expand num_ctx to 32k.
	langchain_model = ChatOllama(
		model=ollama_model,
		base_url=ollama_host,
		num_ctx=32000,
		temperature=0.0  # Keep temperature low so actions are precise
	)

	# 2. Wrap the LangChain model with ChatLangchain to make it compatible with browser-use BaseChatModel
	llm = ChatLangchain(chat=langchain_model)

	# 3. Define the agent and assign the task
	print("🚀 Defining the agent and starting the automation loop...")
	agent = Agent(
		task="Go to hackernews, find the top post, and tell me its title.",
		llm=llm,
		max_actions_per_step=1,
		tool_call_in_content=False,
		llm_timeout=300  # Give Ollama ample time to form responses
	)

	# 4. Execute the automation loop
	result = await agent.run(max_steps=20)
	print("\n[Agent Execution Result]:\n", result)

if __name__ == "__main__":
	asyncio.run(main())
