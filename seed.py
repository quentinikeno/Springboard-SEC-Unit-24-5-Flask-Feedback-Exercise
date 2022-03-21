from app import db
from models import User, Feedback

db.drop_all()
db.create_all()

han = User.registerUser('HanSolo', 'Chewie', 'shotfirst@gmail.com', 'Han', 'Solo')
alison = User.registerUser('tooManyGhosts', 'Mike', 'buttonhouse@email.com', 'Alison', 'Cooper')

db.session.add_all([han, alison])
db.session.commit()

lorem1 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
lorem2 = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Egestas dui id ornare arcu odio. Suspendisse ultrices gravida dictum fusce ut. Erat nam at lectus urna duis. Habitant morbi tristique senectus et netus et malesuada. Libero enim sed faucibus turpis. Posuere urna nec tincidunt praesent semper feugiat nibh sed. Sed faucibus turpis in eu mi bibendum neque egestas. Enim facilisis gravida neque convallis a cras. Ultrices eros in cursus turpis massa tincidunt dui ut ornare. Scelerisque viverra mauris in aliquam sem fringilla. Lectus arcu bibendum at varius vel pharetra. Tellus molestie nunc non blandit. Bibendum at varius vel pharetra vel.'

hanFeedback = Feedback(title='Kessel Run', content=lorem1, username=han.username)
alisonFeedback = Feedback(title='Too Many Roomates', content=lorem2, username=alison.username)

db.session.add_all([hanFeedback, alisonFeedback])
db.session.commit()