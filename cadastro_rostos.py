import cv2
import face_recognition
import numpy as np
import os

# Diretório onde os rostos cadastrados serão salvos
faces_dir = 'cadastrados'

# Cria o diretório se não existir
if not os.path.exists(faces_dir):
    os.makedirs(faces_dir)

# Inicializa a webcam
video_capture = cv2.VideoCapture(0)

print("Pressione 'q' para sair ou 'c' para cadastrar uma nova face")

while True:
    ret, frame = video_capture.read()
    rgb_frame = frame[:, :, ::-1]

    # Detecta as faces no quadro
    face_locations = face_recognition.face_locations(rgb_frame)

    for (top, right, bottom, left) in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

    cv2.imshow('Video', frame)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break
    elif key & 0xFF == ord('c'):
        if len(face_locations) == 1:
            face_image = rgb_frame[top:bottom, left:right]
            face_image = cv2.resize(face_image, (150, 150))
            name = input("Digite o nome para cadastrar: ")
            file_path = os.path.join(faces_dir, f"{name}.jpg")
            cv2.imwrite(file_path, face_image)
            print(f"Face de {name} cadastrada com sucesso!")
        else:
            print("Por favor, certifique-se de que há apenas uma face na câmera.")

video_capture.release()
cv2.destroyAllWindows()
