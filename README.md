# Crawl
## File CrawlV2.py sẽ thu thập tiêu đề từ qua các gợi ý của google
1. Đầu tiên sẽ truyền từ khóa, chờ cho đến khi google hiện kết quả tìm kiếm.
2. Sau đó chương trình sẽ tìm đến phần chứa các gợi ý từ khóa đó, dùng click tự động vào gợi ý đầu tiên liên tục 20 lần (có thể thay đổi số lần click).
3. Sau khi đã click đủ thì chương trình sẽ lưu số gợi ý đã được sinh ra từ gợi ý đầu tiên.
4. Tiếp theo chương trình sẽ thu thập lần lượt tiêu đề, nội dung và đường dẫn tới thông tin đó.
5. Chương trình sẽ vừa thu thập vừa lưu dữ liệu vào file .csv để có thể biết được dữ liệu thu thập có được hay không.
6. Cuối cùng chương trình sẽ lưu lại tất cả dữ liệu đã thu thập vào 1 file csv.
## Code
0. Cài đặt python trên ubuntu:
```bash
sudo apt install python3
```
1. Clone Repo:
```bash
git clone https://github.com/HoangLinh03-code/Crawl
cd Crawl
```
2. Tải các thư viện cần thiết về:
```bash
pip install -r requirements.txt
```
3. Chạy CrawlV2.py:
```bash
python gui.py
```

