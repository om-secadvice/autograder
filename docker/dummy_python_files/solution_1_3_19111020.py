from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from io import BytesIO
class Userlib:

	def encrypt(self,key,msg):
		aes_obj = AES.new(key, AES.MODE_EAX)
		cipher, tag = aes_obj.encrypt_and_digest(msg)
		ciphertext=BytesIO()
		ciphertext.write(aes_obj.nonce)
		ciphertext.write(tag)
		ciphertext.write(cipher)
		ciphertext.seek(0)
		
		return ciphertext
		
	def decrypt(self,key,ciphertext):
		
		nonce, tag, cipher = [ ciphertext.read(x) for x in (16,16, -1) ]
		
		aes_obj = AES.new(key, AES.MODE_EAX, nonce)
		msgbuff = aes_obj.decrypt_and_verify(cipher, tag)
		retrieved_msg=BytesIO(msgbuff)
		retrieved_msg.seek(0)
		return retrieved_msg
