import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import math
import time

# Configure ultra-performance system flags
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # Removes default delays built into PyAutoGUI
screen_width, screen_height = pyautogui.size()

# Balanced tracking flags for instant gesture execution
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, 
    min_detection_confidence=0.65,  # Balanced for faster initialization
    min_tracking_confidence=0.80     # Kept high to lock coordinates firmly
)
mp_draw = mp.solutions.drawing_utils

# Video setup
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
frame_w, frame_h = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_w)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_h)

# Positional filtering variables
prev_x, prev_y = 0, 0

# Visual boundary padding map
box_x1, box_y1 = 110, 70
box_x2, box_y2 = frame_w - 110, frame_h - 130

# Non-blocking state management timers
clicked = False
last_click_time = 0
last_zoom_time = 0
click_cooldown = 0.12  # Fast 120ms gesture repeat limit
zoom_cooldown = 0.15   # 150ms incremental zoom tracking steps

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break
        
    frame = cv2.flip(frame, 1)
    current_time = time.time()
    
    # Draw tracking context area box
    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (255, 255, 0), 2)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm_list = []
            for id, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * frame_w), int(lm.y * frame_h)
                lm_list.append((cx, cy))
                
            if len(lm_list) >= 21:
                # FIX: Explicitly index individual coordinates using array positions
                x_idx, y_idx = lm_list[8]    # Index Tip
                x_mid, y_mid = lm_list[12]   # Middle Tip
                x_thumb, y_thumb = lm_list[4] # Thumb Tip
                x_ring, y_ring = lm_list[16]  # Ring Tip
                
                # Normalize distances using index base scale factor
                hand_scale = math.hypot(lm_list[5][0] - lm_list[0][0], lm_list[5][1] - lm_list[0][1])
                hand_scale = max(hand_scale, 1)  
                
                index_up = y_idx < lm_list[6][1]
                middle_up = y_mid < lm_list[10][1]
                ring_up = y_ring < lm_list[14][1]
                
                target_x = np.interp(x_idx, (box_x1, box_x2), (0, screen_width))
                target_y = np.interp(y_idx, (box_y1, box_y2), (0, screen_height))
                
                distance_moved = math.hypot(target_x - prev_x, target_y - prev_y)
                
                # High-speed responsive EMA interpolation
                if distance_moved < 10:
                    ema_alpha = 0.15  # Total steady lock
                elif distance_moved < 40:
                    ema_alpha = 0.35  # Smooth responsive curve
                else:
                    ema_alpha = 0.75  # Ultra-fast snap response to quick motions
                
                dist_im = math.hypot(x_mid - x_idx, y_mid - y_idx) / hand_scale
                
                # 1. Moving & Non-Blocking Clicking Mode
                if index_up and not ring_up:
                    if dist_im < 0.25:  # Click gesture confirmed
                        if not clicked and (current_time - last_click_time > click_cooldown):
                            pyautogui.click(int(prev_x), int(prev_y))
                            clicked = True
                            last_click_time = current_time
                            cv2.circle(frame, (x_idx, y_idx), 15, (0, 0, 255), cv2.FILLED)
                    else:
                        clicked = False
                        
                        # Compute motion calculations safely outside blocking events
                        loc_x = (ema_alpha * target_x) + ((1 - ema_alpha) * prev_x)
                        loc_y = (ema_alpha * target_y) + ((1 - ema_alpha) * prev_y)
                        
                        pyautogui.moveTo(int(loc_x), int(loc_y))
                        prev_x, prev_y = loc_x, loc_y
                        cv2.circle(frame, (x_idx, y_idx), 10, (255, 0, 255), cv2.FILLED)
                
                # 2. Delta Proportional Scrolling Mode 
                elif index_up and middle_up and ring_up:
                    if dist_im < 0.28:
                        y_delta = target_y - prev_y
                        if abs(y_delta) > 4:
                            scroll_speed = int(y_delta / 6)
                            pyautogui.scroll(-scroll_speed)
                            prev_x, prev_y = target_x, target_y  # Synced tracking update
                            cv2.circle(frame, (x_idx, y_idx), 10, (0, 255, 0), cv2.FILLED)
                
                # 3. Non-Blocking Dynamic Zooming Mode
                dist_ti = math.hypot(x_thumb - x_idx, y_thumb - y_idx) / hand_scale
                if current_time - last_zoom_time > zoom_cooldown:
                    if dist_ti < 0.25:
                        pyautogui.keyDown('ctrl')
                        pyautogui.scroll(-2) 
                        pyautogui.keyUp('ctrl')
                        last_zoom_time = current_time
                        cv2.circle(frame, (x_thumb, y_thumb), 10, (0, 0, 255), cv2.FILLED)
                        
                    elif dist_ti > 0.85 and not middle_up:
                        pyautogui.keyDown('ctrl')
                        pyautogui.scroll(2)  
                        pyautogui.keyUp('ctrl')
                        last_zoom_time = current_time
                        cv2.circle(frame, (x_thumb, y_thumb), 10, (0, 255, 255), cv2.FILLED)

    cv2.imshow("High Accuracy AI Virtual Mouse", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
