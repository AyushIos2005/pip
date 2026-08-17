import qrcode as q 
from PIL import Image

qr=q.QRCode(version=1,
            error_correction=q.constants.ERROR_CORRECT_H,
            box_size=10,
            border=5,
            
            )
qr.add_data("https://youtu.be/H47f-qyc3wg?si=z7WgAzpXm30qaadS")
qr.make(fit=True)
img = qr.make_image(fill_color="red",back_color="blue")
img.save("youtubr.png")
