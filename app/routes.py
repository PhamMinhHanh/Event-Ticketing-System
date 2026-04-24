from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User, Organizer, Event, Category, TicketType

# Khởi tạo Blueprint thay vì gọi trực tiếp biến 'app'
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    #Duyệt và Tìm kiếm sự kiện
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)
    
    events_query = Event.query
    if query:
        events_query = events_query.filter(Event.title.contains(query))
    if category_id:
        events_query = events_query.filter_by(category_id=category_id)
        
    events = events_query.all()
    categories = Category.query.all()
    return render_template('index.html', events=events, categories=categories)

@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    #Xem chi tiết sự kiện và chọn loại vé
    event = Event.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Tìm user trong Database
        user = User.query.filter_by(email=email).first()

        # Kiểm tra user có tồn tại và mật khẩu có khớp không
        if user and user.check_password(password):
            # Lưu thông tin vào session (Phiên làm việc)
            session['user_id'] = user.id
            session['user_name'] = user.full_name
            session['user_role'] = user.role
            
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('main.index')) # Chuyển về trang chủ
        else:
            flash('Email hoặc mật khẩu không chính xác!', 'error')

    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    # Xóa sạch thông tin trong phiên làm việc
    session.clear()
    flash('Bạn đã đăng xuất thành công.', 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role') # 'USER' hoặc 'ORGANIZER'
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')

        # Kiểm tra email đã tồn tại chưa
        if User.query.filter_by(email=email).first():
            flash('Email này đã được đăng ký!', 'danger')
            return redirect(url_for('main.register'))

        # Tạo user mới
        new_user = User(full_name=full_name, email=email, phone=phone, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush() # Lấy ID của user vừa tạo

        # Nếu là Nhà tổ chức, lưu thêm vào bảng Organizer
        if role == 'ORGANIZER':
            org_name = request.form.get('org_name')
            new_org = Organizer(user_id=new_user.id, name=org_name)
            db.session.add(new_org)

        db.session.commit()
        flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')