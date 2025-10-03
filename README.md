# Log Analytics

## 📌 Giới thiệu

Log Analytics là một công cụ giám sát và phân tích nhật ký hệ thống được xây dựng bằng Python và Docker.
Mục tiêu của dự án là thu thập, lưu trữ, phân tích dữ liệu log từ nhiều nguồn khác nhau, đồng thời hỗ trợ giám sát, phát hiện và cảnh báo sự cố trong hệ thống.

## ⚙️ Các thành phần chính

- **Collectors**:
Chịu trách nhiệm thu thập dữ liệu log từ các nguồn khác nhau.
Ví dụ: hệ thống nội bộ, log request HTTP, kiểm tra IP với AbuseIPDB.
- **streamlitDB**:
Giao diện người dùng trực quan để hiển thị và tương tác với dữ liệu log.
Cho phép xem log theo thời gian, loại log, trạng thái cảnh báo, v.v.
- **Alert System**:
Gửi cảnh báo Slack hoặc Email khi phát hiện log bất thường.
Ngưỡng cảnh báo có thể tuỳ chỉnh qua biến môi trường.
- **Database**:
Lưu trữ dữ liệu log và trạng thái alert.
Mặc định dùng SQLite (logs.db) với các table: logs, alerts.
- **Docker & Docker Compose**:
Đóng gói toàn bộ ứng dụng, dễ triển khai trên mọi môi trường.

## 🚀 Hướng dẫn cài đặt

### Yêu cầu hệ thống

- Python 3.8 trở lên
- Docker và Docker Compose

### Cài đặt bằng Docker Compose

1. Clone repository này về máy của bạn:

   ```bash
   git clone https://github.com/phucngo02/log_analytics.git
   cd log_analytics
2. Cài đặt các phụ thuộc:

   ```bash
   pip install -r requirements.txt
3. Khởi tạo cơ sở dữ liệu:

   ```bash
   python init_db.py


4. Chạy ứng dụng:
 
   ```bash
   streamlit run streamlitDB


Truy cập giao diện người dùng tại http://localhost:8501.

🧪 Kiểm thử

Để chạy các bài kiểm thử:
   ```bash
   pytest

```
📄 Tệp tin quan trọng

docker-compose.yml : cấu hình Docker Compose.

init_db.py : script khởi tạo cơ sở dữ liệu.

streamlitDB : giao diện Streamlit.

collectors/ : các collector thu thập log.

alerts.py : logic gửi cảnh báo Slack/Email.

test_abuseipdb.py : kiểm thử module AbuseIPDB.

⚙️ Biến môi trường

Cấu hình alert và DB:
- Email

ALERT_EMAIL_SMTP=<smtp_server>

ALERT_EMAIL_USER=<email_user>

ALERT_EMAIL_PASS=<email_pass>

- Database

DB_PATH=logs.db

- Alert thresholds

ALERT_THRESHOLD=3

💡 Ghi chú

Bạn có thể thêm collector mới vào thư mục collectors/.

Mọi log mới sẽ tự động cập nhật lên dashboard và trigger alert nếu vượt ngưỡng.

Docker giúp triển khai nhanh mà không cần cài Python hay các package.

