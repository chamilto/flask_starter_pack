from jsonschema import Draft4Validator

register_user_schema = Draft4Validator(
    schema={
        "title": "Register User",
        "type": "object",
        "properties": {
            "firstName": {
                "type": "string"
            },
            "lastName": {
                "type": "string"
            },
            "username": {
                "description": "username",
                "type": "string"
            },
            "email": {
                "description": "email address",
                "type": "string"
            },
            "password": {
                "type": "string"
            },
        },
        "required": ["username", "password", "email"]
    }
)

confirm_registration_schema = Draft4Validator(
    schema={
        "title": "Confirm Registration",
        "type": "object",
        "properties": {
            "registrationCode": {
                "type": "integer",
            },
        },
        "required": ["registrationCode"]
    }
)
