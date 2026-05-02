# Project Event-Ticketing-System
# EventBox - Hệ thống Bán vé Sự kiện Trực tuyến 🎟️

**EventBox** là nền tảng trực tuyến cho phép các nhà tổ chức sự kiện đăng tải và bán vé cho các chương trình của họ (hòa nhạc, hội thảo, thể thao,...). Người dùng có thể dễ dàng tìm kiếm, mua vé và nhận vé điện tử một cách tiện lợi. 

*Dự án thuộc Bài tập lớn môn học **Quản lý dự án phần mềm** - GVHD: **Ths Nguyễn Trung Hậu**.*

---

## 👥 Đội ngũ phát triển (Nhóm 7)
* **Thành viên 1:** Phạm Minh Hạnh - 2151053015
* **Thành viên 2:** Phan Văn Hào - 2151010090
* **Thành viên 3:** Lê Mạnh Cường - 2051052014

---

## 🚀 Tiến trình làm việc
Dự án được phát triển theo từng giai đoạn (Milestones).

### Cột mốc hiện tại
- [x] **Duyệt và tìm kiếm sự kiện:** Lọc sự kiện theo danh mục, địa điểm, tìm kiếm theo từ khóa.
- [x] **Xem chi tiết sự kiện:** Hiển thị thông tin mô tả, thời gian, địa điểm, ...
- [x] **Khám phá loại vé:** Tích hợp bộ đếm hiển thị số lượng vé còn lại và giá vé.
- [x] **Quét vé Check-in (Mã QR):** Quét QR Code.
- [x] **Thanh toán online VNPay:** Tích hợp Payment Gateway.
- [x] **Tạo sự kiện:** Tạo mới sự kiện.

### Cột mốc tiếp theo (Các tính năng sắp và đang phát triển)
- [ ] **Hoàn tiền:** Tích hợp Payment Gateway.
- [ ] **Quản lý sự kiện:** Sửa sự kiện, Thống kê doanh thu, cấu hình vé.
- [ ] **Quét vé Check-in (Face ID):** Quét nhận diện khuôn mặt.
- [ ] **Gợi ý sự kiện:** Đề xuất cá nhân hóa dựa trên lịch sử tương tác.
- [ ] **Dynamic Pricing:** Điều chỉnh giá vé tự động theo nhu cầu.

---

## 🛠️ Công nghệ sử dụng
* **Backend:** Python, Flask framework.
* **Database:** MySQL, SQLAlchemy (ORM), PyMySQL.
* **Frontend:** HTML5, CSS3, Jinja2 Template, Bootstrap 5 (UI/UX).
* **Quản lý dự án:** GitHub, Trello/Jira (Task tracking).

---

## ⚙️ Hướng dẫn Cài đặt & Chạy dự án (Local Development)

Yêu cầu máy tính đã cài đặt sẵn **Python (>=3.8)** và **MySQL Server**.

### Bước 1: Clone source code
```bash
git clone https://github.com/PhamMinhHanh/Event-Ticketing-System.git
```
```bash
cd Event-Ticketing-System
```

### Bước 2: Thiết lập môi trường ảo (Virtual Environment)
#### Tạo môi trường ảo
```bash
python -m venv .venv
```
#### Kích hoạt (Windows)
```bash
.venv\Scripts\activate
```

### Bước 3: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 4: Thiết lập Cơ sở dữ liệu
#### Tạo db trên SQL
Mở MySQL, tạo một database trống có tên event_ticketing:
```bash
CREATE DATABASE event_ticketing;
```
#### Chỉnh thông tin kết nối tới MySQL
Mở file config.py và điều chỉnh chuỗi kết nối (URI) cho khớp với user/password MySQL trên máy cá nhân:

```bash
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://<user_cua_ban>:<password_cua_ban>@lo
```

### Bước 5: Nạp dữ liệu mẫu (Mock Data)
Để có sẵn dữ liệu các danh mục, sự kiện và loại vé để test, chạy script sau:

```bash
python seed.py
```
(Nếu Terminal báo "Tạo Mock Data thành công!" là bạn đã làm đúng).


### Bước 6: Khởi chạy Server
```bash
python run.py
```
Mở trình duyệt: http://127.0.0.1:5000

## 📂 Cấu trúc thư mục chính
```text
Event-Ticketing-System/
│
├── app/
│   ├── __init__.py           # Khởi tạo Flask app & kết nối Cơ sở dữ liệu
│   ├── models.py             # Định nghĩa cấu trúc các bảng (User, Event, Ticket, Checkin...)
│   ├── routes.py             # Xử lý logic điều hướng, API và Thanh toán VNPAY
│   │
│   ├── static/               # Thư mục chứa các tệp tĩnh (CSS, JS, Hình ảnh)
│   │   └── uploads/
│   │       └── banners/      # Nơi lưu trữ ảnh bìa sự kiện do Organizer tải lên
│   │
│   └── templates/            # Giao diện HTML (Sử dụng cú pháp Jinja2)
│       ├── base.html             # Layout gốc (Chứa Navbar, Footer dùng chung)
│       ├── index.html            # Trang chủ & Tìm kiếm sự kiện
│       ├── login.html            # Trang đăng nhập
│       ├── register.html         # Trang đăng ký tài khoản
│       ├── event_detail.html     # Trang chi tiết sự kiện & Chọn vé
│       ├── checkout.html         # Trang xác nhận đơn hàng & Chuyển hướng VNPAY
│       ├── my_tickets.html       # Trang "Vé của tôi" (Hiển thị mã QR cho người mua)
│       ├── create_event.html     # Form tạo sự kiện mới (Dành cho Organizer)
│       ├── manage_events.html    # Bảng quản lý sự kiện (Dành cho Organizer)
│       └── checkin_scanner.html  # Màn hình mở Camera quét mã QR (Dành cho Organizer)
│
├── .venv/                    # Môi trường ảo chứa thư viện Python (Đã Gitignore)
├── config.py                 # Cấu hình hệ thống, Database, và API Key VNPAY
├── requirements.txt          # Danh sách thư viện (Flask, SQLAlchemy, PyMySQL...)
├── run.py                    # File khởi chạy ứng dụng web chính
└── seed.py                   # Script tự động làm sạch DB và tạo dữ liệu mẫu
```
