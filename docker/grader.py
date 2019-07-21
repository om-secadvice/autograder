from Crypto.Random import get_random_bytes
from io import BytesIO
def test_aes_encryption():
    key=get_random_bytes(16)
    msg=get_random_bytes(100)
    ciphertext=Userlib().encrypt(key,msg)
    
    retrieved_msg=Userlib().decrypt(key,ciphertext)
    
    if msg == retrieved_msg.getbuffer():
        return "Test Success:AES Encryption-Decryption"
    else:
        return "Test Failure:AES Encryption-Decryption"
    
print(test_aes_encryption())

