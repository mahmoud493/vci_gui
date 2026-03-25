import openai

def chat_with_ai(user_input: str):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un assistant utile et amical."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message["content"]

if __name__ == "__main__":
    while True:
        user_input = input("Vous: ")
        if user_input.lower() in ["quit", "exit"]:
            break
        print("Bot:", chat_with_ai(user_input))
