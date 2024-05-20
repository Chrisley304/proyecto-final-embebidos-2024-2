import face_recognition
import os

def recognize_face_from_photos(base_photo_path:str, unknown_photo_path:str):
	"""
		Función que devuelve si las fotos compartidas contienen a la misma persona.

		Params:
			base_photo_path: path hacia la foto que contiene la cara a reconocer.
			unknown_photo_path: path hacia la foto a reconocer.
	"""

	if os.path.isfile(base_photo_path) and os.path.isfile(unknown_photo_path):
		picture_of_user = face_recognition.load_image_file(base_photo_path)
		user_face_encoding = face_recognition.face_encodings(picture_of_user)[0]

		unknown_picture = face_recognition.load_image_file(unknown_photo_path)
		unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]

		results = face_recognition.compare_faces([user_face_encoding], unknown_face_encoding)

		return results[0] == True
	else:
		return False