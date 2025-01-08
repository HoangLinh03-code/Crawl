# Crawl
## File CrawlTitle.py sẽ thu thập tiêu đề từ qua các gợi ý của google
1. Đầu tiên sẽ truyền từ khóa, chờ cho đến khi google hiện kết quả tìm kiếm.
2. Sau đó chương trình sẽ tìm đến phần chứa các gợi ý, dùng click tự động để hiện ra thêm gợi ý mới đồng thời thu thập thập các tiêu đề sau đó, tiếp tục như vậy cho đến khi đủ dữ liệu thì dừng.
## File CrawlContent sẽ thu thập nội dung và link từ các từ khóa đã thu thập trước đó
1. Truyền vào các từ khóa tiêu đề tìm kiếm đã được thu thập vào file gg_sugg.csv trước đó, chờ gg hiển thị kết quả.
2. Sau đó sẽ lấy nội dùng và link đầu tiên từ từ khóa đó, nếu không lấy được nội dung thì có thể lấy đường dẫn.
3. Sử dụng multithread để chạy nhiều gg chrome cùng một lúc và lưu dữ liệu vào csv song song với việc chạy tiến trình thu thập dữ liệu.
