from cadastro import capturar_imagem
import subprocess
import os   
import time
import platform

def limpar_tela():
    system = platform.system().upper()
    if system == 'WINDOWS':
        os.system('cls')
    else:
        os.system('clear')

def chamar_outro_script():
    try:
        # Executa o script Python
        subprocess.run(['python', 'presenca_refactored_v2_no_conversion.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o script: {e}")

#Loop para cadastrar rostos ou marcar presença
while True:
    print("Escolha uma opção:")
    print("1. Cadastrar rosto")
    print("2. Marcar presença")
    print("3. Sair")

    escolha = input("Digite o número da sua escolha: ")

    if escolha == '1':
        nome = input("Digite o nome da pessoa: ")
        capturar_imagem(nome)
    elif escolha == '2':
        chamar_outro_script()
    elif escolha == '3' or escolha.lower() == 'sair' or escolha.lower() == 'exit' or escolha.lower() == 'quit':
        print("Saindo...")
        time.sleep(1)
        limpar_tela()
        break
    else:
        print("Opção inválida. Tente novamente.")