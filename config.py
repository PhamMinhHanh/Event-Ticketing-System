import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mot-chuoi-bi-mat-bat-ky-cua-nhom-7'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ticket_user:123456@localhost/event_ticketing'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- CẤU HÌNH THANH TOÁN VNPAY SANDBOX ---
    VNPAY_TMN_CODE = "VVUJIGW6"
    VNPAY_HASH_SECRET = "FRJ57Y1VV27PJSTNVFMGNQHWEUT13YX1"
    VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    VNPAY_RETURN_URL = "http://127.0.0.1:5000/vnpay_return"

    # Cấu hình upload ảnh
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads', 'banners')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # Giới hạn file tối đa 5MB