import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from CrawlV2 import web_driver, google_search, scrape_suggestions

class GoogleScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Cào Dữ Liệu Google")
        self.root.geometry("800x600")
        
        self.driver = None
        self.is_scraping = False
        self.scraping_event = threading.Event()
        self.create_gui()
        
    def create_gui(self):
        # Khung chính với padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Khung tìm kiếm
        search_frame = ttk.LabelFrame(main_frame, text="Cài Đặt Tìm Kiếm", padding="5")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(search_frame, text="Danh sách từ khóa (mỗi từ khóa một dòng):").grid(row=0, column=0, padx=5, pady=5)
        self.keyword_text = scrolledtext.ScrolledText(search_frame, height=5, width=40)
        self.keyword_text.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Số lần click ban đầu:").grid(row=1, column=0, padx=5, pady=5)
        self.clicks_entry = ttk.Entry(search_frame, width=10)
        self.clicks_entry.insert(0, "20")
        self.clicks_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Số lượng core (max_workers):").grid(row=2, column=0, padx=5, pady=5)
        self.workers_entry = ttk.Entry(search_frame, width=10)
        self.workers_entry.insert(0, "5")
        self.workers_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Thêm Checkbutton cho chế độ headless
        self.headless_var = tk.BooleanVar()
        self.headless_check = ttk.Checkbutton(search_frame, text="Chế độ không cửa sổ (headless)", variable=self.headless_var)
        self.headless_check.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=tk.W)
        
        # Nút điều khiển
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Bắt Đầu Cào", command=self.start_scraping)
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Dừng", command=self.stop_scraping, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # Khung tiến trình
        progress_frame = ttk.LabelFrame(main_frame, text="Tiến Trình", padding="5")
        progress_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate', variable=self.progress_var)
        self.progress_bar.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        self.status_label = ttk.Label(progress_frame, text="Đang chờ...", wraplength=700)
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Vùng nhật ký
        log_frame = ttk.LabelFrame(main_frame, text="Nhật Ký", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=15, width=70)
        self.log_area.grid(row=0, column=0, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Cấu hình grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def update_progress(self, value):
        """Cập nhật thanh tiến trình"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def update_status(self, message):
        """Cập nhật trạng thái hiện tại"""
        self.status_label.config(text=message)
        self.log_message(message)
        self.root.update_idletasks()
    
    def log_message(self, message):
        """Ghi log với timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.see(tk.END)
    
    def start_scraping(self):
        keywords = self.keyword_text.get("1.0", tk.END).strip().splitlines()
        if not keywords:
            messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất một từ khóa")
            return
        
        try:
            clicks = int(self.clicks_entry.get())
            if clicks <= 0:
                messagebox.showerror("Lỗi", "Số lần click phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số lần click hợp lệ")
            return
        
        try:
            max_workers = int(self.workers_entry.get())
            if max_workers <= 0:
                messagebox.showerror("Lỗi", "Số lượng core phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số lượng core hợp lệ")
            return
        
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.update_status("Đang khởi động...")
        
        self.scraping_event.clear()  # Đặt lại sự kiện để tiếp tục quá trình
        thread = threading.Thread(target=self.scraping_thread, args=(keywords, clicks, max_workers))
        thread.daemon = True
        thread.start()
    
    def scraping_thread(self, keywords, clicks, max_workers):
        try:
            self.update_status("Đang khởi động Chrome...")
            headless_mode = self.headless_var.get()  # Lấy giá trị chế độ headless
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(self.process_keyword, keyword, clicks, headless_mode) for keyword in keywords]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        self.log_message(f"Lỗi xử lý keyword: {e}")
            
            if self.is_scraping:
                final_message = f"Hoàn thành! Kết quả được lưu vào các file CSV riêng biệt."
                self.update_status(final_message)
                messagebox.showinfo("Thành công", final_message)
        except Exception as e:
            error_message = f"Lỗi: {str(e)}"
            self.update_status(error_message)
            messagebox.showerror("Lỗi", error_message)
        finally:
            self.is_scraping = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if not self.is_scraping:
                self.update_status("Đã dừng quá trình cào dữ liệu")
    
    def process_keyword(self, keyword, clicks, headless_mode):
        driver = web_driver(headless=headless_mode)
        try:
            if google_search(driver, keyword):
                total_results, total_suggestions = scrape_suggestions(
                    driver,
                    keyword,
                    clicks,
                    progress_callback=self.update_progress,
                    status_callback=self.update_status,
                    stop_event=self.scraping_event
                )
                if total_suggestions == 0:
                    self.log_message(f"Không tìm thấy suggestions cho {keyword}. Bỏ qua tạo file CSV.")
                else:
                    self.log_message(f"Đã thu thập {total_results} kết quả cho {keyword}.")
        finally:
            driver.quit()
    
    def stop_scraping(self):
        """Dừng quá trình cào dữ liệu"""
        self.is_scraping = False
        self.scraping_event.set()  # Đánh dấu sự kiện để dừng quá trình cào dữ liệu
        self.update_status("Đang dừng quá trình cào dữ liệu...")
        self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = GoogleScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()