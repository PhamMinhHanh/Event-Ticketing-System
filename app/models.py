from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Bảng Danh mục sự kiện
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

# Bảng Sự kiện
class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    organizer_id = db.Column(db.BigInteger, db.ForeignKey('organizers.user_id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    province = db.Column(db.String(100), nullable=False, default="TP.HCM")  
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    banner_url = db.Column(db.String(255), nullable=True)
    base_price = db.Column(db.Numeric(12, 2), default=0)
    status = db.Column(db.Enum('DRAFT', 'PUBLISHED', 'CLOSED', 'CANCELLED'), default='DRAFT')
    checkin_mode = db.Column(db.Enum('QR', 'FACE', 'BOTH'), default='QR')
    ticket_types = db.relationship('TicketType', backref='event', lazy=True)

# BẢNG LOẠI VÉ
class TicketType(db.Model):
    __tablename__ = 'ticket_types'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity_total = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Integer, default=0)
    sale_start = db.Column(db.DateTime, nullable=True)
    sale_end = db.Column(db.DateTime, nullable=True)
    refund_policy_days = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE'), default='ACTIVE')

# BẢNG ĐẶT VÉ
class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_code = db.Column(db.String(50), unique=True, nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.BigInteger, db.ForeignKey('events.id'), nullable=False)
    status = db.Column(db.Enum('PENDING', 'PAID', 'CANCELLED', 'REFUNDED', 'FAILED', 'EXPIRED'), nullable=False)
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    discount_amount = db.Column(db.Numeric(12, 2), default=0)
    final_amount = db.Column(db.Numeric(12, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    order_id = db.Column(db.BigInteger, db.ForeignKey('orders.id'), nullable=False)
    ticket_type_id = db.Column(db.BigInteger, db.ForeignKey('ticket_types.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    line_total = db.Column(db.Numeric(12, 2), nullable=False)

# BẢNG VÉ
class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ticket_code = db.Column(db.String(60), unique=True, nullable=False)
    order_item_id = db.Column(db.BigInteger, db.ForeignKey('order_items.id'), nullable=False)
    
    qr_token = db.Column(db.String(255), unique=True, nullable=False)
    status = db.Column(db.Enum('ISSUED', 'CHECKED_IN', 'CANCELLED', 'REFUNDED'), default='ISSUED')
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)

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

# BẢNG CHECKIN
class Checkin(db.Model):
    __tablename__ = 'checkins'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    ticket_id = db.Column(db.BigInteger, db.ForeignKey('tickets.id'), nullable=False)
    checked_in_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    checkin_method = db.Column(db.Enum('QR', 'FACE', 'MANUAL'), nullable=False)
    matched_score = db.Column(db.Numeric(5, 4), nullable=True) # Dành cho FaceID sau này
    result = db.Column(db.Enum('SUCCESS', 'FAILED'), nullable=False)
    checkin_time = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(255), nullable=True)