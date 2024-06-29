import cv2
import face_recognition
import numpy as np
import os
from datetime import datetime

# Diretório onde os rostos cadastrados estão salvos
faces_dir = 'cadastrados'

# Carrega os rostos cadastrados
known_face_encodings = []
known_face_names = []

for file_name in os.listdir(faces_dir):
    if file_name.endswith(".jpg"):
        image = face_recognition.load_image_file(os.path.join(faces_dir, file_name))
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        known_face_names.append(os.path.splitext(file_name)[0])

# Inicializa a webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    rgb_frame = frame[:, :, ::-1]

    # Detecta as faces no quadro
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Desconhecido"

        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]
        
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 0, 255), 1)

        if name != "Desconhecido":
            with open('frequencia.csv', 'a') as f:
                now = datetime.now()
                f.write(f"{name},{now}\n")
                print(f"Registro de frequência para {name} às {now}")

    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
