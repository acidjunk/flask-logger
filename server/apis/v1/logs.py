import json

import structlog
from apis.helpers import (
    get_filter_from_args,
    get_range_from_args,
    get_sort_from_args,
    load,
    query_with_filters,
)
from database import Log
from flask_restplus import Namespace, Resource, fields, marshal_with

logger = structlog.get_logger(__name__)

api = Namespace("logs", description="Log operations")

header_wildcard = fields.Wildcard(fields.String)

log_serializer = api.model(
    "Log",
    {
        "id": fields.String(),
        "ip": fields.String(),
        "full_headers": header_wildcard,
        "remote_port": fields.Integer(required=True, description="Remote protocol"),
        "server_protocol": fields.String(required=True, description="Server protocol"),
        "http_connection": fields.String(required=True, description="HTTP Connection"),
        "http_cache_control": fields.String(
            required=True, description="Cache control header"
        ),
        "body": fields.String(required=True, description="Body of request"),
        "created_at": fields.DateTime(required=True, description="Date for log entry"),
    },
)

parser = api.parser()
parser.add_argument("range", location="args", help="Pagination: default=[0,19]")
parser.add_argument("sort", location="args", help='Sort: default=["name","ASC"]')
parser.add_argument("filter", location="args", help="Filter default=[]")


@api.route("/")
@api.doc("Show all logs.")
class LogResourceList(Resource):
    @marshal_with(log_serializer)
    @api.doc(parser=parser)
    def get(self):
        """List Logs"""
        args = parser.parse_args()
        range = get_range_from_args(args)
        sort = get_sort_from_args(args, "created_at", "DESC")
        filter = get_filter_from_args(args)

        query_result, content_range = query_with_filters(
            Log, Log.query, range, sort, filter, quick_search_columns=["ip"]
        )
        for item in query_result:
            item.full_headers = json.loads(item.headers)
        return query_result, 200, {"Content-Range": content_range}


@api.route("/<id>")
@api.doc("Log detail operations.")
class LogResource(Resource):
    @marshal_with(log_serializer)
    def get(self, id):
        """List Log"""
        item = load(Log, id)
        return item, 200
