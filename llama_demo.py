import asyncio
from browser_use import Agent
from langchain_ollama import ChatOllama
from examples.models.langchain.chat import ChatLangchain


async def main():
    # 1. Initialize your local Llama 3 model
    # Note: browser-use tasks take up significant context, 
    # so we explicitly expand num_ctx to 32k.
    langchain_model = ChatOllama(
        model="qwen2.5vl:3b",
        base_url="http://192.168.1.5:11434",
        num_ctx=32000,        # Leave this high so the page DOM data fits comfortably
        temperature=0.0
    )

    # Wrap it to make it compatible with browser-use's BaseChatModel protocol
    llm = ChatLangchain(chat=langchain_model)

    # 2. Define the agent and assign the task
    agent = Agent(
        task="Go to google.com, find the top post, and tell me its title.",
        llm=llm,
        max_actions_per_step=1,
        # tool_call_in_content=False,
        # llm_timeout=300
    )

    # 3. Execute the automation loop
    result = await agent.run(max_steps=20)
    print("\n[Agent Execution Result]:\n", result)

if __name__ == "__main__":
    asyncio.run(main())