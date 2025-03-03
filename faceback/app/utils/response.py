from flask import jsonify

class Result:
    @staticmethod
    def success(data=None, message="操作成功", code=200):
        return jsonify({
            "code": 200,
            "message": message,
            "data": data
        })

    @staticmethod
    def error(message="操作失败", code=400, data=None):
        return jsonify({
            "code": code,
            "message": message,
            "data": data
        }), code
