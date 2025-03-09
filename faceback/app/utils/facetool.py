# d进行辅助，完成人脸编码，匹配等
import face_recognition


def create_known_face(image_path):
  """从单个图片创建known_face编码"""
  # 加载图片
  image = face_recognition.load_image_file(image_path)
  # 获取人脸编码
  face_encodings = face_recognition.face_encodings(image)

  if len(face_encodings) > 0:
    return face_encodings[0]  # 返回第一个人脸的编码
  return None


def create_known_faces_database():
  """创建人脸数据库"""
  known_faces = {}

  # 假设图片存储在 known_people 文件夹中
  known_people_folder = "known_people"

  # 遍历文件夹中的所有图片
  for filename in os.listdir(known_people_folder):
    if filename.endswith((".jpg", ".jpeg", ".png")):
      # 使用文件名作为人名（去掉扩展名）
      name = os.path.splitext(filename)[0]
      image_path = os.path.join(known_people_folder, filename)

      # 获取人脸编码
      encoding = create_known_face(image_path)
      if encoding is not None:
        known_faces[name] = encoding

  return known_faces

