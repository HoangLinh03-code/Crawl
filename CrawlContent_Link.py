# import os
# import time
# import csv
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# def web_driver():
#     chrome_driver_path = '/home/hoanglinh/CrawlData/chromedriver-linux64/chromedriver'
#     chrome_binary_path = '/usr/bin/google-chrome'
    
#     service = ChromeService(chrome_driver_path)
#     options = Options()
#     options.binary_location = chrome_binary_path
#     options.add_argument('--headless')  # Uncomment nếu muốn chạy không giao diện
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
#         logger.error(f"Error initializing the WebDriver: {e}")
#         raise

# def google_search(driver, keyword):
#     try:
#         url = "https://www.google.com/"
#         driver.get(url)
#         time.sleep(2)
        
#         search_box = driver.find_element(By.NAME, "q")
#         search_box.clear()
#         search_box.send_keys(keyword)
#         search_box.send_keys(Keys.RETURN)
#         time.sleep(3)
#         return True
#     except Exception as e:
#         logger.error(f"Error during search: {e}")
#         return False

# def scrape_first_result(driver, keyword):
#     try:
#         # Lấy kết quả đầu tiên
#         first_result = driver.find_element(By.CLASS_NAME, 'V3FYCf')  # CLASS_NAME của kết quả tìm kiếm
#         content = first_result.find_element(By.CLASS_NAME, 'hgKElc').text.strip()  # Lấy nội dung mô tả
#         link = first_result.find_element(By.TAG_NAME, 'a').get_attribute('href')  # Lấy link
        
#         return {"keyword": keyword, "content": content, "link": link}
#     except Exception as e:
#         logger.warning(f"Could not fetch content, only getting link: {e}")
#         try:
#             link = first_result.find_element(By.CSS_SELECTOR, 'div.yuRUbf a').get_attribute('href')
#             return {"keyword": keyword, "content": None, "link": link}
#         except Exception as e:
#             logger.error(f"Could not fetch link: {e}")
#             return {"keyword": keyword, "content": None, "link": None}

# def save_to_csv(data, filename="google_results.csv", is_new=False):
#     try:
#         mode = 'w' if is_new else 'a'
#         with open(filename, mode, newline='', encoding='utf-8') as file:
#             writer = csv.DictWriter(file, fieldnames=["keyword", "title", "link"])
#             if is_new:
#                 writer.writeheader()
#             writer.writerow(data)
#         return True
#     except Exception as e:
#         logger.error(f"Error saving to CSV: {e}")
#         return False

# def main():
#     input_csv = "/home/hoanglinh/CrawlData/GGChrome/google_suggestions.csv"  # File chứa danh sách từ khóa
#     output_csv = "google_results.csv"  # File kết quả
#     driver = None
    
#     try:
#         # Kiểm tra file input
#         if not os.path.exists(input_csv):
#             raise FileNotFoundError(f"File {input_csv} không tồn tại.")
        
#         # Đọc từ khóa từ file CSV
#         with open(input_csv, 'r', encoding='utf-8') as file:
#             reader = csv.reader(file)
#             keywords = [row[0] for row in reader]
        
#         if not keywords:
#             raise ValueError("Danh sách từ khóa trống.")
        
#         # Khởi động WebDriver
#         logger.info("Đang khởi động trình duyệt...")
#         driver = web_driver()
        
#         # Ghi header vào file output
#         save_to_csv({}, output_csv, is_new=True)
        
#         # Tìm kiếm từng từ khóa
#         for keyword in keywords:
#             logger.info(f"Tìm kiếm từ khóa: {keyword}")
            
#             if google_search(driver, keyword):
#                 result = scrape_first_result(driver, keyword)
#                 if result:
#                     result["keyword"] = keyword
#                     save_to_csv(result, output_csv)
#                     logger.info(f"Đã lưu kết quả: {result}")
#                 else:
#                     logger.warning(f"Không tìm thấy kết quả cho từ khóa: {keyword}")
#             else:
#                 logger.error(f"Tìm kiếm thất bại cho từ khóa: {keyword}")
            
#             time.sleep(2)  # Tránh bị Google chặn
            
#     except Exception as e:
#         logger.error(f"Lỗi: {e}")
#     finally:
#         if driver:
#             driver.quit()

# if __name__ == "__main__":
#     main()



import os
import csv
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Thread
from queue import Queue
import pandas as pd
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def web_driver():
    chrome_driver_path = '/home/hoanglinh/CrawlData/chromedriver-linux64/chromedriver'
    chrome_binary_path = '/usr/bin/google-chrome'
    
    service = ChromeService(chrome_driver_path)
    options = Options()
    options.binary_location = chrome_binary_path
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument('--blink-settings=imagesEnabled=false')  # Tắt tải ảnh
    
    return webdriver.Chrome(service=service, options=options)

def google_search(driver, keyword):
    try:
        url = "https://www.google.com/"
        driver.get(url)
        time.sleep(1)  # Chờ load trang
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(2)  # Chờ kết quả hiển thị
        return True
    except Exception as e:
        logger.error(f"Error during search for '{keyword}': {e}")
        return False

def scrape_first_result(driver, keyword):
    try:
        first_result = driver.find_element(By.CLASS_NAME, 'V3FYCf')  # CLASS_NAME của kết quả tìm kiếm
        content = first_result.find_element(By.CLASS_NAME, 'hgKElc').text.strip()  # Nội dung mô tả
        link = first_result.find_element(By.CSS_SELECTOR, 'div.yuRUbf a').get_attribute('href')  # URL
        return {"keyword": keyword, "content": content, "link": link}
    except Exception as e:
        logger.warning(f"Could not fetch content, only getting link: {e}")
        try:
            link = driver.find_element(By.CSS_SELECTOR, 'div.yuRUbf a').get_attribute('href')
            return {"keyword": keyword, "content": None, "link": link}
        except Exception as e:
            logger.error(f"Could not fetch link: {e}")
            return {"keyword": keyword, "content": None, "link": None}

def process_keyword(keyword, queue):
    driver = None
    try:
        driver = web_driver()
        if google_search(driver, keyword):
            result = scrape_first_result(driver, keyword)
            queue.put(result)  # Đẩy kết quả vào queue để lưu
        else:
            queue.put({"keyword": keyword, "content": None, "link": None})
    except Exception as e:
        logger.error(f"Error processing keyword '{keyword}': {e}")
        queue.put({"keyword": keyword, "content": None, "link": None})
    finally:
        if driver:
            driver.quit()

def save_to_csv(queue, filename="google_results.csv"):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["keyword", "content", "link"])
            writer.writeheader()

            while True:
                result = queue.get()  # Lấy kết quả từ queue
                if result is None:  # Dừng khi nhận được None (dấu hiệu kết thúc)
                    break
                writer.writerow(result)
                logger.info(f"Saved result: {result}")

    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")

def main():
    input_csv = "/home/hoanglinh/CrawlData/GGChrome/google_suggestions.csv"
    output_csv = "google_results.csv"
    
    try:
        if not os.path.exists(input_csv):
            raise FileNotFoundError(f"Input file {input_csv} does not exist.")
        
        # Đọc từ khóa từ file
        with open(input_csv, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            keywords = [row[0] for row in reader]
        
        if not keywords:
            raise ValueError("Keyword list is empty.")
        
        # Khởi tạo queue và thread cho việc lưu kết quả
        queue = Queue()
        save_thread = Thread(target=save_to_csv, args=(queue, output_csv))
        save_thread.start()

        # Dùng ThreadPoolExecutor để xử lý nhiều từ khóa song song
        logger.info("Starting multithreaded scraping...")
        with ThreadPoolExecutor(max_workers=4) as executor:  # Tùy chỉnh số lượng luồng
            future_to_keyword = {executor.submit(process_keyword, keyword, queue): keyword for keyword in keywords}
            
            for future in as_completed(future_to_keyword):
                keyword = future_to_keyword[future]
                try:
                    future.result()  # Chờ kết quả của luồng
                    logger.info(f"Completed: {keyword}")
                except Exception as e:
                    logger.error(f"Error processing keyword '{keyword}': {e}")

        # Gửi None vào queue để thông báo kết thúc
        queue.put(None)
        save_thread.join()  # Đợi thread lưu kết quả hoàn thành

        logger.info(f"Scraping completed. Results saved to {output_csv}.")
    
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()
