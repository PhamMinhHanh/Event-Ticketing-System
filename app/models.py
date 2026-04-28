from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Bảng Danh mục sự kiện
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    events = db.relationship('Event', backref='category', lazy=True)

# Bảng Sự kiện
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    province = db.Column(db.String(100), nullable=False, default="TP.HCM")  
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    banner_url = db.Column(db.String(255), nullable=True)
    base_price = db.Column(db.Float, nullable=False, default=0.0)
    category_id = db.Column(db.BigInteger, db.ForeignKey('categories.id'), nullable=False)
    
    # Khóa ngoại với Organizer
    organizer_id = db.Column(db.BigInteger, db.ForeignKey('organizers.user_id'), nullable=False)
    
    # Relationship
    organizer = db.relationship('Organizer', backref=db.backref('events', lazy=True))


# Bảng Loại vé
class TicketType(db.Model):
    __tablename__ = 'ticket_types'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.id'))
    name = db.Column(db.String(100), nullable=False) # VD: Vé VIP, Vé Thường
    price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity_total = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Integer, default=0)

# Bảng Người dùng chung
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('USER', 'ORGANIZER', 'ADMIN'), default='USER', nullable=False)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'BANNED'), default='ACTIVE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Hàm hỗ trợ mã hóa mật khẩu
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Bảng chi tiết Nhà tổ chức
class Organizer(db.Model):
    __tablename__ = 'organizers'
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), primary_key=True)
    name = db.Column(db.String(200), nullable=False) # Tên đơn vị tổ chức
    bio = db.Column(db.Text, nullable=True)
    verified = db.Column(db.Boolean, default=False)