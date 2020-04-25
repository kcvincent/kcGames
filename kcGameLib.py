from operator import truediv


def d1tod3(d1, b):
    b2 = b**2
    return d1//b2, (d1 % b2) // b, d1 % b


def d3tod1(d1, d2, d3, b):
    b2 = b**2
    return d1*b2 + d2*b + d3


#def floor(n):
#    return int(n - (n % 1))


def toKivyColor(rgb):
    b = tuple(map(truediv, rgb, (255.0, 255.0, 255.0)))
    return b


def isArrow(k):
    return k == 'up' or k == 'down' or k == 'left' or k == 'right'


def getRotations(k):
    if k == 'up':
        return 0
    elif k == 'down':
        return 2
    elif k == 'left':
        return 1
    elif k == 'right':
        return 3
