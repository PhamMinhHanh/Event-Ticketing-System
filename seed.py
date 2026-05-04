from app import create_app, db
from app.models import Category, Event, TicketType, User, Organizer
from datetime import datetime, timedelta

# Khởi tạo app để lấy cấu hình kết nối CSDL
app = create_app()

with app.app_context():
    # Xóa toàn bộ bảng cũ và tạo lại bảng mới (Làm sạch Database)
    print("Đang làm sạch Database...")
    db.drop_all()
    db.create_all()

    print("Đang tạo dữ liệu mẫu (Mock Data)...")

    # Tạo một User là Nhà tổ chức
    org_user = User(full_name="Công ty Giải trí OUEvents", email="org@eventbox.com", phone="0999999999", role="ORGANIZER")
    org_user.set_password("123456")
    db.session.add(org_user)
    db.session.commit()

    org_profile = Organizer(user_id=org_user.id, name="OUEvents Official")
    db.session.add(org_profile)
    db.session.commit()

    # Tạo các Danh mục sự kiện
    cat_music = Category(name='Âm nhạc', description='Các buổi hòa nhạc, liveshow')
    cat_sport = Category(name='Thể thao', description='Các trận đấu thể thao, giải đấu')
    cat_workshop = Category(name='Hội thảo', description='Hội thảo chuyên đề, talkshow')
    cat_theater = Category(name='Sân khấu kịch', description='Các vở diễn sân khấu kịch, kịch')

    # Thêm vào phiên làm việc và lưu (commit) để CSDL cấp phát ID
    db.session.add_all([cat_music, cat_sport, cat_workshop, cat_theater])
    db.session.commit()

    # Tạo các Sự kiện
    # Dùng timedelta để ngày sự kiện luôn ở tương lai so với thời điểm chạy code
    event1 = Event(
        category_id=cat_music.id,
        title='Tan Tan Acoustic - DATE NIGHT',
        description='Một buổi tối với ánh đèn vàng, sân khấu acoustic nhỏ và những giai điệu quen thuộc trong không gian ấm áp.',
        location='Tan Tan Café Acoustic',
        province="TP.HCM",
        start_time=datetime.now() + timedelta(days=10),
        end_time=datetime.now() + timedelta(days=10, hours=3),
        banner_url='https://salt.tkbcdn.com/ts/ds/5d/bd/4c/7e7634e6feb267283819752d0bbb162e.png',
        base_price=140000,
        organizer_id=org_profile.user_id,
        sales_start_time=datetime.now(), 
        sales_end_time=Event.end_time, 
        checkin_method='QR'
    )

    event2 = Event(
        category_id=cat_sport.id,
        title='ĐUA XE GO-KART CITY PARK',
        description='Trải nghiệm Go Kart tại The Global City – Tốc độ đỉnh cao giữa lòng TP.HCM',
        location='THE GLOBAL CITY',
        province="TP.HCM",
        start_time=datetime.now() + timedelta(days=5),
        end_time=datetime.now() + timedelta(days=5, hours=2),
        banner_url='https://salt.tkbcdn.com/ts/ds/d7/e7/f7/44b4ab809ab3e945f80730175c343f31.jpg',
        base_price=100000,
        organizer_id=org_profile.user_id,
        sales_start_time=datetime.now(), 
        sales_end_time=Event.end_time, 
        checkin_method='QR'
    )

    event3 = Event(
        category_id=cat_theater.id,
        title='Anh Hùng Cờ Lau',
        description='Show Thực Cảnh “Anh Hùng Cờ Lau – Đinh Bộ Lĩnh” là vở diễn ngoài trời quy mô lớn tái hiện hành trình từ cậu bé chăn trâu phất cờ lau tập trận đến khi lên ngôi Hoàng đế, mở đầu triều đại Đại Cồ Việt — thời kỳ độc lập đầu tiên của dân tộc.',
        location='Sân Khấu Thuỷ Đình Phố Cổ Hoa Lư',
        province="Ninh Bình",
        start_time=datetime.now() + timedelta(days=15),
        end_time=datetime.now() + timedelta(days=15, hours=1),
        banner_url='https://salt.tkbcdn.com/ts/ds/4f/4d/31/6da02c3b396bc1b68fc3e487a9cb1fab.png',
        base_price=150000,
        organizer_id=org_profile.user_id,
        sales_start_time=datetime.now(), 
        sales_end_time=Event.end_time, 
        checkin_method='QR'
    )

    event4 = Event(
        category_id=cat_theater.id,
        title='Làng Vô Tặc',
        description='Vở kịch “Làng vô tặc” mang màu sắc hài dân gian, kể câu chuyện oan khuất, phơi bày nghịch lý quyền lực và bộ mặt thật của chức sắc thôn làng.',
        location='Nhà Hát Kịch IDECAF',
        start_time=datetime.now() + timedelta(days=7),
        end_time=datetime.now() + timedelta(days=7, hours=2),
        banner_url='https://salt.tkbcdn.com/ts/ds/db/d9/6b/7ef0f96eb6bc673df8fd0a7163f1a640.jpg',
        base_price=300000,
        organizer_id=org_profile.user_id,
        sales_start_time=datetime.now(), 
        sales_end_time=Event.end_time, 
        checkin_method='QR'
    )

    db.session.add_all([event1, event2, event3, event4])
    db.session.commit()

    # 4. Tạo các Loại vé cho từng sự kiện
    tickets = [
        # Vé cho sự kiện âm nhạc
        TicketType(event_id=event1.id, name='RIÊNG TƯ', price=160000, quantity_total=40, quantity_sold=10),
        TicketType(event_id=event1.id, name='LÃNG MẠN', price=150000, quantity_total=60, quantity_sold=30),
        TicketType(event_id=event1.id, name='HƯỚNG NỘI', price=140000, quantity_total=100, quantity_sold=60),

        # Vé cho sự kiện thể thao - ĐUA XE GO-KART CITY PARK
        TicketType(event_id=event2.id, name='Người lớn (13+)', price=150000, quantity_total=70, quantity_sold=30),
        TicketType(event_id=event2.id, name='Trẻ em (Dưới 13t)', price=100000, quantity_total=30, quantity_sold=10),

        # Vé cho sự kiện sân khấu kịch 01 - Anh Hùng Cờ Lau
        TicketType(event_id=event3.id, name='Vé người lớn (Trên 1m3)', price=250000, quantity_total=150, quantity_sold=100),
        TicketType(event_id=event3.id, name='Vé trẻ em (Dưới 1m3)', price=150000, quantity_total=50, quantity_sold=30),

        # Vé cho sự kiện sân khấu kịch 02 - Làng Vô Tặc
        TicketType(event_id=event4.id, name='Hạng VIP', price=350000, quantity_total=100, quantity_sold=50),
        TicketType(event_id=event4.id, name='Hạng Regular', price=300000, quantity_total=200, quantity_sold=150),
    ]

    db.session.add_all(tickets)
    db.session.commit()

    print("Tạo Mock Data thành công!")