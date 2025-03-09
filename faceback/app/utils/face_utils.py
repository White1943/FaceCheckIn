import face_recognition
import os
from werkzeug.utils import secure_filename
import numpy as np

class FaceUtils:
    def __init__(self, upload_folder='uploads', known_faces_folder='pics'):
        self.upload_folder = upload_folder
        self.known_faces_folder = known_faces_folder
        
    def save_upload_file(self, file):
        """保存上传的图片"""
        filename = secure_filename(file.filename)
        filepath = os.path.join(self.upload_folder, filename)
        file.save(filepath)
        return filepath
        
    def get_face_encoding(self, image_path):
        """获取图片中的人脸编码"""
        image = face_recognition.load_image_file(image_path)
        face_encodings = face_recognition.face_encodings(image)
        return face_encodings[0] if face_encodings else None
        
    def compare_faces(self, known_face_path, unknown_face_path, tolerance=0.6):
        """比较两张图片中的人脸是否匹配"""
        try:
            known_image = face_recognition.load_image_file(known_face_path)
            unknown_image = face_recognition.load_image_file(unknown_face_path)
            
            known_encoding = face_recognition.face_encodings(known_image)[0]
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            
            results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance)
            return results[0]
        except Exception as e:
            print(f"Face comparison error: {str(e)}")
            return False 