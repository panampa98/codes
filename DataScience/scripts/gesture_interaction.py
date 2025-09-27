import cv2
import mediapipe as mp
import math
import tkinter as tk
from PIL import Image, ImageTk

# Configuración MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)

# Funciones auxiliares
def distance(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1])

def rgb_to_photoimage(frame):
    return ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))

# Tkinter ventana
root = tk.Tk()
root.title("AR File Mover")

canvas_width, canvas_height = 640, 480
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

# Objetos: carpetas y archivos
folders = [
    {"name": "Carpeta A", "x": 50, "y": 50, "w": 120, "h": 80, "color": "blue"},
    {"name": "Carpeta B", "x": 470, "y": 50, "w": 120, "h": 80, "color": "green"}
]

files = [
    {"name": "Archivo 1", "x": 250, "y": 300, "size": 40, "color": "red"},
    {"name": "Archivo 2", "x": 350, "y": 300, "size": 40, "color": "orange"}
]

holding_file = None  # archivo que estamos sujetando

# Loop principal
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7) as hands:

    def loop():
        global holding_file

        ret, frame = cap.read()
        if not ret:
            root.after(10, loop)
            return

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Procesar mano
        results = hands.process(rgb_frame)
        hand_center = None
        grab = False

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]

            # Coordenadas pulgar e índice
            thumb = hand.landmark[4]
            index = hand.landmark[8]
            thumb_pos = (int(thumb.x*w), int(thumb.y*h))
            index_pos = (int(index.x*w), int(index.y*h))

            # Centro de acnlaje
            cx = int((thumb_pos[0] + index_pos[0]) / 2)
            cy = int((thumb_pos[1] + index_pos[1]) / 2)
            hand_center = (cx, cy)

            # Distancia pulgar–índice
            d = distance(thumb_pos, index_pos)
            grab = d < 40  # mano cerrada = agarrando

            # Dibujar landmarks
            for lm in [thumb_pos, index_pos, hand_center]:
                cv2.circle(frame, lm, 5, (255, 255, 0), -1)

        # Limpiar canvas
        canvas.delete("all")

        # Dibujar video de fondo
        img = rgb_to_photoimage(frame)
        canvas.imgtk = img
        canvas.create_image(0, 0, anchor="nw", image=img)

        # Dibujar carpetas
        for f in folders:
            canvas.create_rectangle(f["x"], f["y"], f["x"]+f["w"], f["y"]+f["h"], fill=f["color"])
            canvas.create_text(f["x"]+f["w"]//2, f["y"]+f["h"]//2, text=f["name"], fill="white")

        # Dibujar archivos
        for f in files:
            if holding_file == f and hand_center:
                # Seguir la mano
                f["x"], f["y"] = hand_center
            canvas.create_oval(f["x"]-f["size"], f["y"]-f["size"],
                               f["x"]+f["size"], f["y"]+f["size"],
                               fill=f["color"])
            canvas.create_text(f["x"], f["y"], text=f["name"], fill="white")

        # Agarrar o soltar
        if hand_center:
            if grab and not holding_file:
                # Revisar si la mano está sobre algún archivo
                for f in files:
                    if abs(f["x"] - hand_center[0]) < f["size"] and abs(f["y"] - hand_center[1]) < f["size"]:
                        holding_file = f
                        break
            elif not grab:
                holding_file = None  # soltar archivo

        root.after(10, loop)

    loop()
    root.mainloop()

cap.release()
