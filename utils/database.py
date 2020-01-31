from datetime import datetime

def add_single_item(sqlalchemy_db, item_to_add):
    sqlalchemy_db.session.add(item_to_add)
    sqlalchemy_db.session.commit()


def add_multiple_items(sqlalchemy_db, items_to_add):
    for item in items_to_add:
        sqlalchemy_db.session.add(item)
    sqlalchemy_db.session.commit()


def delete_all_items(sqlalchemy_db, model):
    for item in model.query.all():
        sqlalchemy_db.session.delete(item)
    sqlalchemy_db.session.commit()


def sign_on_user(sqlalchemy_db, user, user_sid):
    user.current_game = 0
    user.last_active_datetime = datetime.utcnow()
    user.online = True
    user.websocket_id = user_sid
    sqlalchemy_db.session.commit()


def sign_off_user(sqlalchemy_db, user):
    user.current_game = 0
    user.last_active_datetime = datetime.utcnow()
    user.online = False
    sqlalchemy_db.session.commit()
