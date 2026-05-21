
def error_400(msg):
    return ({
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
    return ({
                "errors": [
                    {
                        "code": "404",
                        "message": "NOT FOUND",
                        "level": "error",
                        "description": str(msg)
                    }
                ]
            }), 404

def error_500(msg):
    return ({
                "errors": [
                    {
                        "code": "500",
                        "message": "INTERNAL SERVER ERROR",
                        "level": "error",
                        "description": str(msg)
                    }
                ]
            }), 500