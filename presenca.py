import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# Função para carregar imagens e seus nomes
def load_images_from_folder(folder):
    images = []
    classNames = []
    for filename in os.listdir(folder):
        img = cv2.imread(os.path.join(folder, filename))
        if img is not None:
            # Verificar se a imagem está em 8 bits e converter para RGB se necessário
            if len(img.shape) == 2:  # Imagem em escala de cinza
                img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            elif img.shape[2] == 4:  # Imagem com canal alfa (RGBA)
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            elif img.shape[2] == 3:  # Imagem BGR (formato padrão do OpenCV)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
            classNames.append(os.path.splitext(filename)[0])
    return images, classNames

# Função para codificar as imagens
def find_encodings(images):
    encode_list = []
    for img in images:
        try:
            if img.dtype != np.uint8:
                raise ValueError("Image is not 8-bit")
            encode = face_recognition.face_encodings(img)[0]
            encode_list.append(encode)
        except IndexError:
            print(f"Warning: No face found in image.")
            continue
        except Exception as e:
            print(f"Error processing image: {e}")
            continue
    return encode_list

# Função para marcar a presença
def mark_attendance(name):
    with open('attendance.csv', 'r+') as f:
        my_data_list = f.readlines()
        name_list = []
        for line in my_data_list:
            entry = line.split(',')
            name_list.append(entry[0])
        if name not in name_list:
            now = datetime.now()
            dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
            f.writelines(f'\n{name},{dt_string}')

# Caminho da pasta das imagens
folder_path = '../imagens/'  # Substitua pelo caminho correto
images, classNames = load_images_from_folder(folder_path)
known_face_encodings = find_encodings(images)

# Inicializando a webcam
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image from webcam.")
        break

    # Verificar e converter a imagem para RGB se necessário
    if img is not None:
        print(f"Captured image shape: {img.shape}, dtype: {img.dtype}")
        if img.shape[-1] == 3 and img.dtype == np.uint8:
            img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            img_small = cv2.cvtColor(img_small, cv2.COLOR_BGR2RGB)

            try:
                # Conversão explícita para garantir o formato correto
                img_small = img_small.astype(np.uint8)
                faces_cur_frame = face_recognition.face_locations(img_small)
                encodes_cur_frame = face_recognition.face_encodings(img_small, faces_cur_frame)
            except Exception as e:
                print(f"Error processing webcam image: {e}")
                continue

            for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
                matches = face_recognition.compare_faces(known_face_encodings, encode_face)
                face_distances = face_recognition.face_distance(known_face_encodings, encode_face)
                match_index = np.argmin(face_distances)

                if matches[match_index]:
                    name = classNames[match_index].upper()
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    mark_attendance(name)

            cv2.imshow('Webcam', img)
        else:
            print("Captured image is not in the expected format.")
    else:
        print("Captured image is None.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
