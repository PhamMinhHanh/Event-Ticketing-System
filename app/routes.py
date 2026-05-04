from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from app import db
from app.models import User, Organizer, Event, Category, TicketType,  Order, OrderItem, Ticket, Checkin
import time
from datetime import datetime
from app.vnpay import vnpay 
import uuid
import os
from werkzeug.utils import secure_filename
import json

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

# ===================== [Tìm và lọc tìm kiếm] ========================
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

# ======================== [CHI TIẾT SỰ KIỆN] ========================
@main_bp.route('/event/<int:event_id>')
def event_detail(event_id):
    #Xem chi tiết sự kiện và chọn loại vé
    event = Event.query.get_or_404(event_id)
    organizer = User.query.get(event.organizer_id) # Lấy data Ban tổ chức
    ticket_types = TicketType.query.filter_by(event_id=event.id).all()

    return render_template('event_detail.html', event=event, ticket_types=ticket_types, organizer=organizer, now=datetime.now())

# ======================== [LOGIN] ========================
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

# ======================== [LOGOUT] ========================
@main_bp.route('/logout')
def logout():
    # Xóa sạch thông tin trong phiên làm việc
    session.clear()
    flash('Bạn đã đăng xuất thành công.', 'success')
    return redirect(url_for('main.index'))

# ======================== [ĐĂNG KÝ] ========================
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form.get('role') # 'USER' hoặc 'ORGANIZER'
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        
        # Lấy dữ liệu theo role
        if role == 'ORGANIZER':
            organization_name = request.form.get('organization_name')
            # Gán organization_name cho full_name để lưu vào bảng User
            full_name = organization_name 
        else:
            full_name = request.form.get('full_name')

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
            # SỬA LỖI TẠI ĐÂY: Dùng chung biến organization_name
            new_org = Organizer(user_id=new_user.id, name=organization_name)
            db.session.add(new_org)

        db.session.commit()
        flash('Đăng ký thành công! Hãy đăng nhập.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

# ======================== [XỬ LÝ ĐẶT VÉ] ========================
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

# ======================== [XỬ LÝ THANH TOÁN VN PAY] ========================
@main_bp.route('/process_checkout/<int:event_id>', methods=['POST'])
def process_checkout(event_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    cart_data = session.get('cart')
    if not cart_data or cart_data['event_id'] != event_id:
        flash('Giỏ hàng không hợp lệ.', 'error')
        return redirect(url_for('main.event_detail', event_id=event_id))

    # 1. Tạo mã đơn hàng duy nhất (Ví dụ: EVB-20260429153012)
    order_code = f"EVB-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    total_amount = cart_data['total_amount']

    # 2. Lưu Đơn hàng (Order) vào Database với trạng thái PENDING
    new_order = Order(
        order_code=order_code,
        user_id=session['user_id'],
        event_id=event_id,
        status='PENDING',
        total_amount=total_amount,
        final_amount=total_amount
    )
    db.session.add(new_order)
    db.session.commit() # Commit để lấy được new_order.id

    # 3. Lưu Chi tiết đơn hàng (Order Items) và trừ số lượng vé
    for item in cart_data['items']:
        order_item = OrderItem(
            order_id=new_order.id,
            ticket_type_id=item['ticket_type_id'],
            quantity=item['quantity'],
            unit_price=item['price'],
            line_total=item['subtotal']
        )
        db.session.add(order_item)
        
        # Cập nhật số vé đã bán
        ticket_type = TicketType.query.get(item['ticket_type_id'])
        if ticket_type:
            ticket_type.quantity_sold += item['quantity']

    db.session.commit()

    # Xóa giỏ hàng khỏi session vì đã tạo đơn thành công
    session.pop('cart', None)

    # 4. CHUẨN BỊ DỮ LIỆU GỬI SANG VNPAY
    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = current_app.config['VNPAY_TMN_CODE']
    
    # Lưu ý: VNPAY yêu cầu số tiền phải nhân với 100 (Bỏ phần thập phân)
    vnp.requestData['vnp_Amount'] = int(total_amount * 100) 
    
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = order_code
    vnp.requestData['vnp_OrderInfo'] = f"Thanh toan ve su kien {event_id} ma don {order_code}"
    vnp.requestData['vnp_OrderType'] = 'billpayment'
    vnp.requestData['vnp_Locale'] = 'vn'
    
    # Thời gian tạo giao dịch
    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')
    vnp.requestData['vnp_IpAddr'] = request.remote_addr
    vnp.requestData['vnp_ReturnUrl'] = current_app.config['VNPAY_RETURN_URL']

    # 5. TẠO LINK VÀ CHUYỂN HƯỚNG
    vnpay_payment_url = vnp.get_payment_url(
        current_app.config['VNPAY_PAYMENT_URL'], 
        current_app.config['VNPAY_HASH_SECRET']
    )
    
    return redirect(vnpay_payment_url)

# ============================= [Trả kết quả VN Pay] =============================
@main_bp.route('/vnpay_return')
def vnpay_return():
    vnp = vnpay()
    # Lấy toàn bộ dữ liệu VNPAY trả về trên URL
    vnp.responseData = request.args.to_dict()
    
    # Lấy mã đơn hàng và mã kết quả
    order_code = request.args.get('vnp_TxnRef')
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')

    # Lấy chuỗi bí mật từ config
    secret_key = current_app.config['VNPAY_HASH_SECRET']

    # 1. Kiểm tra chữ ký bảo mật (đảm bảo không ai giả mạo URL)
    if vnp.validate_response(secret_key):
        order = Order.query.filter_by(order_code=order_code).first()
        
        if order:
            # Mã 00 nghĩa là khách hàng đã thanh toán thành công
            if vnp_ResponseCode == '00':
                # Chỉ xử lý nếu đơn hàng đang ở trạng thái PENDING
                if order.status == 'PENDING':
                    order.status = 'PAID'
                    
                    # Truy xuất các dòng chi tiết của đơn hàng này
                    order_items = OrderItem.query.filter_by(order_id=order.id).all()
                    
                    for item in order_items:
                        # --- CỘNG DỒN SỐ VÉ ĐÃ BÁN ---
                        ticket_type = TicketType.query.get(item.ticket_type_id)
                        if ticket_type:
                            ticket_type.quantity_sold += item.quantity

                        # Phát hành vé tương ứng với số lượng từng loại
                        for _ in range(item.quantity):
                            # Tạo mã hiển thị trên vé (VD: TK-5-A1B2C3D4)
                            ticket_code = f"TK-{order.id}-{uuid.uuid4().hex[:8].upper()}"
                            
                            # Tạo chuỗi bí mật để render ra mã QR
                            qr_token = str(uuid.uuid4())
                            
                            new_ticket = Ticket(
                                ticket_code=ticket_code,
                                order_item_id=item.id,
                                qr_token=qr_token,
                                status='ISSUED'
                            )
                            db.session.add(new_ticket)
                    
                    # Lưu tất cả vào cơ sở dữ liệu
                    db.session.commit()
                    flash(f'Thanh toán thành công! Mã đơn hàng: {order_code}. Vé điện tử đã được phát hành.', 'success')
                else:
                    flash(f'Đơn hàng {order_code} đã được xử lý trước đó.', 'info')
        else:
            flash('Không tìm thấy thông tin đơn hàng trong hệ thống.', 'error')
    else:
        flash('Lỗi bảo mật: Dữ liệu trả về không hợp lệ!', 'error')

    # Đưa người dùng về trang chủ (hoặc trang Lịch sử mua vé sau này)
    return redirect(url_for('main.index'))

# ================================= [VÉ CỦA TÔI] =================================
@main_bp.route('/my-tickets')
def my_tickets():
    # Chặn người lạ
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xem vé!', 'error')
        return redirect(url_for('main.login'))

    # Lấy danh sách đơn hàng ĐÃ THANH TOÁN của user này, xếp mới nhất lên đầu
    orders = Order.query.filter_by(user_id=session['user_id'], status='PAID').order_by(Order.created_at.desc()).all()
    
    my_events = []
    for order in orders:
        event = Event.query.get(order.event_id)
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        
        ticket_list = []
        for item in order_items:
            ticket_type = TicketType.query.get(item.ticket_type_id)
            # Lấy các vé đã phát hành thuộc dòng đơn hàng này
            tickets = Ticket.query.filter_by(order_item_id=item.id).all()
            for t in tickets:
                ticket_list.append({
                    'code': t.ticket_code,
                    'type_name': ticket_type.name,
                    'qr_token': t.qr_token,
                    'status': t.status
                })
        
        if ticket_list:
            my_events.append({
                'order_code': order.order_code,
                'event_title': event.title,
                'start_time': event.start_time.strftime('%d/%m/%Y %H:%M'),
                'location': event.location,
                'tickets': ticket_list
            })

    return render_template('my_tickets.html', my_events=my_events)

# ================================= [CHECKIN] ======================================
@main_bp.route('/event/<int:event_id>/checkin-scanner')
def checkin_scanner(event_id):
    # Chỉ cho phép Organizer truy cập
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập!', 'error')
        return redirect(url_for('main.login'))
            
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role != 'ORGANIZER':
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('main.index'))
    
    event = Event.query.get_or_404(event_id)
    
    # Đảm bảo Organizer này là chủ nhân của sự kiện
    if event.organizer_id != session['user_id']:
        flash('Bạn không phải ban tổ chức của sự kiện này!', 'error')
        return redirect(url_for('main.index'))
        
    return render_template('checkin_scanner.html', event=event)

@main_bp.route('/api/checkin', methods=['POST'])
def api_checkin():
    # 1. Kiểm tra quyền (Chỉ Organizer mới được check-in) - Truy vấn trực tiếp role từ Database
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập!'}), 401
        
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role != 'ORGANIZER':
        return jsonify({'success': False, 'message': 'Bạn không có quyền thực hiện thao tác này!'}), 403

    # 2. Lấy dữ liệu JavaScript gửi lên
    data = request.get_json()
    qr_token = data.get('qr_token')
    event_id = data.get('event_id')

    if not qr_token or not event_id:
        return jsonify({'success': False, 'message': 'Thiếu dữ liệu mã QR hoặc ID sự kiện!'})

    # 3. Tìm vé theo mã QR
    ticket = Ticket.query.filter_by(qr_token=qr_token).first()
    if not ticket:
        return jsonify({'success': False, 'message': 'Mã QR không hợp lệ hoặc không tồn tại!'})

    # 4. Kiểm tra xem vé này có thuộc về sự kiện đang tổ chức không
    order_item = OrderItem.query.get(ticket.order_item_id)
    order = Order.query.get(order_item.order_id)
    
    if order.event_id != int(event_id):
        return jsonify({'success': False, 'message': 'Vé này KHÔNG thuộc về sự kiện hiện tại!'})

    # 5. Kiểm tra trạng thái vé
    if ticket.status == 'CHECKED_IN':
        return jsonify({'success': False, 'message': 'CẢNH BÁO: Vé này ĐÃ ĐƯỢC SỬ DỤNG trước đó!'})
    elif ticket.status != 'ISSUED':
        return jsonify({'success': False, 'message': f'Trạng thái vé không hợp lệ ({ticket.status})!'})

    # 6. THÀNH CÔNG: Cập nhật trạng thái vé và ghi Log
    ticket.status = 'CHECKED_IN'
    
    new_checkin = Checkin(
        ticket_id=ticket.id,
        checked_in_by=session['user_id'],
        checkin_method='QR',
        result='SUCCESS'
    )
    db.session.add(new_checkin)
    db.session.commit()

    ticket_type = TicketType.query.get(order_item.ticket_type_id)

    return jsonify({
        'success': True,
        'message': 'Hợp lệ! Mời khách vào.',
        'ticket_code': ticket.ticket_code,
        'ticket_type': ticket_type.name
    })

# ============================= [ TẠO SỰ KIỆN ] ========================================
@main_bp.route('/organizer/event/create', methods=['GET', 'POST'])
def create_event():
    # Kiểm tra quyền Organizer
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập!', 'error')
        return redirect(url_for('main.login'))
        
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role != 'ORGANIZER':
        flash('Chỉ Ban tổ chức mới có quyền tạo sự kiện!', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 1. Lấy dữ liệu thông tin sự kiện
        title = request.form.get('title')
        location = request.form.get('location')
        province = request.form.get('province')
        description = request.form.get('description')
        category_id = request.form.get('category')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        sales_start_time_str = request.form.get('sales_start_time')
        sales_end_time_str = request.form.get('sales_end_time')
        checkin_method = request.form.get('checkin_method')

        # Chuyển đổi chuỗi thời gian HTML thành đối tượng datetime của Python
        start_time = datetime.strptime(start_time_str, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_time_str, '%Y-%m-%dT%H:%M')
        sales_start_time = datetime.strptime(sales_start_time_str, '%Y-%m-%dT%H:%M')
        sales_end_time = datetime.strptime(sales_end_time_str, '%Y-%m-%dT%H:%M')

        # --- LOGIC VALIDATE THỜI GIAN ---
        if sales_start_time > start_time:
            flash('Lỗi: Thời gian bắt đầu bán vé không được sau khi sự kiện bắt đầu!', 'error')
            return redirect(url_for('main.create_event'))
            
        if sales_end_time > end_time:
            flash('Lỗi: Thời gian kết thúc bán vé không được vượt quá thời gian kết thúc sự kiện!', 'error')
            return redirect(url_for('main.create_event'))
            
        if sales_start_time >= sales_end_time:
            flash('Lỗi: Thời gian bắt đầu bán phải trước thời gian kết thúc bán!', 'error')
            return redirect(url_for('main.create_event'))

        # 2. Xử lý Upload Ảnh
        banner_file = request.files.get('banner')
        banner_filename = 'default_banner.jpg' # Tên mặc định nếu lỗi

        if banner_file and banner_file.filename != '':
            # Dùng secure_filename để xóa bỏ các ký tự độc hại trong tên file
            filename = secure_filename(banner_file.filename)
            # Thêm timestamp để tên file không bao giờ bị trùng
            unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            
            # Đảm bảo thư mục upload tồn tại
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_folder, exist_ok=True)
            
            # Lưu file vào ổ cứng
            file_path = os.path.join(upload_folder, unique_filename)
            banner_file.save(file_path)
            
            # Chỉ lưu đường dẫn tương đối vào database để render trên web
            banner_filename = f"uploads/banners/{unique_filename}"

        # 3. Tạo Sự kiện mới
        new_event = Event(
            title=title,
            description=description,
            location=location,
            province=province,
            start_time=start_time,
            end_time=end_time,
            banner_url=banner_filename,
            organizer_id=current_user.id,
            category_id=category_id,
            status='PUBLISHED',
            sales_start_time=sales_start_time,
            sales_end_time=sales_end_time,
            checkin_method=checkin_method
        )
        db.session.add(new_event)
        db.session.flush() # flush để lấy được new_event.id lập tức mà chưa cần commit

        # 4. Lưu các loại vé từ Form (Sử dụng getlist vì input có name là mảng ticket_names[])
        ticket_names = request.form.getlist('ticket_names[]')
        ticket_prices = request.form.getlist('ticket_prices[]')
        ticket_quantities = request.form.getlist('ticket_quantities[]')

        # Vòng lặp zip() giúp duyệt song song 3 mảng cùng lúc
        for name, price, quantity in zip(ticket_names, ticket_prices, ticket_quantities):
            if name.strip(): # Bỏ qua nếu tên vé bị rỗng
                new_ticket_type = TicketType(
                    event_id=new_event.id,
                    name=name,
                    price=float(price),
                    quantity_total=int(quantity),
                    quantity_sold=0
                )
                db.session.add(new_ticket_type)

        # TÌM VÀ CẬP NHẬT GIÁ RẺ NHẤT
        # Lọc ra các mức giá hợp lệ (bỏ qua ô trống) và ép kiểu số thực
        valid_prices = [float(p) for p in ticket_prices if p.strip()]
        if valid_prices:
            new_event.base_price = min(valid_prices) # Tìm giá nhỏ nhất
        else:
            new_event.base_price = 0

        # Lưu toàn bộ vào Database
        db.session.commit()
        flash('Tạo sự kiện thành công!', 'success')
        
        # Tạo xong thì đẩy ra trang chi tiết sự kiện vừa tạo để xem thành quả
        return redirect(url_for('main.event_detail', event_id=new_event.id))

    # Nếu là GET thì hiển thị trang form
    categories = Category.query.all()
    return render_template('create_event.html', categories=categories)

# ============================== [SỬA SỰ KIỆN] ========================================
@main_bp.route('/organizer/event/<int:event_id>/edit', methods=['GET', 'POST'])
def edit_event(event_id):
    # 1. Kiểm tra quyền
    if 'user_id' not in session or (session.get('role') != 'ORGANIZER' and session.get('user_role') != 'ORGANIZER'):
        flash('Vui lòng đăng nhập với tài khoản Ban tổ chức!', 'error')
        return redirect(url_for('main.login'))
        
    current_user = User.query.get(session['user_id'])
    
    # 2. Lấy sự kiện và kiểm tra xem có đúng của người này tạo không
    event = Event.query.get_or_404(event_id)
    if event.organizer_id != current_user.id:
        flash('Bạn không có quyền chỉnh sửa sự kiện này!', 'error')
        return redirect(url_for('main.manage_events'))
        
    # Không cho sửa sự kiện đã Hủy hoặc Đã kết thúc (Tùy logic của bạn)
    if event.status == 'CANCELLED':
        flash('Không thể chỉnh sửa sự kiện đã hủy!', 'error')
        return redirect(url_for('main.manage_events'))

    if request.method == 'POST':
        # 3. Lấy dữ liệu Text từ Form
        event.title = request.form.get('title')
        event.category_id = request.form.get('category')
        event.location = request.form.get('location')
        event.province = request.form.get('province')
        event.description = request.form.get('description')
        event.checkin_method = request.form.get('checkin_method')
        
        # 4. Xử lý Thời gian (Nhớ import datetime ở đầu file nếu chưa có)
        from datetime import datetime
        event.start_time = datetime.strptime(request.form.get('start_time'), '%Y-%m-%dT%H:%M')
        event.end_time = datetime.strptime(request.form.get('end_time'), '%Y-%m-%dT%H:%M')
        event.sales_start_time = datetime.strptime(request.form.get('sales_start_time'), '%Y-%m-%dT%H:%M')
        event.sales_end_time = datetime.strptime(request.form.get('sales_end_time'), '%Y-%m-%dT%H:%M')
        
        # Validate logic thời gian cơ bản
        if event.sales_start_time >= event.sales_end_time or event.start_time >= event.end_time:
            flash('Lỗi logic thời gian: Bắt đầu phải trước Kết thúc!', 'error')
            return redirect(url_for('main.edit_event', event_id=event.id))

        # 5. Xử lý Ảnh Banner mới (Chỉ cập nhật nếu họ chọn file mới)
        banner_file = request.files.get('banner')
        if banner_file and banner_file.filename != '':
            # Tạo đường dẫn lưu ảnh (Giống hàm create_event)
            upload_dir = os.path.join('app', 'static', 'uploads', 'banners')
            os.makedirs(upload_dir, exist_ok=True)
            
            # (Tùy chọn) Xóa ảnh cũ nếu nó là ảnh tự upload, không phải link HTTP
            if event.banner_url and not event.banner_url.startswith('http'):
                old_path = os.path.join('app', 'static', event.banner_url)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            # Lưu ảnh mới
            filename = secure_filename(banner_file.filename)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(upload_dir, new_filename)
            banner_file.save(filepath)
            
            # Cập nhật DB
            event.banner_url = f"uploads/banners/{new_filename}"

        # Lưu thay đổi vào DB
        db.session.commit()
        flash('Cập nhật sự kiện thành công!', 'success')
        return redirect(url_for('main.manage_events'))

    # NẾU LÀ TRANG GET: Lấy danh sách thể loại để đổ ra form
    categories = Category.query.all()
    return render_template('edit_event.html', event=event, categories=categories)

# ========== [Xử lý tìm tất cả các sự kiện thuộc về Ban tổ chức đang đăng nhập] ================
@main_bp.route('/organizer/events')
def manage_events():
    # Kiểm tra quyền Organizer
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập!', 'error')
        return redirect(url_for('main.login'))
        
    current_user = User.query.get(session['user_id'])
    if not current_user or current_user.role != 'ORGANIZER':
        flash('Chỉ Ban tổ chức mới có quyền truy cập trang này!', 'error')
        return redirect(url_for('main.index'))

    # Lấy danh sách sự kiện do chính người này tạo, sắp xếp mới nhất lên đầu
    my_events = Event.query.filter_by(organizer_id=current_user.id).order_by(Event.id.desc()).all()
    
    return render_template('manage_events.html', events=my_events, now=datetime.now())

# ============================== [THỐNG KÊ NTC] ==============================
@main_bp.route('/organizer/dashboard')
def organizer_dashboard():
    # 1. Kiểm tra quyền truy cập
    if 'user_id' not in session or (session.get('role') != 'ORGANIZER' and session.get('user_role') != 'ORGANIZER'):
        flash('Vui lòng đăng nhập với tài khoản Ban tổ chức!', 'error')
        return redirect(url_for('main.login'))

    current_user_id = session['user_id']
    
    # 2. Lấy tất cả sự kiện của Nhà tổ chức này
    events = Event.query.filter_by(organizer_id=current_user_id).all()

    # 3. Khởi tạo các biến thống kê
    total_events = len(events)
    total_tickets_sold = 0
    total_revenue = 0

    # Dữ liệu dành cho biểu đồ (Chart.js)
    chart_labels = [] # Tên sự kiện
    chart_data = []   # Doanh thu của sự kiện đó

    for event in events:
        event_revenue = 0
        event_tickets_sold = 0
        
        # Quét qua các loại vé của sự kiện này để cộng dồn
        for tt in event.ticket_types:
            sold = tt.quantity_sold
            price = tt.price
            event_tickets_sold += sold
            event_revenue += (sold * price)

        # Cộng vào tổng hệ thống
        total_tickets_sold += event_tickets_sold
        total_revenue += event_revenue

        # Đẩy dữ liệu vào mảng vẽ biểu đồ
        chart_labels.append(event.title)
        chart_data.append(float(event_revenue))

    return render_template('dashboard.html',
                           total_events=total_events,
                           total_tickets_sold=total_tickets_sold,
                           total_revenue=total_revenue,
                           chart_labels=json.dumps(chart_labels), # Dùng json.dumps để JS đọc được an toàn
                           chart_data=json.dumps(chart_data))