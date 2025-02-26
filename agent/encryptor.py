import base64

def xor_encrypt(data, key="secret"):
    """ פונקציה להצפנת נתונים בשיטת XOR עם קידוד Base64 """
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data))
    return base64.b64encode(encrypted.encode()).decode()  # מקודד ל-Base64

def xor_decrypt(encrypted_data, key="secret"):
    """ פונקציה לפענוח נתונים שהוצפנו ב-XOR (מפענח קודם את Base64) """
    decoded_data = base64.b64decode(encrypted_data).decode()  # מפענח את Base64
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded_data))  # מפענח XOR

# בדיקה
if __name__ == "__main__":
    text = "מה נשמע"  # טקסט בעברית לבדיקה
    encrypted = xor_encrypt(text)
    print("Encrypted:", encrypted)
    
    decrypted = xor_decrypt(encrypted)
    print("Decrypted:", decrypted)  # אמור להחזיר "מה נשמע"
