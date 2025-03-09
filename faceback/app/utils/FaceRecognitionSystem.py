import face_recognition
class FaceRecognitionSystem:
  def __init__(self):
    self.known_faces = {}
    self.known_face_encodings = []
    self.known_face_names = []

  def add_person(self, name, image_path):
    """添加新人员到系统"""
    try:
      # 加载并编码人脸
      image = face_recognition.load_image_file(image_path)
      encodings = face_recognition.face_encodings(image)

      if len(encodings) == 0:
        raise ValueError("No face found in the image")

      if len(encodings) > 1:
        print(f"Warning: Multiple faces found in {image_path}. Using the first one.")

      # 存储编码
      self.known_faces[name] = encodings[0]
      self.known_face_encodings.append(encodings[0])
      self.known_face_names.append(name)

      return True

    except Exception as e:
      print(f"Error adding person: {str(e)}")
      return False

  def identify_person(self, image_path, tolerance=0.6):
    """识别图片中的人脸"""
    try:
      # 加载要识别的图片
      image = face_recognition.load_image_file(image_path)
      # 获取图片中所有人脸的编码
      face_encodings = face_recognition.face_encodings(image)

      results = []
      for face_encoding in face_encodings:
        # 与所有已知人脸比较
        matches = face_recognition.compare_faces(
          self.known_face_encodings,
          face_encoding,
          tolerance=tolerance
        )

        # 计算人脸距离
        face_distances = face_recognition.face_distance(
          self.known_face_encodings,
          face_encoding
        )

        if True in matches:
          # 找到最佳匹配
          best_match_index = np.argmin(face_distances)
          name = self.known_face_names[best_match_index]
          confidence = 1 - face_distances[best_match_index]
          results.append({
            'name': name,
            'confidence': confidence
          })
        else:
          results.append({
            'name': 'unknown',
            'confidence': 0
          })

      return results

    except Exception as e:
      print(f"Error during identification: {str(e)}")
      return []
