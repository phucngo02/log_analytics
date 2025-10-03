# Log Analytics

## 📌 Giới thiệu

Dự án **Log Analytics** là một công cụ phân tích và giám sát nhật ký hệ thống, được xây dựng bằng Python và Docker. Mục tiêu của dự án là cung cấp một giải pháp đơn giản và hiệu quả để thu thập, lưu trữ và phân tích dữ liệu nhật ký từ các nguồn khác nhau, hỗ trợ việc giám sát và phát hiện sự cố trong hệ thống.

## ⚙️ Các thành phần chính

- **Collectors**: Các mô-đun chịu trách nhiệm thu thập dữ liệu từ các nguồn khác nhau.
- **streamlitDB**: Giao diện người dùng được xây dựng bằng Streamlit để hiển thị và tương tác với dữ liệu nhật ký.
- **Docker**: Sử dụng Docker để đóng gói và triển khai ứng dụng một cách dễ dàng và nhất quán.

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

📄 Tệp tin quan trọng

docker-compose.yml: Cấu hình Docker Compose cho các dịch vụ.

init_db.py: Script khởi tạo cơ sở dữ liệu.

streamlitDB: Giao diện người dùng được xây dựng bằng Streamlit.

test_abuseipdb.py: Bài kiểm thử cho mô-đun AbuseIPDB.
