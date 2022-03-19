from app import db
from models import User

db.drop_all()
db.create_all()

han = User.registerUser('HanSolo', 'Chewie', 'ishotfirst@gmail.com', 'Han', 'Solo')
alison = User.registerUser('tooManyGhosts', 'Mike', 'buttonhouse@email.com', 'Alison', 'Cooper')

db.session.add_all([han, alison])
db.session.commit()