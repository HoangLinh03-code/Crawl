# Cách chương trình hoạt động:
**CrawV2.py**
- File này sẽ thực hiện phần thu thập dữ liệu
- Khi người dùng nhập 1 hoặc nhiều từ khóa cùng lúc vào tìm kiếm trên google, google sẽ trả về kết quả dựa theo từ khóa đó.
- Tiếp theo, chương trình sẽ tìm đến phần 'Mọi người cũng hỏi' để thu thập dữ liệu, nếu không tìm được sẽ dừng tìm kiếm.
- Chương trình sẽ chỉ bấm vào phần gợi ý đầu tiên trong 'Mọi người cũng hỏi' chỉ tạo ra gợi ý giống với từ khóa hoặc gợi ý đầu tiên.
- Sau khi đã thực hiện click, chương trình sẽ thu thập dữ liệu từ các gợi ý đã được gg tạo ra, sau đó đưa vào file excel.
- Kết thúc chương trình.

**Main.py**
- Phần giao diện người dùng gồm:
    + Thanh công cụ nhập 1 hoặc nhiều từ khóa
    + Thanh điều chỉnh số lần click
    + Thanh điều chỉnh số cửa số gg có thể mở
    + Nút để bật mở cửa sổ khi cào hoặc tắt đi để giảm các cửa sổ chạy cùng lúc.
    + Nút cào và dừng
    + Phần console chứa thông tin quá trình thu thập dữ liệu.
# Cách chạy chương trình:
1. Clone git hub
```bash
git clone https://github.com/HoangLinh03-code/Crawl
cd Crawl
```
2. Chạy chương trình
```bash
python main.py
```
Nếu sử dụng python3
```bash
python3 main.py
```
3. Build app dành cho các hệ điều hành khác nhau:
- Phần này sẽ xây một app dành cho linux, macos, windows
- Có thể tùy chỉnh (Riêng về macos sẽ không thể sử dụng cách này)
```bash
python build_all.py
```
4. Build cho macos:
- Tạo repo riêng, upcode lên github.
- Tạo folder ./github/workflows/
- Tạo file build_mac.yml trong folder đó
- Sau khi build sẽ có file tar.gz, tải và giải nén để sử dụng trên mac
```bash
name: Build macOS App

on:
  push:
    branches:
      - main  # Kích hoạt workflow khi push lên nhánh main

jobs:
  build:
    runs-on: macos-latest  # Sử dụng môi trường macOS mới nhất

    steps:
      # Bước 1: Checkout code từ repository
      - name: Checkout code
        uses: actions/checkout@v2

      # Bước 2: Cài đặt Python
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'  # Chọn phiên bản Python phù hợp

      # Bước 3: Cài đặt các dependencies
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller selenium pillow
        

      # Bước 4: Build ứng dụng macOS
      - name: Build macOS app
        run: |
          python build.py

      # Bước 5: Tải file .app dưới dạng artifact
      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: GoogleScraper-macos
          path: dist/release/macos/
```
