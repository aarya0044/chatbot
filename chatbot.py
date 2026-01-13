import os
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Load environment variables
load_dotenv()

# Initialize Groq LLM (FREE cloud model)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.3,
    api_key=os.getenv("GROQ_API_KEY")
)

# Memory to store conversation
memory = ConversationBufferMemory()

# Create conversation chain
chatbot = ConversationChain(
    llm=llm,
    memory=memory
)

print("🤖 AI Chatbot started! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        print("👋 Goodbye!")
        break

    response = chatbot.predict(input=user_input)
    print("Bot:", response)
