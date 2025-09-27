import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import math
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import imutils

import customtkinter as ctk

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

import matplotlib.pyplot as plt
plt.style.use('dark_background')

# MediaPipe config
mp_face_mesh = mp.solutions.face_mesh

# índices de landmarks (ojos)
RIGHT_EYE_TOP = 159
RIGHT_EYE_BOTTOM = 145
LEFT_EYE_TOP = 386
LEFT_EYE_BOTTOM = 374


class EyeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Eye Opening Tracker')

        # Video Frame
        self.video_label = tk.Label(root)
        self.video_label.grid(row=0, column=0)

        # Matplotlib Figure
        self.fig = Figure(figsize=(8, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title('Apertura de ojos')
        self.ax.set_xlabel('Frames')
        self.ax.set_ylabel('Distancia (px)')
        self.ax.set_ylim(0, 50)
        self.line_left, = self.ax.plot([], [], label='Ojo Izquierdo', color='green')
        self.line_right, = self.ax.plot([], [], label='Ojo Derecho', color='blue')
        self.ax.legend()

        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)

        # Variables
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.left_data = []
        self.right_data = []
        self.max_points = 200  # número máximo de puntos en el gráfico

        # MediaPipe FaceMesh
        self.face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

        # Loop principal
        self.update_video()

    def get_eye_distance(self, landmarks, idx1, idx2, w, h):
        x1, y1 = int(landmarks[idx1].x * w), int(landmarks[idx1].y * h)
        x2, y2 = int(landmarks[idx2].x * w), int(landmarks[idx2].y * h)
        return math.hypot(x2 - x1, y2 - y1), (x1, y1), (x2, y2)

    def update_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_video)
            return
        
        frame = imutils.resize(frame, width=960)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        h, w, _ = frame.shape
        left_len, right_len = None, None

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0].landmark

            # Ojo derecho
            right_len, p1, p2 = self.get_eye_distance(face_landmarks,
                                                      RIGHT_EYE_TOP,
                                                      RIGHT_EYE_BOTTOM,
                                                      w, h)
            cv2.circle(frame, p1, 2, (255, 0, 0), -1)
            cv2.circle(frame, p2, 2, (255, 0, 0), -1)

            # Ojo izquierdo
            left_len, p3, p4 = self.get_eye_distance(face_landmarks,
                                                     LEFT_EYE_TOP,
                                                     LEFT_EYE_BOTTOM,
                                                     w, h)
            cv2.circle(frame, p3, 2, (0, 255, 0), -1)
            cv2.circle(frame, p4, 2, (0, 255, 0), -1)

            # Guardar datos
            if left_len and right_len:
                self.left_data.append(left_len)
                self.right_data.append(right_len)
                if len(self.left_data) > self.max_points:
                    self.left_data.pop(0)
                    self.right_data.pop(0)

                # Actualizar gráfico
                self.line_left.set_data(range(len(self.left_data)), self.left_data)
                self.line_right.set_data(range(len(self.right_data)), self.right_data)

                
                self.ax.set_xlim(0, self.max_points)    # Eje X dinámico
                self.ax.set_ylim(0, 50)                 # Eje Y fijo

                self.fig.tight_layout()
                self.canvas.draw()

        # Mostrar video en tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        self.video_label.imgtk = img
        self.video_label.configure(image=img)

        # Loop
        self.root.after(10, self.update_video)

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()


if __name__ == '__main__':
    root = ctk.CTk()
    app = EyeTrackerApp(root)
    root.mainloop()
