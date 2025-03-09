from app import create_app

from app.utils.FaceRecognitionSystem import FaceRecognitionSystem
app = create_app()

if __name__ == '__main__':
      face_system = FaceRecognitionSystem()
      app.run(debug=True,port=5001)
# run.py
