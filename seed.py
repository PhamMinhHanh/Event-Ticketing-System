from app import create_app, db
from app.models import Category, Event, TicketType, User, Organizer
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("Đang làm sạch Database...")
    db.drop_all()
    db.create_all()

    print("Đang tạo dữ liệu mẫu (Mock Data)...")
    now = datetime.now()

    # ==========================================
    # 1. TẠO TÀI KHOẢN (USERS & ORGANIZERS)
    # ==========================================
    org1 = User(full_name="Công ty cổ phần tập đoàn Yeah1", email="yeah1@gmail.com", phone="0281231111", role="ORGANIZER")
    org1.set_password("123")
    db.session.add(org1)
    
    org2 = User(full_name="Những thành phố mơ màng", email="ntpmm@gmail.com", phone="0281232222", role="ORGANIZER")
    org2.set_password("123")
    db.session.add(org2)
    
    guest1 = User(full_name="Guest 01", email="guest01@gmail.com", phone="0901231111", role="USER")
    guest1.set_password("123")
    db.session.add(guest1)
    
    guest2 = User(full_name="Guest 02", email="guest02@gmail.com", phone="0901232222", role="USER")
    guest2.set_password("123")
    db.session.add(guest2)

    db.session.commit()

    org_profile1 = Organizer(user_id=org1.id, name="Yeah1 Entertainment")
    org_profile2 = Organizer(user_id=org2.id, name="NTPMM Official")
    db.session.add_all([org_profile1, org_profile2])
    db.session.commit()

    # ==========================================
    # 2. TẠO DANH MỤC SỰ KIỆN
    # ==========================================
    cat_music = Category(name='Âm nhạc', description='Các buổi hòa nhạc, liveshow')
    cat_sport = Category(name='Thể thao', description='Các trận đấu thể thao, giải đấu')
    cat_theater = Category(name='Sân khấu kịch', description='Các vở diễn sân khấu kịch, kịch')
    
    # Các danh mục mới
    cat_exhibition = Category(name='Triển lãm', description='Trưng bày nghệ thuật, bảo tàng')
    cat_workshop = Category(name='Workshop', description='Lớp học kỹ năng, thủ công')
    cat_experience = Category(name='Trải nghiệm', description='Tour tham quan, hoạt động văn hóa')
    cat_other = Category(name='Khác', description='Các sự kiện giải trí tổng hợp khác')

    db.session.add_all([cat_music, cat_sport, cat_theater, cat_exhibition, cat_workshop, cat_experience, cat_other])
    db.session.commit()

    # ==========================================
    # 3. TẠO SỰ KIỆN
    # ==========================================
    event1 = Event(
        category_id=cat_music.id, title='Tan Tan Acoustic - DATE NIGHT',
        description='Một buổi tối với ánh đèn vàng, sân khấu acoustic nhỏ...',
        location='Tan Tan Café Acoustic', province="TP.HCM",
        start_time=now + timedelta(days=10), end_time=now + timedelta(days=10, hours=3),
        banner_url='https://salt.tkbcdn.com/ts/ds/5d/bd/4c/7e7634e6feb267283819752d0bbb162e.png',
        base_price=140000, organizer_id=org1.id,
        sales_start_time=now - timedelta(days=1), sales_end_time=now + timedelta(days=9), 
        checkin_method='QR', status='PUBLISHED'
    )

    event2 = Event(
        category_id=cat_sport.id, title='ĐUA XE GO-KART CITY PARK',
        description='Trải nghiệm Go Kart tại The Global City – Tốc độ đỉnh cao giữa lòng TP.HCM',
        location='THE GLOBAL CITY', province="TP.HCM",
        start_time=now + timedelta(days=15), end_time=now + timedelta(days=15, hours=2),
        banner_url='https://salt.tkbcdn.com/ts/ds/d7/e7/f7/44b4ab809ab3e945f80730175c343f31.jpg',
        base_price=100000, organizer_id=org2.id,
        sales_start_time=now + timedelta(days=3), sales_end_time=now + timedelta(days=14), 
        checkin_method='QR', status='PUBLISHED'
    )

    event3 = Event(
        category_id=cat_theater.id, title='Anh Hùng Cờ Lau',
        description='Show Thực Cảnh “Anh Hùng Cờ Lau – Đinh Bộ Lĩnh” tái hiện hành trình Đinh Bộ Lĩnh...',
        location='Sân Khấu Thuỷ Đình Phố Cổ Hoa Lư', province="Ninh Bình",
        start_time=now - timedelta(hours=2), end_time=now + timedelta(hours=1),
        banner_url='https://salt.tkbcdn.com/ts/ds/4f/4d/31/6da02c3b396bc1b68fc3e487a9cb1fab.png',
        base_price=150000, organizer_id=org1.id,
        sales_start_time=now - timedelta(days=15), sales_end_time=now - timedelta(days=1), 
        checkin_method='QR', status='PUBLISHED'
    )

    event4 = Event(
        category_id=cat_theater.id, title='Làng Vô Tặc',
        description='Vở kịch “Làng vô tặc” mang màu sắc hài dân gian...',
        location='Nhà Hát Kịch IDECAF', province="TP.HCM",
        start_time=now + timedelta(days=7), end_time=now + timedelta(days=7, hours=2),
        banner_url='https://salt.tkbcdn.com/ts/ds/db/d9/6b/7ef0f96eb6bc673df8fd0a7163f1a640.jpg',
        base_price=300000, organizer_id=org2.id,
        sales_start_time=now - timedelta(days=2), sales_end_time=now + timedelta(days=6), 
        checkin_method='QR', status='CANCELLED'
    )

    # ---> SỰ KIỆN: VIVIAN VU'S HANDMADE CANDLES <---
    event5 = Event(
        category_id=cat_workshop.id,
        title='VIVIAN VU’S HANDMADE CANDLES',
        description='WORKSHOP LÀM NẾN & SÁP THƠM HANDMADE\nKhông chỉ là một buổi workshop mà là một trải nghiệm đáng nhớ\nGiữa guồng quay bận rộn, có khi nào bạn tự hỏi: Lần cuối mình dành 90 phút chỉ cho bản thân là khi nào?\nWorkshop làm Nến & Sáp thơm của Vivian Vu’s Candles không đơn thuần là một lớp học thủ công. Đây là khoảng thời gian để bạn thả lỏng tâm trí, chạm vào mùi hương mình yêu thích và tự tay tạo nên những điều xinh đẹp mang dấu ấn cá nhân.',
        location='CDC Building 25 Lê Đại Hành, Hai Bà Trưng',
        province="Hà Nội",
        start_time=now + timedelta(days=4), 
        end_time=now + timedelta(days=4, hours=2),
        banner_url='https://salt.tkbcdn.com/ts/ds/33/1e/58/b379fb2dd015f334432d11370da5bb46.jpg',
        base_price=315000,
        organizer_id=org2.id,
        sales_start_time=now - timedelta(days=3), 
        sales_end_time=now + timedelta(days=3), 
        checkin_method='FACE', # Quét khuôn mặt
        status='PUBLISHED'
    )

    # ---> SỰ KIỆN: TOUR ĐÊM VĂN MIẾU <---
    event6 = Event(
        category_id=cat_experience.id,
        title='TOUR ĐÊM VĂN MIẾU - VAN MIEU NIGHT TOUR',
        description='Tham quan Văn Miếu Đêm\nMột không gian vừa mộc mạc, vừa quen thuộc nhưng lại ấn tượng về đêm với sắc thái ngàn năm văn hiến. Nhấn mạnh vào hành trình học, trở thành những bậc kỳ tài của đất nước, không gian Văn Miếu - Quốc Tử Giám về đêm được tái hiện toàn cảnh một môi trường đơn sơ về học tập thời xưa... Đến với tour đêm Văn Miếu, bạn sẽ có cái nhìn toàn cảnh về nền quốc học Việt Nam.',
        location='Văn Miếu - Quốc Tử Giám, 58 Quốc Tử Giám',
        province="Hà Nội",
        start_time=now + timedelta(days=6),
        end_time=now + timedelta(days=6, hours=3),
        banner_url='https://salt.tkbcdn.com/ts/ds/47/19/34/ab4d5359e79aa5204c3a8376f0c96747.png',
        base_price=0,
        organizer_id=org1.id,
        sales_start_time=now - timedelta(days=5),
        sales_end_time=now + timedelta(days=5),
        checkin_method='QR',
        status='PUBLISHED'
    )

    db.session.add_all([event1, event2, event3, event4, event5, event6])
    db.session.commit()

    # ==========================================
    # 4. TẠO CÁC LOẠI VÉ
    # ==========================================
    tickets = [
        TicketType(event_id=event1.id, name='RIÊNG TƯ', price=160000, quantity_total=40, quantity_sold=10),
        TicketType(event_id=event1.id, name='LÃNG MẠN', price=150000, quantity_total=60, quantity_sold=30),
        TicketType(event_id=event1.id, name='HƯỚNG NỘI', price=140000, quantity_total=100, quantity_sold=60),

        TicketType(event_id=event2.id, name='Người lớn (13+)', price=150000, quantity_total=70, quantity_sold=0),
        TicketType(event_id=event2.id, name='Trẻ em (Dưới 13t)', price=100000, quantity_total=30, quantity_sold=0),

        TicketType(event_id=event3.id, name='Vé người lớn', price=250000, quantity_total=150, quantity_sold=150),
        TicketType(event_id=event3.id, name='Vé trẻ em', price=150000, quantity_total=50, quantity_sold=50),

        TicketType(event_id=event4.id, name='Hạng VIP', price=350000, quantity_total=100, quantity_sold=20),
        TicketType(event_id=event4.id, name='Hạng Regular', price=300000, quantity_total=200, quantity_sold=80),

        # ---> Vé cho EVENT 5 (Workshop Nến) <---
        TicketType(event_id=event5.id, name='VÉ ĐƠN', price=315000, quantity_total=40, quantity_sold=15),
        TicketType(event_id=event5.id, name='VÉ ĐÔI', price=599000, quantity_total=60, quantity_sold=20),

        # ---> Vé cho EVENT 6 (Văn Miếu) <---
        TicketType(event_id=event6.id, name='Trẻ em dưới 1m', price=0, quantity_total=50, quantity_sold=5),
        TicketType(event_id=event6.id, name='Sử đá lưu danh', price=199000, quantity_total=100, quantity_sold=35),
        TicketType(event_id=event6.id, name='Tinh hoa đạo học', price=299000, quantity_total=50, quantity_sold=10),
    ]

    db.session.add_all(tickets)
    db.session.commit()

    print("========================================")
    print("Tạo Mock Data thành công!")
    print("========================================")