import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mot-chuoi-bi-mat-bat-ky-cua-nhom-7'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ticket_user:123456@localhost/event_ticketing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False