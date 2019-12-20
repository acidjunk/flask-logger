from flask_restplus import Api

from .v1.logs import api as logs_ns

api = Api(
    title="Flask logger",
    version="1.0",
    description="A restful api for the Flask HTTP Request logger. Add a log by visiting: http://fiber.formatics.nl:8888/log",
)
api.add_namespace(logs_ns, path="/v1/logs")
