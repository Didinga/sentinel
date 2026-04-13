import cv2
import time
from enum import Enum
import os
from datetime import datetime
from telegram import Bot
from dotenv import load_dotenv

# =========================
# TELEGRAM SETTINGS
# =========================
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = int(os.getenv("TELEGRAM_CHAT_ID"))
bot = Bot(token=TELEGRAM_TOKEN)

# =========================
# STATE MACHINE
# =========================
class State(Enum):
    IDLE = 1
    INVESTIGATE = 2
    ALERT = 3

class Brain:
    def __init__(self):
        self.state = State.IDLE
        self.last_motion_time = 0
        self.last_face_time = 0
        self.alert_sent = False

    def update(self, motion_detected, face_detected):
        now = time.time()
        if motion_detected:
            self.last_motion_time = now
        if face_detected:
            self.last_face_time = now

        if self.state == State.IDLE:
            if motion_detected:
                self.state = State.INVESTIGATE
        elif self.state == State.INVESTIGATE:
            if face_detected:
                self.state = State.ALERT
            elif now - self.last_motion_time > 3:
                self.state = State.IDLE
        elif self.state == State.ALERT:
            if now - self.last_face_time > 5:
                self.state = State.IDLE
        return self.state

# =========================
# VISION SYSTEM
# =========================
class Vision:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.fgbg = cv2.createBackgroundSubtractorMOG2()
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def process(self):
        ret, frame = self.cap.read()
        if not ret:
            return None, False, False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Motion detection
        fgmask = self.fgbg.apply(frame)
        _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        motion_detected = any(cv2.contourArea(cnt) > 1000 for cnt in contours)
        for cnt in contours:
            if cv2.contourArea(cnt) > 1000:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Face detection
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
        )
        face_detected = len(faces) > 0
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        return frame, motion_detected, face_detected

# =========================
# MAIN LOOP
# =========================
def main():
    vision = Vision()
    brain = Brain()

    if not os.path.exists("snapshots"):
        os.makedirs("snapshots")

    ALERT_COOLDOWN = 5
    last_alert_time = 0

    while True:
        frame, motion, face = vision.process()
        if frame is None:
            break

        state = brain.update(motion, face)

        now = time.time()
        if state == State.ALERT and (now - last_alert_time > ALERT_COOLDOWN):
            last_alert_time = now

            # Save snapshot
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            snapshot_file = f"snapshots/alert_{timestamp}.jpg"
            cv2.imwrite(snapshot_file, frame)
            print(f"[ALERT] Snapshot saved: {snapshot_file}")

            # Audio alarm
            os.system('aplay /usr/share/sounds/alsa/Front_Center.wav &')

            # Telegram notification
            try:
                bot.send_message(TELEGRAM_CHAT_ID, f"[ALERT] Face and motion detected!\n{snapshot_file}")
                bot.send_photo(TELEGRAM_CHAT_ID, photo=open(snapshot_file, "rb"))
            except Exception as e:
                print(f"Telegram error: {e}")

        cv2.putText(frame, f"STATE: {state.name}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Sentinel Robot", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    vision.cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
