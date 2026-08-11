import qrcode
def gen_qr(title):
    qr=qrcode.make(f'FREE bonus for {title}')
    qr.save('/tmp/qr.jpg')
    return '/tmp/qr.jpg'
