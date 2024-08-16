# menuGemini.py

import os

def executarGeminiBasico():
    os.system('python geminiBasico.py')

def executarGeminiBasicoChat():
    os.system('python geminiBasicoChat.py')

def executarGeminiBasicoChatVoz():
    os.system('python geminiBasicoChatVoz.py')

def executarGeminiBasicoImagem():
    os.system('python geminiBasicoImagem.py')

def executarGeminiBasicoStream():
    os.system('python geminiBasicoStream.py')

def mostrarMenu():
    while True:
        print("\n### Menu do Baymax! ###")
        print("1. Executar Baymax Básico")
        print("2. Executar Baymax Básico Chat")
        print("3. Executar Baymax Básico Chat Voz")
        print("4. Executar Baymax Básico Imagem")
        print("5. Executar Baymax Básico Stream")
        print("6. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            executarGeminiBasico()
        elif escolha == '2':
            executarGeminiBasicoChat()
        elif escolha == '3':
            executarGeminiBasicoChatVoz()
        elif escolha == '4':
            executarGeminiBasicoImagem()
        elif escolha == '5':
            executarGeminiBasicoStream()
        elif escolha == '6':
            print("Saindo do menu...")
            break
        else:
            print("Opção inválida, tente novamente.")

if __name__ == '__main__':
    mostrarMenu()
