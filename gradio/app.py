from llm.agent import MCPChat
import gradio as gr

agent = ConversationalMCPAgent('http://localhost:8000')

await agent.setup_tools()

try:
    llm = create_groq_llm()
    print("✅ Groq LLM initialized successfully")
except ValueError as e:
    print(f"❌ Error initializing Groq LLM: {e}")
    print("Get your free API key at: https://console.groq.com/")
    return

agent.create_agent(llm)

def mcp_chat(message, history):
    if not message:
        return
    
    if message.lower() == '/clear':
        agent.clear_conversation()
        return 'Conversation cleared'
    elif message.lower() == '/history':
        history = agent.get_conversation_history()
        output = ''
        for message in history:
            output += '👤' if message['role'] == 'user' else '🤖'
            output += f"{role_emoji}: {message['role'].title()}: {message['content'][:100]}"
            output += '\n'
        return output
    elif message.lower() == '/save':
        parts = message.split(' ', 1)
        filename = parts[1] if len(parts) > 1 else 'conversation.json'
        agent.save_conversation(filename)
        return 'Chat history saved succesfully'

    result = await agent.chat(message)
    return '🤖' + result['response']

if __name__ == '__main__':
    gr.ChatInterface(
        fn = mcp_chat,
        type = 'message'
    ).launch()