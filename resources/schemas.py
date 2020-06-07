#!/usr/bin/python
# -*- coding: utf-8 -*-

SchemaUserToken = {
    "type": "object",
    "properties": {
        "token": {"type": "string"},
    },
    "required": ["token"]
}

SchemaRegisterUser = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "password": {"type": "string"},
        "email": {"type": "string"},
        "name": {"type": "string"},
        "surname": {"type": "string"},
        "genere": {"type": "string"}
    },
    "required": ["username", "password", "email", "name", "surname", "genere"]
}

SchemaCreateAnunci = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "description": {"type": "string"},
        "price": {"type": "float"},
        "level": {"type": "string"},
        "admits_negotiation": {"type": "boolean"},
        "distance_to_serve": {"type": "integer"},
        "type": {"type": "string"},
    },
    "required": ["title", "description", "price", "level", "admits_negotiation", "distance_to_serve", "type"]
}
