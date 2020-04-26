# -*- coding: utf-8 -*-
from operator import truediv
import qrcode
from io import BytesIO
from PIL import Image

def d1tod3(d1, b):
    b2 = b**2
    return d1//b2, (d1 % b2) // b, d1 % b


def d3tod1(d1, d2, d3, b):
    b2 = b**2
    return d1*b2 + d2*b + d3


def toKivyColor(rgb):
    b = tuple(map(truediv, rgb, (255.0, 255.0, 255.0)))
    return b


def genQrCodePilImage(msg, stream_format = "png",fill_color = "black",back_color="white"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(msg)
    qr.make(fit=True)
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    return img


def genQrCodeImgFile(msg, filename, stream_format = "png",fill_color = "black",back_color="white"):
    img = genQrCodePilImage(msg, stream_format ,fill_color ,back_color)
    img.save(filename)


def genQrCodeBytesIOwithSize(msg, stream_format="png", fill_color="black", back_color="white"):
    """
    使用方法
     w, h, rawimg = genQrCodeBytesIOwithSize(msg)
     img = kivy.core.image(BytesIO(rawimg.read()), ext="png", filename="image.png")
     img = CoreImage(BytesIO(rawimg.read()), ext="png", filename="image.png")
    :param msg:
    :param stream_format:
    :param fill_color:
    :param back_color:
    :return:
        int, int, BytesIO
    """
    img = genQrCodePilImage(msg, stream_format, fill_color, back_color)
    data = BytesIO()
    img.save(data, format=stream_format)
    data.seek(0)
    w, h = img.size
    return w, h, data


def genQrCodeBytesIO(msg, stream_format="png", fill_color="black", back_color="white"):
    """
    使用方法
     rawimg = genQrCodeBytesIOwithSize(msg)
     img = kivy.core.image(BytesIO(rawimg.read()), ext="png", filename="image.png")
     img = CoreImage(BytesIO(rawimg.read()), ext="png", filename="image.png")
    :param msg:
    :param stream_format:
    :param fill_color:
    :param back_color:
    :return:
        type = BytesIO
    """
    img = genQrCodePilImage(msg, stream_format, fill_color, back_color)
    data = BytesIO()
    img.save(data, format=stream_format)
    data.seek(0)
    return data
