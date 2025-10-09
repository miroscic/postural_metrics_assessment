import json
import math
import time

def generate_pose(angle_deg):
    # --- Simulazione movimento schiena ---
    # Flessione avanti (x asse): 0° (frame 0) -> 30° (frame finale)
    flex_fwd_deg = -30.0 + (60.0 * angle_deg / 180.0)
    flex_fwd_rad = math.radians(flex_fwd_deg)
    # Rotazione spalle (y asse): -30° (frame 0) -> 30° (frame finale)
    rot_sh_deg = -30 + (60.0 * angle_deg / 180.0)
    rot_sh_rad = math.radians(rot_sh_deg)
    # Bending laterale (z asse): -40° (frame 0) -> 40° (frame finale)
    bend_lat_deg = -40 + (40.0 * angle_deg / 180.0)
    bend_lat_rad = math.radians(bend_lat_deg)

    def rotate_point(p, origin, flex, rot, bend):
        # Applica rotazione: prima bending (z), poi rotazione (y), poi flessione (x)
        x, y, z = [p[i] - origin[i] for i in range(3)]
        # Bending (z, attorno a x)
        yb = y * math.cos(bend) - z * math.sin(bend)
        zb = y * math.sin(bend) + z * math.cos(bend)
        y, z = yb, zb
        # Rotazione (y, attorno a z)
        xb = x * math.cos(rot) - z * math.sin(rot)
        zb = x * math.sin(rot) + z * math.cos(rot)
        x, z = xb, zb
        # Flessione (x, attorno a y)
        xb = x * math.cos(flex) - y * math.sin(flex)
        yb = x * math.sin(flex) + y * math.cos(flex)
        x, y = xb, yb
        return [origin[0] + x, origin[1] + y, origin[2] + z]

    
    # Parametri antropometrici (in mm)
    shoulder_height = 1450
    shoulder_width = 400
    arm_length = 700
    hip_height = 1000
    hip_width = 350
    leg_length = 900
    ankle_height = 100
    head_height = 1700
    head_width = 180
    neck_height = 1550
    body_center_x = 0

    angle_rad = math.radians(angle_deg)

    # Keypoints principali
    keypoints = {
        "NEC_": [body_center_x, neck_height, 0],
        "SPN_": [body_center_x, (neck_height + shoulder_height) / 2, 0],  # spina toracica superiore
        "SPC_": [body_center_x, (shoulder_height + hip_height) / 2, 0],   # spina toracica centrale
        "SHOR": [body_center_x + shoulder_width/2, shoulder_height, 0],
        "SHOL": [body_center_x - shoulder_width/2, shoulder_height, 0],
        "HIPR": [body_center_x + hip_width/2, hip_height, 0],
        "HIPL": [body_center_x - hip_width/2, hip_height, 0],
        "KNER": [body_center_x + hip_width/2, hip_height - leg_length/2, 0],
        "KNEL": [body_center_x - hip_width/2, hip_height - leg_length/2, 0],
        "ANKR": [body_center_x + hip_width/2, ankle_height, 0],
        "ANKL": [body_center_x - hip_width/2, ankle_height, 0],
    }

    # Flessione cervicale: ruota i keypoint della testa da 0 a 30 gradi in avanti rispetto a NEC_
    # L'angolo di flessione cresce linearmente con l'angolo del braccio (0° braccia in basso, 30° braccia sopra la testa)
    flex_angle_deg = 0 + (30.0 * angle_deg / 180.0)
    flex_angle_rad = math.radians(flex_angle_deg)
    neck_to_nose = head_height - neck_height
    dy = neck_to_nose * math.cos(flex_angle_rad)
    dz = neck_to_nose * math.sin(flex_angle_rad)
    keypoints["NOS_"] = [body_center_x, neck_height + dy, dz]
    # Occhi
    eye_offset_x = head_width/4
    eye_offset_y = 30
    eye_offset_z = 40
    keypoints["EYER"] = [body_center_x + eye_offset_x, neck_height + dy + eye_offset_y * math.cos(flex_angle_rad), dz + eye_offset_y * math.sin(flex_angle_rad) + eye_offset_z]
    keypoints["EYEL"] = [body_center_x - eye_offset_x, neck_height + dy + eye_offset_y * math.cos(flex_angle_rad), dz + eye_offset_y * math.sin(flex_angle_rad) + eye_offset_z]
    # Orecchie
    ear_offset_x = head_width/2
    ear_offset_y = 10
    keypoints["EARR"] = [body_center_x + ear_offset_x, neck_height + dy + ear_offset_y * math.cos(flex_angle_rad), dz + ear_offset_y * math.sin(flex_angle_rad)]
    keypoints["EARL"] = [body_center_x - ear_offset_x, neck_height + dy + ear_offset_y * math.cos(flex_angle_rad), dz + ear_offset_y * math.sin(flex_angle_rad)]

    # Braccio destro (omero + avambraccio tesi, ruota solo la spalla nel piano sagittale)
    shor = keypoints["SHOR"]
    # Lunghezza segmenti
    humerus = arm_length * 0.5
    forearm = arm_length * 0.5
    # Direzione (versore)
    dir_y = -math.cos(angle_rad)
    dir_z = math.sin(angle_rad)
    # Gomito destro
    elbr = [
        shor[0],
        shor[1] + humerus * dir_y,
        humerus * dir_z
    ]
    wrir = [
        shor[0],
        shor[1] + (humerus + forearm) * dir_y,
        (humerus + forearm) * dir_z
    ]
        
    shol = keypoints["SHOL"]
    elbl = [
        shol[0],
        shol[1] + humerus * dir_y,
        humerus * dir_z
    ]
    wril = [
        shol[0],
        shol[1] + (humerus + forearm) * dir_y,
        (humerus + forearm) * dir_z
    ]

    keypoints["ELBR"] = elbr
    keypoints["WRIR"] = wrir
    keypoints["ELBL"] = elbl
    keypoints["WRIL"] = wril
    
    # Applica la rotazione a SPC_, SPN_, NEC_, SHOR, SHOL, e ai keypoint della testa
    # Origine rotazione: punto medio tra le anche
    hip_center = [ (keypoints["HIPR"][0] + keypoints["HIPL"][0]) / 2,
                   (keypoints["HIPR"][1] + keypoints["HIPL"][1]) / 2,
                   (keypoints["HIPR"][2] + keypoints["HIPL"][2]) / 2 ]
    for k in ["SPC_", "SPN_", "NEC_", "SHOR", "SHOL", "ELBR", "WRIR", "ELBL", "WRIL", "NOS_", "EYER", "EYEL", "EARR", "EARL"]:
        keypoints[k] = rotate_point(keypoints[k], hip_center, flex_fwd_rad, rot_sh_rad, bend_lat_rad)
        
    # Uncertainty fittizia
    unc = [1,1,1,0,0,0]

    message = {
        "NOS_": {"crd": keypoints["NOS_"], "ncm": 1, "unc": unc},
        "NEC_": {"crd": keypoints["NEC_"], "ncm": 1, "unc": unc},
        "SPN_": {"crd": keypoints["SPN_"], "ncm": 1, "unc": unc},
        "SPC_": {"crd": keypoints["SPC_"], "ncm": 1, "unc": unc},
        "SHOR": {"crd": keypoints["SHOR"], "ncm": 1, "unc": unc},
        "ELBR": {"crd": keypoints["ELBR"], "ncm": 1, "unc": unc},
        "WRIR": {"crd": keypoints["WRIR"], "ncm": 1, "unc": unc},
        "SHOL": {"crd": keypoints["SHOL"], "ncm": 1, "unc": unc},
        "ELBL": {"crd": keypoints["ELBL"], "ncm": 1, "unc": unc},
        "WRIL": {"crd": keypoints["WRIL"], "ncm": 1, "unc": unc},
        "HIPR": {"crd": keypoints["HIPR"], "ncm": 1, "unc": unc},
        "KNER": {"crd": keypoints["KNER"], "ncm": 1, "unc": unc},
        "ANKR": {"crd": keypoints["ANKR"], "ncm": 1, "unc": unc},
        "HIPL": {"crd": keypoints["HIPL"], "ncm": 1, "unc": unc},
        "KNEL": {"crd": keypoints["KNEL"], "ncm": 1, "unc": unc},
        "ANKL": {"crd": keypoints["ANKL"], "ncm": 1, "unc": unc},
        "EYER": {"crd": keypoints["EYER"], "ncm": 1, "unc": unc},
        "EYEL": {"crd": keypoints["EYEL"], "ncm": 1, "unc": unc},
        "EARR": {"crd": keypoints["EARR"], "ncm": 1, "unc": unc},
        "EARL": {"crd": keypoints["EARL"], "ncm": 1, "unc": unc},
    }
    return message

frames = []
ts_base = int(time.time() * 1e9)
for i, angle in enumerate(range(0, 181, 15)):
    frame = {
        "agent_id": "SIMULATED",
        "hostname": "simulator",
        "timecode": i * 0.1,
        "ts": ts_base + i * 1_000_000,
        "typ": "FSD",
        "message": generate_pose(angle)
    }
    frames.append(frame)

with open("simulated_hpe_inputs.json", "w") as f:
    json.dump(frames, f, indent=2)