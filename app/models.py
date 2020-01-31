from app import webapp_db



# GuestUser is the default user class; it's assigned to everyone when they first visit the site
class GuestUser(webapp_db.Model):
    __tablename__ = "users"

    id = webapp_db.Column(webapp_db.Integer, primary_key=True)
    username = webapp_db.Column(webapp_db.String(32), index=True, unique=True)
    last_active_datetime = webapp_db.Column(webapp_db.DateTime, index=True)
    websocket_id = webapp_db.Column(webapp_db.String(32)) # unique by WebSockets implementation, so we don't have to specify unique here
    current_game = webapp_db.Column(webapp_db.Integer)
    avatar_url = webapp_db.Column(webapp_db.String(48))
    online = webapp_db.Column(webapp_db.Boolean, index=True) # index by online to make populating the user list faster

    def __repr__(self):
        return "<GuestUser | id: {} | username: {}>".format(self.id, self.username)
