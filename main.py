import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from socket import gaierror
from PIL import Image
from threading import Thread
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()


def send_image(data):
    msg_root = MIMEMultipart("related")
    msg_root['To'] = 'radwan.chaieb@gmail.com'
    msg_root['Subject'] = 'test'
    msg_root['From'] = os.getenv("MAIL")
    msg_alt = MIMEMultipart("Alternative")
    msg_root.attach(msg_alt)
    msg_text = MIMEText('detected ')
    msg_alt.attach(msg_text)
    msg_image = MIMEImage(data)
    msg_image.add_header("Content-ID", "<image1>")
    msg_root.attach(msg_image)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as gmail:
            gmail.starttls()
            gmail.login(os.getenv("MAIL"), os.getenv("PASS"))
            gmail.sendmail(os.getenv("MAIL"), ['radwan.chaieb@gmail.com'], msg_root.as_string())
    except gaierror:
        print('bad settings')
    except smtplib.SMTPServerDisconnected:
        print('connection faild')
    except smtplib.SMTPException as e:
        print('error : '+str(e))


async def async_range(start, stop):
    for i in range(start, stop):
        yield i
        await asyncio.sleep(0)


async def connect():
    async for i in async_range(2, 255):
        host_ = f"192.168.1.{i}"
        try:
            _reader, writer = await asyncio.wait_for(asyncio.open_connection(host_, 6677), timeout=0.5)
            writer.close()
            await writer.wait_closed()
            return host_
        except asyncio.exceptions.TimeoutError:
            print(f"[-] {host_} failed")
            continue
        except OSError:
            print("network error")
            break
    return None


async def get_camera_ip():
    a = await connect()
    return a
host = asyncio.run(get_camera_ip())

if host is None:
    print("[-] error there is no camera")
    exit(0)
else:
    print(f"[+] camera ip {host}")

sended = False
cap = cv2.VideoCapture(f"http://{host}:6677/videofeed?username=&password=")
# sended = False
# cap = cv2.VideoCapture(f"http://192.168.1.100:6677/videofeed?username=&password=")

faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

while cap.isOpened():
    ret, img = cap.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=2)
    if type(faces) != tuple:
        x, y, w, h = faces[0]
        Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).save("data.jpeg")
        if not sended:
            thread = Thread(target=send_image, args=(open("data.jpeg", "rb").read(),))
            thread.start()
        sended = True
        # cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
    else:
        sended = False
    # cv2.imshow("win", img)
    key = cv2.waitKey(1)
    # closed = cv2.getWindowProperty("win", cv2.WND_PROP_VISIBLE) == 0
    if key == 27 or key == 113:  #or closed:
        cv2.destroyAllWindows()
        break
