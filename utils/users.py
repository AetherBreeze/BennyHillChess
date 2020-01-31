from app import webapp_db
from app.models import GuestUser
from base64 import b64encode
from datetime import datetime
from random import choice
from constants import NAMES_FILEPATH


def add_guest_user(session): # POSSIBLE ERROR: if person A has name X, and then person B takes name X, but coincidentially gets the same ID as person A, then person A can steal person B's guest account
    guest_username = get_random_name()  # get_random_name() ensures the name is not already in use, as long as there are under 64^30 + 1 users
    new_user = GuestUser(username=guest_username,
                         last_active_datetime=datetime.utcnow(),
                         avatar_url="/static/img/avatars/default.png",
                         online=True)  # add the user to the database...
    webapp_db.session.add(new_user) # don't need to commit here, the rest of the index() route does it for us
    webapp_db.session.commit() # just fucking kidding
    session["username"] = guest_username  # ...and remember that this session corresponds to that guest user
    session["id"] = new_user.id

    print("New user added: {}".format(guest_username)) # TODO: actual logging functionality
    return new_user


def get_random_name(): # POSSIBLE ERROR: what if the base64 encoding of len(names_in_use) happens to be an in-use pony name?
    with open(NAMES_FILEPATH) as f:
        possible_names = [line[:-1] for line in f.readlines()] # strip the newline off of every name || can't just do this to the successful name because then comparisons to existing names won't work

    current_users = GuestUser.query.all()
    if len(current_users) == 0:
        return choice(possible_names) # fallback to just use the name if there are no other users
    while len(possible_names) > 0: # try to find a horse name that isn't already in use
        candidate_name = choice(possible_names)
        name_is_used = False
        for user in current_users:
            if user.username == candidate_name:
                if (datetime.utcnow() - user.last_active_datetime).total_seconds() > 3600: # if the account has been inactive for more than an hour
                    webapp_db.session.delete(user) # then this account can be replaced
                    break # break to commit this deletion and start using this name
                else: # otherwise, this acct is recently active
                    possible_names.remove(candidate_name) # so we can't use this name
                    name_is_used = True
                    break # get out of the for loop, since we already know this name is taken
        if not name_is_used: # if this name is unused, use it
            webapp_db.session.commit() # ONLY commit after we've found a name, so we don't lose access to the other users
            return candidate_name

    return str(b64encode(len(current_users)), "utf-8")  # if there are no horse names available, use the base64 encoding of how many names are in use
                                                       # (this should avoid both collisions and overflow of the database's name field, assuming there are under 64^30 + 1 accounts

def update_user_active_time(user_id):
    GuestUser.query.filter_by(id=user_id).first().last_active_datetime = datetime.utcnow()
    webapp_db.session.commit()
