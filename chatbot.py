import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Carregar o modelo treinado e o tokenizador
model = GPT2LMHeadModel.from_pretrained("../chatbot_model")
tokenizer = GPT2Tokenizer.from_pretrained("../chatbot_model")

# Função para gerar uma resposta
def generate_response(prompt):
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    outputs = model.generate(inputs, max_length=200, num_return_sequences=1, no_repeat_ngram_size=2)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Loop de interação do chatbot
print("Chatbot:How can i help you today?")
while True:
    user_input = input("Você: ")
    if user_input.lower() in ["sair", "exit", "quit"]:
        break
    response = generate_response(user_input)
    print(f"Chatbot: {response}")
