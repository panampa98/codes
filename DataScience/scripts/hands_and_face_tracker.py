import tkinter as tk
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import imutils
import customtkinter as ctk
import numpy as np
import math
import time

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

# MediaPipe configs
mp_face_mesh = mp.solutions.face_mesh
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils


class FaceMeshApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Face Mesh + Hands Viewer')

        # Layout con 2 columnas
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # Video
        self.video_label = tk.Label(root)
        self.video_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # ---------- KPI 1: manos en rostro ----------
        self.card1 = ctk.CTkFrame(root, corner_radius=12)
        self.card1.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.hands_value = ctk.CTkLabel(self.card1, text="0", font=("Arial", 36, "bold"))
        self.hands_value.pack(pady=(20, 5))

        self.hands_label = ctk.CTkLabel(self.card1, text="Manos en rostro", font=("Arial", 16))
        self.hands_label.pack(pady=(0, 20))

        # ---------- KPI 2: segundos acumulados ----------
        self.card2 = ctk.CTkFrame(root, corner_radius=12)
        self.card2.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.seconds_value = ctk.CTkLabel(self.card2, text="0.0", font=("Arial", 36, "bold"))
        self.seconds_value.pack(pady=(20, 5))

        self.seconds_label = ctk.CTkLabel(self.card2, text="Segundos totales", font=("Arial", 16))
        self.seconds_label.pack(pady=(0, 20))

        # Cámara
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # FPS
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30
        self.seconds_in_face = 0.0  # acumulador de segundos

        # MediaPipe
        self.face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
        self.hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)

        # Loop principal
        self.update_video()

    def update_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_video)
            return

        frame = imutils.resize(frame, width=960)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar rostro
        face_results = self.face_mesh.process(frame_rgb)
        h, w, _ = frame.shape
        face_box = None

        if face_results.multi_face_landmarks:
            face_landmarks = face_results.multi_face_landmarks[0]

            # Bounding box rostro
            xs = [lm.x * w for lm in face_landmarks.landmark]
            ys = [lm.y * h for lm in face_landmarks.landmark]
            x_min, x_max = int(min(xs)), int(max(xs))
            y_min, y_max = int(min(ys)), int(max(ys))
            face_box = (x_min, y_min, x_max, y_max)

            # Dibujar rostro
            mp_drawing.draw_landmarks(frame, face_landmarks,
                                      mp_face_mesh.FACEMESH_TESSELATION,
                                      landmark_drawing_spec=None,
                                      connection_drawing_spec=mp_drawing.DrawingSpec(color=(50, 255, 50),
                                                                                      thickness=1,
                                                                                      circle_radius=1))
            if face_box:
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

        # Procesar manos
        hand_results = self.hands.process(frame_rgb)
        hands_in_face = 0

        if hand_results.multi_hand_landmarks and face_box:
            for hand_landmarks in hand_results.multi_hand_landmarks:
                # Centro mano
                cx = int(np.mean([lm.x * w for lm in hand_landmarks.landmark]))
                cy = int(np.mean([lm.y * h for lm in hand_landmarks.landmark]))
                cv2.circle(frame, (cx, cy), 10, (255, 0, 0), -1)

                # Dibujar malla mano
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Chequear si centro está dentro de rostro
                x_min, y_min, x_max, y_max = face_box
                if x_min < cx < x_max and y_min < cy < y_max:
                    hands_in_face += 1

        # Acumular segundos si al menos una mano está en rostro
        if hands_in_face > 0:
            self.seconds_in_face += 1 / self.fps

        # Actualizar indicadores
        self.hands_value.configure(text=f"{hands_in_face}")
        self.seconds_value.configure(text=f"{self.seconds_in_face:.1f}")

        # Mostrar video
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        self.video_label.imgtk = img
        self.video_label.configure(image=img)

        self.root.after(10, self.update_video)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()


if __name__ == '__main__':
    root = ctk.CTk()
    app = FaceMeshApp(root)
    root.mainloop()
