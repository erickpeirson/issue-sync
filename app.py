from sync.factory import create_app
from sync.services import database

app = create_app()

with app.app_context():
    database.create_all()