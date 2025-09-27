import tkinter as tk
from PIL import Image, ImageTk
import cv2
import mediapipe as mp
import imutils
import customtkinter as ctk
import numpy as np

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

# MediaPipe config
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils

# Diccionario con regiones faciales (subset de landmarks)
FACIAL_LANDMARKS = {
    "Ojo Derecho": [33, 133, 159, 145, 153, 154, 155, 246],
    "Ojo Izquierdo": [362, 263, 386, 374, 373, 380, 381, 382],
    "Cejas": [70, 63, 105, 66, 107, 336, 296, 334, 293, 300],
    "Labios": [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308],
    "Nariz": [1, 2, 4, 94, 168, 197, 195, 5, 51, 6],
    "Todo el rostro": list(range(468))  # todos los puntos
}


class FaceMeshApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Face Mesh Viewer')

        self.root.grid_columnconfigure(0, weight=1)   # permite que la columna 0 crezca
        self.root.grid_columnconfigure(1, weight=1)   # permite que la columna 1 crezca

        # Video Frame
        self.video_label = tk.Label(root)
        self.video_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Dropdown para seleccionar parte del rostro
        self.selected_part = ctk.StringVar(value="Todo el rostro")
        self.dropdown = ctk.CTkOptionMenu(root, variable=self.selected_part,
                                          values=list(FACIAL_LANDMARKS.keys()))
        self.dropdown.grid(row=1, column=0, pady=10)

        # Checkbox para activar/desactivar malla
        self.show_mesh = ctk.BooleanVar(value=True)  # activo por defecto
        self.mesh_checkbox = ctk.CTkCheckBox(root, text="Mostrar malla",
                                             variable=self.show_mesh)
        self.mesh_checkbox.grid(row=1, column=1, pady=10)

        # Slider para seleccionar rango de índices (solo cuando es "Todo el rostro")
        self.range_start = ctk.IntVar(value=0)
        self.range_end = ctk.IntVar(value=467)

        self.slider_start = ctk.CTkSlider(root, from_=0, to=467,
                                          variable=self.range_start,
                                          number_of_steps=467,
                                          command=self.update_range_label)

                                          
        self.slider_end = ctk.CTkSlider(root, from_=0, to=467,
                                        variable=self.range_end,
                                        number_of_steps=467,
                                        command=self.update_range_label)

        self.range_label = ctk.CTkLabel(root, text="Rango: 0 - 467")

        # Cámara
        self.cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        # MediaPipe FaceMesh
        self.face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

        # Mostrar sliders si aplica
        self.on_part_change(self.selected_part.get())

        # Loop principal
        self.update_video()
    
    def on_part_change(self, value):
        """Muestra u oculta los sliders dependiendo de la parte seleccionada"""
        if value == "Todo el rostro":
            self.slider_start.grid(row=2, column=0, padx=(200, 0), pady=5, sticky="ew")  # padding a la izquierda
            self.slider_end.grid(row=2, column=1, padx=(0, 200), pady=5, sticky="ew")    # padding a la derecha
            self.range_label.grid(row=3, column=0, columnspan=2, pady=5)
        else:
            self.slider_start.grid_forget()
            self.slider_end.grid_forget()
            self.range_label.grid_forget()

    def update_range_label(self, _=None):
        """Actualiza la etiqueta que muestra el rango"""
        start = self.range_start.get()
        end = self.range_end.get()
        if start > end:  # asegurar consistencia
            start, end = end, start
        self.range_label.configure(text=f"Rango: {start} - {end}")

    def update_video(self):
        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_video)
            return

        frame = imutils.resize(frame, width=1400)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(frame_rgb)

        h, w, _ = frame.shape

        if results.multi_face_landmarks:
            face_landmarks = results.multi_face_landmarks[0]

            # --- Dibujar malla si el checkbox está activo ---
            if self.show_mesh.get():
                # --- Crear overlay vacío ---
                overlay = frame.copy()
                blank = np.zeros_like(frame)

                # Dibujar siempre la malla completa
                mp_drawing.draw_landmarks(
                    overlay, face_landmarks,
                    mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing.DrawingSpec(color=(50, 255, 50), thickness=1, circle_radius=1)
                )

                # --- Mezclar con transparencia ---
                alpha = 0.3  # 0 = transparente, 1 = opaco
                frame = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)

            # Dibujar puntos de la parte seleccionada
            part = self.selected_part.get()
            if part == "Todo el rostro":
                start = min(self.range_start.get(), self.range_end.get())
                end = max(self.range_start.get(), self.range_end.get())
                indices = list(range(start, end + 1))
            else:
                indices = FACIAL_LANDMARKS.get(part, [])

            for idx in indices:
                lx = int(face_landmarks.landmark[idx].x * w)
                ly = int(face_landmarks.landmark[idx].y * h)
                cv2.circle(frame, (lx, ly), 2, (0, 0, 255), -1)
                cv2.putText(frame, str(idx), (lx + 2, ly - 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

        # Mostrar video en tkinter
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
