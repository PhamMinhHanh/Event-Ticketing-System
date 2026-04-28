from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models import User, Organizer, Event, Category, TicketType

# Khởi tạo Blueprint thay vì gọi trực tiếp biến 'app'
main_bp = Blueprint('main', __name__)

# Dữ liệu  toàn cục, mọi file HTML gọi được
@main_bp.context_processor
def inject_global_vars():
    categories = Category.query.all()
    # Lấy Tỉnh/Thành phố không trùng lặp
    provinces_data = db.session.query(Event.province).distinct().all()
    provinces = [p[0] for p in provinces_data if p[0]]
    return dict(categories=categories, provinces=provinces)

@main_bp.route('/')
def index():
    keyword = request.args.get('q', '')
    category_id = request.args.get('category')
    province = request.args.get('province')

    query = Event.query

    # Tìm trong tiêu đề HOẶC mô tả
    if keyword:
        # không phân biệt chữ hoa/chữ thường
        query = query.filter(db.or_(
            Event.title.ilike(f'%{keyword}%'),
            Event.description.ilike(f'%{keyword}%')
        ))

    # Lọc theo danh mục
    if category_id and category_id.isdigit():
        query = query.filter(Event.category_id == int(category_id))

    # Lọc theo địa điểm (Tỉnh/Thành phố)
    if province and province != 'all':
        query = query.filter(Event.province == province)

    events = query.all()
    categories = Category.query.all()
    
    provinces_data = db.session.query(Event.province).distinct().all()
    provinces = [p[0] for p in provinces_data if p[0]]

    return render_template('index.html', events=events, categories=categories, provinces=provinces)

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

# XỬ LÝ ĐẶT VÉ
@main_bp.route('/checkout/<int:event_id>', methods=['GET', 'POST'])
def checkout(event_id):
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để tiến hành đặt vé!', 'error')
        return redirect(url_for('main.login'))

    event = Event.query.get_or_404(event_id)

    # 1. NẾU LÀ POST: Người dùng vừa bấm "Tiếp tục đặt vé" từ trang chi tiết
    if request.method == 'POST':
        cart = []
        total_amount = 0

        # Quét qua tất cả các ô nhập số lượng vé gửi lên
        for key, value in request.form.items():
            if key.startswith('ticket_') and int(value) > 0:
                ticket_type_id = int(key.split('_')[1])
                qty = int(value)
                ticket_type = TicketType.query.get(ticket_type_id)

                # Xác minh vé hợp lệ và tính tiền
                if ticket_type and ticket_type.event_id == event.id:
                    subtotal = qty * float(ticket_type.price)
                    total_amount += subtotal
                    cart.append({
                        'ticket_type_id': ticket_type.id,
                        'name': ticket_type.name,
                        'price': float(ticket_type.price),
                        'quantity': qty,
                        'subtotal': float(subtotal)
                    })

        # Báo lỗi nếu chưa chọn vé nào
        if not cart:
            flash('Vui lòng chọn ít nhất 1 vé để tiếp tục!', 'error')
            return redirect(url_for('main.event_detail', event_id=event.id))

        # Lưu toàn bộ giỏ hàng vào Session
        session['cart'] = {
            'event_id': event.id,
            'items': cart,
            'total_amount': total_amount
        }
        # Chuyển hướng sang giao diện điền thông tin Checkout
        return redirect(url_for('main.checkout', event_id=event.id))

    # 2. NẾU LÀ GET: Hiển thị giao diện trang Checkout
    cart_data = session.get('cart')
    
    # Chặn nếu nhảy vào link này mà chưa chọn vé
    if not cart_data or cart_data['event_id'] != event.id:
        flash('Giỏ hàng trống. Vui lòng chọn vé trước.', 'error')
        return redirect(url_for('main.event_detail', event_id=event.id))

    return render_template('checkout.html', event=event, cart=cart_data)