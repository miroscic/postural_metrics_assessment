import json

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import imageio
import numpy as np

import matplotlib
matplotlib.use('Agg')

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
    "NOS_": "red", "NEC_": "orange",
    "SPN_": "gold", "SPC_": "goldenrod",
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

images = []
for frame in frames:
    message = frame["message"]
    fig = plt.figure(figsize=(6, 8))
    ax = fig.add_subplot(111, projection='3d')
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
    ax.view_init(elev=-90, azim=90, roll=0)
    ax.set_axis_off()
    plt.tight_layout()
    fig.canvas.draw()
    width, height = fig.canvas.get_width_height()
    image = np.frombuffer(fig.canvas.buffer_rgba(), dtype='uint8').reshape(height, width, 4)[..., :3]
    images.append(image)
    plt.close(fig)

# Salva la gif
imageio.mimsave("skeleton_animation.gif", images, duration=0.15)
print("GIF salvata come skeleton_animation.gif")