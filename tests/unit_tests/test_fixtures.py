import uuid

from database import Price, Tag, db


def test_price(app, price_1):
    # test with query
    price_1 = Price.query.get(price_1.id)
    assert price_1.internal_product_id == "1"


def test_isolation(app):
    tag = Tag(id=str(uuid.uuid4()), name="Test tag 1")
    db.session.add(tag)
    db.session.commit()

    assert len(Tag.query.all()) == 1

    tag_db = Tag.query.first()
    assert tag_db.name == "Test tag 1"


def test_isolation2(app):
    tag = Tag(id=str(uuid.uuid4()), name="Test tag 3")
    db.session.add(tag)
    db.session.commit()

    assert len(Tag.query.all()) == 1
    # test with query
    tag_db = tag.query.first()
    assert tag_db.name == "Test tag 3"


def test_user(app, member):
    assert "member" == member.roles[0]
