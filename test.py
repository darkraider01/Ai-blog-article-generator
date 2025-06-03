import openai

openai.api_key = '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'

response = openai.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say hello"}],
    max_tokens=5
)

print(response.choices[0].message.content)
