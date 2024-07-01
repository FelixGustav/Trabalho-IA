import cv2
import os

def capturar_imagem(nome, pasta='../imagens/'):
    # Tente abrir a câmera padrão (0)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erro: Não foi possível acessar a câmera")
        return
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print('Erro: Não foi possível capturar a imagem')
            break
            
        cv2.imshow('Pressione Q para capturar', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            nome_arquivo_jpeg = os.path.join(pasta, f'{nome}.jpeg')
            
            # Salva a imagem JPEG
            cv2.imwrite(nome_arquivo_jpeg, frame)
            
            print(f'Imagem de {nome} capturada e salva em {nome_arquivo_jpeg}')
            break
    
    cap.release()
    cv2.destroyAllWindows()
