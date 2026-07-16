from app.llm.groq_client import GroqClient

llm = GroqClient()

print(
    llm.generate(
        "Say Hello."
    )
)