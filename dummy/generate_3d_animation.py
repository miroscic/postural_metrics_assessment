import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

# Definisci le connessioni tra i keypoint (scheletro)
SKELETON = [
    ("NOS_", "NEC_"),
    ("NEC_", "SPN_"), ("SPN_", "SPC_"),
    ("NEC_", "SHOR"), ("NEC_", "SHOL"),
    ("SHOR", "ELBR"), ("ELBR", "WRIR"),
    ("SHOL", "ELBL"), ("ELBL", "WRIL"),
    ("SPC_", "HIPR"), ("SPC_", "HIPL"),
    ("HIPR", "KNER"), ("KNER", "ANKR"),
    ("HIPL", "KNEL"), ("KNEL", "ANKL"),
    ("NOS_", "EYER"), ("NOS_", "EYEL"),
    ("EYER", "EARR"), ("EYEL", "EARL"),
]

KEYPOINT_COLORS = {
    "NOS_": "red", "NEC_": "orange", "SPN_": "gold", "SPC_": "goldenrod",
    "SHOR": "blue", "SHOL": "blue",
    "ELBR": "green", "ELBL": "green",
    "WRIR": "purple", "WRIL": "purple",
    "HIPR": "brown", "HIPL": "brown",
    "KNER": "gray", "KNEL": "gray",
    "ANKR": "black", "ANKL": "black",
    "EYER": "cyan", "EYEL": "cyan",
    "EARR": "magenta", "EARL": "magenta"
}

with open("simulated_hpe_inputs.json") as f:
    frames = json.load(f)

fig = plt.figure(figsize=(7, 9))
ax = fig.add_subplot(111, projection='3d')

def draw_frame(frame):
    ax.cla()
    message = frame["message"]
    # Disegna le ossa
    for kp1, kp2 in SKELETON:
        if kp1 in message and kp2 in message:
            p1 = np.array(message[kp1]["crd"])
            p2 = np.array(message[kp2]["crd"])
            ax.plot([p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], 'k-', lw=2)
    # Disegna i keypoint
    for label, data in message.items():
        x, y, z = data["crd"]
        color = KEYPOINT_COLORS.get(label, "gray")
        ax.scatter(x, y, z, c=color, s=60)
        ax.text(x, y, z, label, fontsize=7)
    ax.set_xlim(-600, 600)
    ax.set_ylim(0, 2000)
    ax.set_zlim(-600, 600)
    ax.set_box_aspect([1, 3, 1])
    ax.set_title("Scheletro 3D - Animazione interattiva")
    ax.set_axis_off()

plt.ion()
frame_idx = 0
while True:
    draw_frame(frames[frame_idx])
    plt.draw()
    plt.pause(0.08)
    frame_idx = (frame_idx + 1) % len(frames)