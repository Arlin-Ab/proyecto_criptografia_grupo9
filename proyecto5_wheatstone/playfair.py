from pycipher import Playfair

cipher_text = Playfair('PLAYFIREXMBCDGHKNOQSTUVWZ').encipher('Hide the gold')
print('Texto Cifrado =' + cipher_text)

plain_text = Playfair('PLAYFIREXMBCDGHKNOQSTUVWZ').decipher(cipher_text)

print('Texto Plano = ' + plain_text)