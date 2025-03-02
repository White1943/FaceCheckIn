from flask import jsonify

class Result:
    @staticmethod
    def success(data=None, message="请求成功"):
        return jsonify({
            "status": "success",
            "message": message,
            "data": data
        }), 201

    @staticmethod
    def error(message="出现异常", data=None, status_code=400):
        return jsonify({
            "status": "error",
            "message": message,
            "data": data
        }), status_code
