from flask import jsonify


def error_400(msg):
    return jsonify({
                "errors": [
                    {
                        "code": "400",
                        "message": "BAD REQUEST",
                        "level": "error",
                        "description": str(msg)
                    }
                ]
            }), 400

def error_404(msg):
    return jsonify({
                "errors": [
                    {
                        "code": "404",
                        "message": "NOT FOUND",
                        "level": "error",
                        "description": str(msg)
                    }
                ]
            }), 404