import json

from shared import classes


def lambda_handler(event, context):
    obj = classes.SharedClass()
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": obj.get_value()
        })
    }
