import os
import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import logging
import json
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# def web_driver():
#     chrome_driver_path = '/home/hoanglinh/CrawlData/chromedriver-linux64/chromedriver'
#     chrome_binary_path = '/usr/bin/google-chrome'
    
#     if not os.path.exists(chrome_driver_path):
#         raise FileNotFoundError(f"Không tìm thấy đường dẫn {chrome_driver_path}")
#     if not os.access(chrome_driver_path, os.X_OK):
#         raise PermissionError(f"Không có quyền thực thi file tại {chrome_driver_path}")
#     if not os.path.exists(chrome_binary_path):
#         raise FileNotFoundError(f"Không tìm thấy đường dẫn {chrome_binary_path}")
#     if not os.access(chrome_binary_path, os.X_OK):
#         raise PermissionError(f"Không có quyền thực thi file tại {chrome_binary_path}")
    
#     service = ChromeService(chrome_driver_path)
#     options = Options()
#     options.binary_location = chrome_binary_path
#     options.add_argument('--disable-gpu')
#     options.add_argument('--disable-notifications')
#     options.add_argument('--no-sandbox')
#     options.add_argument('--disable-dev-shm-usage')
#     options.add_argument('--log-level=3')
#     options.add_argument('--disable-extensions')
    
#     try:
#         driver = webdriver.Chrome(service=service, options=options)
#         return driver
#     except Exception as e:
#         logger.error(f"Lỗi khởi tạo WebDriver: {e}")
#         raise

def web_driver():
    try:
        # Đọc cấu hình
        config_path = os.path.join(os.path.expanduser("~"), ".google_scraper", "config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        # Sử dụng WebDriverManager để tự động tải ChromeDriver
        driver_path = ChromeDriverManager().install()
        
        service = ChromeService(driver_path)
        options = Options()
        options.binary_location = config["chrome_binary_path"]
        
        # Các tùy chọn Chrome khác
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-extensions')

        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        raise Exception(f"Lỗi khởi tạo Chrome: {str(e)}")


def google_search(driver, keyword):
    try:
        url = "https://www.google.com/"
        driver.get(url)
        time.sleep(2)
        
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        return True
    except Exception as e:
        logger.error(f"Error during search: {e}")
        return False

def scrape_suggestions(driver, filename, initial_clicks=20, progress_callback=None, status_callback=None, stop_event=None):
    processed_titles = set()
    total_results = 0
    suggestions_count = 0
    
    try:
        if status_callback:
            status_callback("Phase 1: Đang tạo suggestions...")
            
        # Phase 1: Tạo suggestions
        for click_count in range(initial_clicks):
            if stop_event and stop_event.is_set():  # Kiểm tra nếu sự kiện dừng đã được kích hoạt
                if status_callback:
                    status_callback("Quá trình cào đã bị dừng.")
                break
            
            try:
                time.sleep(3)
                
                suggestions_container = driver.find_element(By.CLASS_NAME, "cUnQKe")
                first_suggestion = suggestions_container.find_element(By.CSS_SELECTOR, '[jsname="tJHJj"]')
                
                try:
                    title = first_suggestion.find_element(By.CLASS_NAME, "CSkcDe").text.strip()
                except:
                    title = "Không xác định"
                
                driver.execute_script("arguments[0].click();", first_suggestion)
                if status_callback:
                    status_callback(f"Click {click_count + 1}/{initial_clicks} - Đang mở")
                time.sleep(2)
                
                driver.execute_script("arguments[0].click();", first_suggestion)
                if status_callback:
                    status_callback(f"Click {click_count + 1}/{initial_clicks} - Đang đóng")
                time.sleep(2)
                
                # Cập nhật tiến trình phase 1
                if progress_callback:
                    progress = (click_count + 1) / (initial_clicks * 2) * 100  # Phase 1 chiếm 50% tiến trình
                    progress_callback(progress)
                
            except Exception as e:
                if status_callback:
                    status_callback(f"Lỗi click: {str(e)}")
                continue
        
        # Đếm suggestions
        time.sleep(3)
        suggestions_container = driver.find_element(By.CLASS_NAME, "cUnQKe")
        suggestion_divs = suggestions_container.find_elements(By.CSS_SELECTOR, '[jsname="yEVEwb"]')
        suggestions_count = len(suggestion_divs)
        
        if status_callback:
            status_callback(f"Đã tìm thấy {suggestions_count} suggestions")
            status_callback("Phase 2: Đang thu thập dữ liệu...")
        
        # Phase 2: Thu thập dữ liệu
        for index, div in enumerate(suggestion_divs):
            if stop_event and stop_event.is_set():  # Kiểm tra nếu sự kiện dừng đã được kích hoạt
                if status_callback:
                    status_callback("Quá trình cào đã bị dừng.")
                break
            
            try:
                title = div.find_element(By.CLASS_NAME, "CSkcDe").text.strip()
                if title in processed_titles:
                    continue
                
                div.click()
                time.sleep(5)
                
                content = ""
                link = ""
                
                try:
                    main_content = div.find_element(By.CLASS_NAME, "bCOlv")
                    content_element = main_content.find_element(By.CLASS_NAME, "hgKElc")
                    content = content_element.text.strip()
                except Exception as e:
                    if status_callback:
                        status_callback(f"Không tìm thấy nội dung cho: {title}")
                    
                try:
                    link_element = main_content.find_element(By.TAG_NAME, 'a')
                    link = link_element.get_attribute("href")
                except Exception as e:
                    if status_callback:
                        status_callback(f"Không tìm thấy link cho: {title}")
                
                result = {
                    "title": title,
                    "content": content,
                    "link": link
                }
                
                with open(filename, 'a', newline='', encoding='utf-8') as file:
                    writer = csv.DictWriter(file, fieldnames=["title", "content", "link"])
                    writer.writerow(result)
                
                total_results += 1
                processed_titles.add(title)
                
                if status_callback:
                    status_callback(f"Đã thu thập: {title}")
                
                # Cập nhật tiến trình phase 2
                if progress_callback:
                    base_progress = 50  # Phase 1 đã hoàn thành
                    phase2_progress = (index + 1) / suggestions_count * 50  # Phase 2 chiếm 50% còn lại
                    total_progress = base_progress + phase2_progress
                    progress_callback(total_progress)
                
            except Exception as e:
                if status_callback:
                    status_callback(f"Lỗi xử lý suggestion: {str(e)}")
                
    except Exception as e:
        if status_callback:
            status_callback(f"Lỗi: {str(e)}")
    
    return total_results, suggestions_count




# def save_result(result, filename="google_suggestions.csv", is_new=False):
#     try:
#         mode = 'w' if is_new else 'a'
#         with open(filename, mode, newline='', encoding='utf-8') as file:
#             writer = csv.DictWriter(file, fieldnames=["title","content","link"])
#             if is_new:
#                 writer.writeheader()
#             writer.writerow(result)
#         return True
#     except Exception as e:
#         logger.error(f"Error saving to CSV: {e}")
#         return False
# def scrape_suggestions(driver, filename="google_suggestions.csv", initial_clicks = 20):
#     processed_titles = set()
#     total_results = 0
#     suggestions_count = 0
    
#     # Tạo file mới
#     save_result({}, filename, is_new=True)
    
#     try:
#         # Phase 1: Click nhiều lần vào suggest đầu tiên
#         print(f"Phase 1: Tạo suggestions với {initial_clicks} lần click...")
#         for click_count in range(initial_clicks):
#             try:
#                 time.sleep(3)  # Đợi suggestions load
                
#                 # Tìm và click suggestion đầu tiên
#                 suggestions_container = driver.find_element(By.CLASS_NAME, "cUnQKe")
#                 first_suggestion = suggestions_container.find_element(By.CSS_SELECTOR, '[jsname="tJHJj"]')
                
#                 # Lấy tiêu đề trước khi click
#                 try:
#                     title = first_suggestion.find_element(By.CLASS_NAME, "CSkcDe").text.strip()
#                 except:
#                     title = "Unknown"
                
#                 # Dùng JavaScript để click
#                 driver.execute_script("arguments[0].click();", first_suggestion)
#                 print(f"Click {click_count + 1}/{initial_clicks} - Opening")
#                 time.sleep(2)
                
#                 driver.execute_script("arguments[0].click();", first_suggestion)
#                 print(f"Click {click_count + 1}/{initial_clicks} - Closing")
#                 time.sleep(2)
                
                
#             except Exception as e:
#                 print(f"Lỗi trong quá trình click ban đầu: {str(e)}")
#                 continue
        
#         # Đếm tổng số suggestions sau khi click
#         time.sleep(3)
#         suggestions_container = driver.find_element(By.CLASS_NAME, "cUnQKe")
#         suggestion_divs = suggestions_container.find_elements(By.CSS_SELECTOR, '[jsname="yEVEwb"]')
#         suggestions_count = len(suggestion_divs)
#         print(f"\nHoàn thành Phase 1. Tổng số suggestions: {suggestions_count}")
        
#         # Phase 2: Thu thập dữ liệu
#         print("\nPhase 2: Thu thập dữ liệu từ suggestions...")
        
#         for div in suggestion_divs:
#             try:
#                 # Thu thập và kiểm tra title
#                 title = div.find_element(By.CLASS_NAME, "CSkcDe").text.strip()
#                 if title in processed_titles:
#                     continue
                
#                 div.click()
#                 time.sleep(5)
                
#                 try:
#                     main_content = div.find_element(By.CLASS_NAME, "bCOlv")
#                 except Exception as e:
#                     print(f"Lỗi không tìm thấy nội dung chính: {str(e)}")
#                 content = ""
#                 link = ""
                
#                 try:
#                     content_element = main_content.find_element(By.CLASS_NAME, "hgKElc")
#                     content = content_element.text.strip()
#                 except:
#                     print(f"Không tìm thấy nội dung cho: {title}")
                    
#                 try:
#                     link_element = main_content.find_element(By.TAG_NAME, 'a')
#                     link = link_element.get_attribute("href")
#                 except:
#                     print(f"Không tìm thấy link cho: {title}")
                
#                 # Tạo và lưu kết quả
#                 result = {
#                     "title": title,
#                     "content": content,
#                     "link": link
#                 }
                
#                 if save_result(result, filename):
#                     total_results += 1
#                     processed_titles.add(title)
#                     print(f"\nĐã thu thập và lưu ({total_results}/{suggestions_count}):")
#                     print(f"Tiêu đề: {title}")
#                     print(f"Nội dung: {content[:100]}..." if content else "Nội dung: Không có")
#                     print(f"Link: {link}" if link else "Link: Không có")
#                     print("-" * 50)
#                 else:
#                     print(f"Lỗi khi lưu kết quả cho: {title}")
#             except Exception as e:
#                 print(f"Lỗi khi xử lý suggestion: {str(e)}")
                
#     except Exception as e:
#         logger.error(f"Lỗi khi scraping: {e}")
    
#     return total_results, suggestions_count



# # def main():
# #     keyword = input("Nhập từ khóa tìm kiếm: ")
# #     filename = "google_suggestions.csv"
# #     driver = None
    
# #     try:
# #         print("Đang khởi động trình duyệt...")
# #         driver = web_driver()
# #         print("Đang tìm kiếm...")
        
# #         if google_search(driver, keyword):
# #             print("Bắt đầu thu thập dữ liệu...")
# #             total_results = scrape_suggestions(driver, filename)
# #             print(f"\nHoàn thành! Đã thu thập và lưu {total_results} kết quả vào {filename}")
# #     except Exception as e:
# #         print(f"Lỗi: {e}")
# #     finally:
# #         if driver:
# #             driver.quit()

# # if __name__ == "__main__":
# #     main()

