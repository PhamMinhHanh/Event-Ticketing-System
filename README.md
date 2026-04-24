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
- [x] **Duyệt và tìm kiếm sự kiện:** Lọc sự kiện theo danh mục, tìm kiếm theo từ khóa.
- [x] **Xem chi tiết sự kiện:** Hiển thị thông tin mô tả, thời gian, địa điểm.
- [x] **Khám phá loại vé:** Tích hợp bộ đếm hiển thị số lượng vé còn lại và giá vé.

### Cột mốc tiếp theo (Các tính năng sắp phát triển)
- [ ] **Thanh toán online & Hoàn tiền:** Tích hợp Payment Gateway.
- [ ] **Tạo và quản lý sự kiện:** Thống kê doanh thu, cấu hình vé.
- [ ] **Quét vé Check-in:** Hỗ trợ QR Code và nhận diện khuôn mặt (FaceID).
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
│   ├── __init__.py       # Khởi tạo Flask app & kết nối DB
│   ├── models.py         # Định nghĩa cấu trúc các bảng CSDL (Entities)
│   ├── routes.py         # Xử lý logic điều hướng và gọi Controller
│   └── templates/        # Giao diện HTML (Jinja2)
│       ├── index.html
│       ├── login.html
│       └── event_detail.html
│
├── .venv/                # Môi trường ảo (Đã được gitignore)
├── config.py             # Cấu hình hệ thống & Database
├── requirements.txt      # Danh sách thư viện cần thiết
├── run.py                # File khởi chạy ứng dụng chính
└── seed.py               # Script tự động tạo dữ liệu mẫu (Mock Data)
```
