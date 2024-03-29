from ast import literal_eval
from typing import Dict, List, Optional

import structlog
from database import db
from flask_restplus import abort
from sqlalchemy import String, cast, or_
from sqlalchemy.sql import expression

logger = structlog.get_logger(__name__)


def get_range_from_args(args):
    if args["range"]:
        range = []
        try:
            input = args["range"][1:-1].split(",")
            for i in input:
                range.append(int(i))
            logger.info("Query parameters set to custom range", range=range)
            return range
        except:  # noqa: E722
            logger.warning(
                "Query parameters not parsable",
                args=args.get(["range"], "No range provided"),
            )
    range = [0, 19]  # Default range
    logger.info("Query parameters set to default range", range=range)
    return range


def get_sort_from_args(args, default_sort="name", default_sort_order="ASC"):
    sort = []
    if args["sort"]:
        try:
            input = args["sort"].split(",")
            sort.append(input[0][2:-1])
            sort.append(input[1][1:-2])
            logger.info("Query parameters set to custom sort", sort=sort)
            return sort
        except:  # noqa: E722
            logger.warning(
                "Query parameters not parsable",
                args=args.get(["sort"], "No sort provided"),
            )
    sort = [default_sort, default_sort_order]  # Default sort
    logger.info("Query parameters set to default sort", sort=sort)
    return sort


def get_filter_from_args(args, default_filter={}):
    if args["filter"]:
        print(args["filter"])
        try:

            filter = literal_eval(
                args["filter"].replace(":true", ":True").replace(":false", ":False")
            )
            logger.info("Query parameters set to custom filter", filter=filter)
            return filter
        except:  # noqa: E722
            logger.warning(
                "Query parameters not parsable",
                args=args.get(["filter"], "No filter provided"),
            )
    logger.info("Query parameters set to default filter", filter=default_filter)
    return default_filter


def save(item):
    try:
        db.session.add(item)
        db.session.commit()
    except Exception as error:
        db.session.rollback()
        abort(400, "DB error: {}".format(str(error)))


def load(model, id):
    item = model.query.filter_by(id=id).first()
    if not item:
        abort(404, f"Record id={id} not found")
    return item


def update(item, payload):
    if payload.get("id"):
        del payload["id"]
    try:
        for column, value in payload.items():
            setattr(item, column, value)
        save(item)
    except Exception as e:
        abort(500, f"Error: {e}")
    return item


def query_with_filters(
    model,
    query,
    range: List[int] = None,
    sort: List[str] = None,
    filters: Optional[Dict] = None,
    quick_search_columns: List = ["name"],
):
    if filters != "":
        for column, searchPhrase in filters.items():
            if isinstance(searchPhrase, list):
                # OR query
                logger.error(
                    "Returning first only: todo fix", first_item=searchPhrase[0]
                )
                searchPhrase = searchPhrase[0]
            logger.info("TYPE", searchPhrase=type(searchPhrase))
            logger.info(
                "Query parameters set to custom filter for column",
                column=column,
                searchPhrase=searchPhrase,
            )

            if searchPhrase is not None:
                if type(searchPhrase) == bool:
                    query = query.filter(model.__dict__[column].is_(searchPhrase))
                elif column.endswith("_gt"):
                    query = query.filter(model.__dict__[column[:-3]] > searchPhrase)
                elif column.endswith("_gte"):
                    query = query.filter(model.__dict__[column[:-4]] >= searchPhrase)
                elif column.endswith("_lte"):
                    query = query.filter(model.__dict__[column[:-4]] <= searchPhrase)
                elif column.endswith("_lt"):
                    query = query.filter(model.__dict__[column[:-3]] < searchPhrase)
                elif column.endswith("_ne"):
                    query = query.filter(model.__dict__[column[:-3]] != searchPhrase)
                elif column == "id":
                    query = query.filter_by(id=searchPhrase)
                elif column == "q":
                    logger.debug(
                        "Activating multi kolom filter",
                        column=column,
                        quick_search_columns=quick_search_columns,
                    )
                    conditions = []
                    for item in quick_search_columns:
                        conditions.append(
                            cast(model.__dict__[item], String).ilike(
                                "%" + searchPhrase + "%"
                            )
                        )
                    query = query.filter(or_(*conditions))
                else:
                    query = query.filter(
                        cast(model.__dict__[column], String).ilike(
                            "%" + searchPhrase + "%"
                        )
                    )

    if sort and len(sort) == 2:
        if sort[1].upper() == "DESC":
            query = query.order_by(expression.desc(model.__dict__[sort[0]]))
        else:
            query = query.order_by(expression.asc(model.__dict__[sort[0]]))

    range_start = int(range[0])
    range_end = int(range[1])
    # Range is inclusive so we need to add one
    if len(range) >= 2:
        # Range is inclusive so we need to add one
        total = query.count()
        range_length = max(range_end - range_start + 1, 0)
        query = query.offset(range_start)
        query = query.limit(range_length)
    else:
        total = query.count()

    content_range = f"items {range_start}-{range_end}/{total}"

    return query.all(), content_range
