import cv2


def str_to_array_bits(txt, byte_size=8):
    hexa = txt.encode("utf-8").hex()
    code = []
    for idx in range(0, len(hexa), 2):
        this_hexa = hexa[idx:idx+2]
        byte = bin(int(this_hexa, base=16))[2:]
        byte_padding = max(byte_size - len(byte), 0)
        byte = "0" * byte_padding + byte
        code.append(byte)
    return code


def array_bits_to_str(array_bits):
    return "".join(
        [
            bits_to_bytes(bits).decode("utf-8") for bits in array_bits
        ]
    )


def bits_to_bytes(bits):
    v = int(bits, base=2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])


def opening(img_code):

    morph_size = 5
    morph_elem = cv2.MORPH_ELLIPSE
    element = cv2.getStructuringElement(
        morph_elem, (2*morph_size + 1, 2*morph_size+1), (morph_size, morph_size))
    operation = cv2.MORPH_OPEN
    img_code = cv2.morphologyEx(img_code, operation, element)

    return img_code