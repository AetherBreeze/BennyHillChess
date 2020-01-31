from app import socketio_handler, application, webapp_db
from app.models import GuestUser

if __name__ == "__main__":
    former_online_users = GuestUser.query.filter_by(online=True) # mark everyone that was online when the server closed as offline now
    for user in former_online_users: # so we don't have a million ghosts floating around forever
        user.online = False
    webapp_db.session.commit()

    socketio_handler.run(application)
