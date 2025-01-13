import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
from datetime import datetime
import os
from CrawlV2 import web_driver, google_search, scrape_suggestions
import csv

class GoogleScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Công Cụ Cào Dữ Liệu Google")
        self.root.geometry("800x600")
        
        self.driver = None
        self.is_scraping = False
        self.current_file = None
        self.scraping_event = threading.Event()
        self.create_gui()
        
    def create_gui(self):
        # Khung chính với padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Khung tìm kiếm
        search_frame = ttk.LabelFrame(main_frame, text="Cài Đặt Tìm Kiếm", padding="5")
        search_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(search_frame, text="Từ khóa tìm kiếm:").grid(row=0, column=0, padx=5, pady=5)
        self.keyword_entry = ttk.Entry(search_frame, width=40)
        self.keyword_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Số lần click ban đầu:").grid(row=1, column=0, padx=5, pady=5)
        self.clicks_entry = ttk.Entry(search_frame, width=10)
        self.clicks_entry.insert(0, "20")
        self.clicks_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
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
    
    def create_or_check_file(self, filename):
        """Tạo file mới hoặc kiểm tra file đã tồn tại"""
        if not os.path.exists(filename):
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["title", "content", "link"])
                writer.writeheader()
            self.log_message(f"Đã tạo file mới: {filename}")
        else:
            self.log_message(f"File đã tồn tại: {filename}")
    
    def start_scraping(self):
        if not self.keyword_entry.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập từ khóa tìm kiếm")
            return
        
        try:
            clicks = int(self.clicks_entry.get())
            if clicks <= 0:
                messagebox.showerror("Lỗi", "Số lần click phải lớn hơn 0")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số lần click hợp lệ")
            return
        
        self.current_file = f"google_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.create_or_check_file(self.current_file)
        
        self.is_scraping = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.update_status("Đang khởi động...")
        
        self.scraping_event.clear()  # Đặt lại sự kiện để tiếp tục quá trình
        thread = threading.Thread(target=self.scraping_thread)
        thread.daemon = True
        thread.start()
    
    def scraping_thread(self):
        try:
            self.update_status("Đang khởi động Chrome...")
            self.driver = web_driver()
            
            self.update_status("Đang thực hiện tìm kiếm...")
            if google_search(self.driver, self.keyword_entry.get()):
                self.update_status("Bắt đầu thu thập dữ liệu...")
                total_results, total_suggestions = scrape_suggestions(
                    self.driver, 
                    self.current_file, 
                    int(self.clicks_entry.get()),
                    progress_callback=self.update_progress,
                    status_callback=self.update_status,
                    stop_event=self.scraping_event  # Truyền event để dừng quá trình
                )
                
                if self.is_scraping:
                    final_message = f"Hoàn thành! Đã thu thập {total_results}/{total_suggestions} kết quả"
                    self.update_status(final_message)
                    messagebox.showinfo(
                        "Thành công", 
                        f"{final_message}\nKết quả được lưu vào {self.current_file}"
                    )
            else:
                self.update_status("Không thể thực hiện tìm kiếm Google")
                messagebox.showerror("Lỗi", "Không thể thực hiện tìm kiếm Google")
        except Exception as e:
            error_message = f"Lỗi: {str(e)}"
            self.update_status(error_message)
            messagebox.showerror("Lỗi", error_message)
        finally:
            if self.driver:
                self.driver.quit()
            self.is_scraping = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if not self.is_scraping:  # Nếu dừng thủ công
                self.update_status("Đã dừng quá trình cào dữ liệu")
    
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