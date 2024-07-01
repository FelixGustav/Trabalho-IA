import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

# Função para carregar imagens e seus nomes
def load_images_from_folder(folder):
    images = []
    classNames = []
    print(f"Verificando a pasta: {folder}")
    if not os.path.exists(folder):
        print(f"Error: Pasta {folder} não encontrada.")
        return images, classNames
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        print(f"Verificando arquivo: {file_path}")
        if os.path.isfile(file_path):
            img = cv2.imread(file_path)
            if img is not None:
                print(f"Loading image: {filename}")
                # Convertendo para 8-bit RGB se necessário
                if img.dtype != np.uint8:
                    img = cv2.convertScaleAbs(img)
                if len(img.shape) == 2:  # Imagem em escala de cinza
                    img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
                elif img.shape[2] == 4:  # Imagem com canal alfa (RGBA)
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                elif img.shape[2] == 3:  # Imagem BGR (formato padrão do OpenCV)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                print(f"Tipo de imagem: {img.dtype}, Forma da imagem: {img.shape}")
                images.append(img)
                classNames.append(os.path.splitext(filename)[0])
            else:
                print(f"Failed to load image: {filename}")
        else:
            print(f"{file_path} não é um arquivo.")
    return images, classNames

# Função para codificar as imagens
def find_encodings(images):
    encode_list = []
    for img in images:
        try:
            encode = face_recognition.face_encodings(img)
            if len(encode) > 0:
                encode_list.append(encode[0])
                print("Encoding successful")
            else:
                print(f"Warning: No face found in image.")
        except Exception as e:
            print(f"Error processing image: {e}")
            continue
    return encode_list

# Função para marcar a presença
def mark_attendance(name):
    try:
        now = datetime.now()
        dt_string = now.strftime('%Y-%m-%d %H:%M:%S')
        updated_lines = []
        name_found = False

        # Verifica se o arquivo de presença já existe
        if os.path.isfile('attendance.csv'):
            with open('attendance.csv', 'r') as fr:
                lines = fr.readlines()
                for line in lines:
                    parts = line.strip().split(',')
                    if parts[0] == name:
                        name_found = True
                        # Encontrou o nome, verifica e atualiza o horário de saída se já houver entrada registrada
                        if len(parts) >= 2:  # Verifica se há pelo menos uma entrada registrada
                            parts[2] = dt_string  # Atualiza o horário de saída para o atual
                            updated_lines.append(','.join(parts) + '\n')
                            print(f"Saída atualizada para {name}")
                        else:
                            updated_lines.append(line)
                    else:
                        updated_lines.append(line)

        # Se o nome não foi encontrado no arquivo, adiciona uma nova entrada
        if not name_found:
            updated_lines.append(f'{name},{dt_string},\n')
            print(f"Entrada marcada para {name}")

        # Escreve as linhas atualizadas de volta no arquivo
        with open('attendance.csv', 'w') as fw:
            fw.writelines(updated_lines)

    except Exception as e:
        print(f"Erro marcando a presença: {e}")

# Caminho da pasta das imagens
folder_path = '../imagens/'  # Substitua pelo caminho correto
images, classNames = load_images_from_folder(folder_path)
print(f"Loaded {len(images)} images")
known_face_encodings = find_encodings(images)
print(f"Encoded {len(known_face_encodings)} faces")

# Verificar se a lista de codificações está vazia
if len(known_face_encodings) == 0:
    print("Erro: Nenhuma codificação de rosto encontrada. Por favor, verifique as imagens na pasta.")
    exit()

# Inicializando a webcam
cap = cv2.VideoCapture(0)

tolerance = 0.6  # Ajuste este valor conforme necessário, tolerância ajustável para correspondência facial

while True:
    success, img = cap.read()
    if not success:
        print("Falha ao capturar a imagem da webcam.")
        break

    if img is not None:
        # Redimensiona a imagem para melhorar o desempenho do reconhecimento facial
        img_small = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        print(f"Tipo de imagem capturada: {img.dtype}, Forma da imagem capturada: {img.shape}")
        print(f"Tipo de imagem redimensionada: {img_small.dtype}, Forma da imagem redimensionada: {img_small.shape}")

        try:
            # Localizações e encodings dos rostos no frame atual da webcam
            faces_cur_frame = face_recognition.face_locations(img_small)
            encodes_cur_frame = face_recognition.face_encodings(img_small, faces_cur_frame)
            print(f"Detectou {len(faces_cur_frame)} rostos no quadro")
        except Exception as e:
            print(f"Erro Processando a imagem da webcam: {e}")
            continue

        for encode_face, face_loc in zip(encodes_cur_frame, faces_cur_frame):
            matches = face_recognition.compare_faces(known_face_encodings, encode_face, tolerance)
            face_distances = face_recognition.face_distance(known_face_encodings, encode_face)
            
            if face_distances.size > 0:
                match_index = np.argmin(face_distances)
                if matches[match_index]:
                    name = classNames[match_index].upper()
                    print(f"Combinação encontrada: {name}")
                    y1, x2, y2, x1 = face_loc
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    mark_attendance(name)
                else:
                    print("Nenhuma combinação encontrada")
            else:
                print("Nenhuma distâncias encontradas")

        cv2.imshow('Registro de frequencia, Pressione "Q" para sair', img)
    else:
        print("A imagem capturada não está no formato esperado.")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
