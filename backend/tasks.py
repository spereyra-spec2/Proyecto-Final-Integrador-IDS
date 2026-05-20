import os
import qrcode

def hacer_y_guardar_qr(url):
    img = qrcode.make(url)

    os.makedirs("static", exist_ok=True)
    filepath = os.path.join("static", "qr_asistencia.png")
    img.save(filepath)

    print(f"QR generado y guardado en {filepath}")
