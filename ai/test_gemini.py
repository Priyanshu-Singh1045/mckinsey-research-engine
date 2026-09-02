from ai.llm.gemini import GeminiLLM


llm = GeminiLLM()

response = llm.generate(
    "Explain market research in 3 simple sentences."
)

print(response)