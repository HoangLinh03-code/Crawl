import os
import time
import csv
from selenium import webdriver
import sys
import platform
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import logging
import re
import subprocess
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_chrome_version():
    try:
        # Lấy phiên bản Chrome từ terminal
        output = subprocess.check_output(["google-chrome", "--version"]).decode("utf-8")
        version = re.search(r"\d+\.\d+\.\d+", output).group(0)  # Trích xuất phiên bản (ví dụ: 126.0.6478.55)
        return version
    except Exception as e:
        print(f"Không thể lấy phiên bản Chrome: {e}")
        return None

def get_chromedriver_path():
    system = platform.system().lower()
    base_path = os.path.dirname(os.path.abspath(__file__))
    chrome_driver_dir = os.path.join(base_path, 'ChromeDriver')
    
    if system == 'windows':
        driver_name = 'chromedriver_Win64.exe'
    elif system == 'darwin':
        if platform.machine() == 'arm64':
            driver_name = 'chromedriver_MacARM64'
        else:
            driver_name = 'chromedriver_MACx64'
    else:
        # Xử lý cho Linux x64
        chrome_version = get_chrome_version()
        if chrome_version:
            major_version = int(chrome_version.split('.')[0])  # Lấy số phiên bản chính (ví dụ: 126)
            if major_version < 129:  # Phiên bản Chrome cũ
                driver_name = 'chromedriver_Linux_new'
            else:  # Phiên bản Chrome mới
                driver_name = 'chromedriver_Linux_new'
        else:
            raise RuntimeError("Không thể xác định phiên bản Chrome.")
    
    driver_path = os.path.join(chrome_driver_dir, driver_name)
    if system != 'windows':
        os.chmod(driver_path, 0o755)
    return driver_path

def web_driver(chrome_driver_path=None, headless=False):
    if chrome_driver_path is None:
        chrome_driver_path = get_chromedriver_path()
    
    if not os.path.exists(chrome_driver_path):
        raise FileNotFoundError(f"Chrome driver không tìm thấy tại: {chrome_driver_path}")
    
    service = ChromeService(executable_path=chrome_driver_path)
    options = Options()
    if headless:
        options.add_argument('--headless')  # Bật chế độ headless
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def google_search(driver, keyword):
    try:
        driver.get("https://www.google.com/")
        time.sleep(2)
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        return True
    except Exception as e:
        logger.error(f"Lỗi trong quá trình tìm kiếm cho {keyword}: {e}")
        return False

def sanitize_filename(keyword):
    """Làm sạch tên file bằng cách loại bỏ các ký tự không hợp lệ"""
    return re.sub(r'[\\/*?:"<>|]', '_', keyword).strip()

def scrape_suggestions(driver, keyword, initial_clicks=20, progress_callback=None, status_callback=None, stop_event=None):
    processed_titles = set()
    total_results = 0
    suggestions_count = 0
    
    try:
        if status_callback:
            status_callback(f"Phase 1: Tạo suggestions cho {keyword}...")
        
        for click_count in range(initial_clicks):
            if stop_event and stop_event.is_set():
                if status_callback:
                    status_callback("Quá trình thu thập đã bị dừng.")
                break
            
            time.sleep(3)
            try:
                suggestions_container = driver.find_element(By.CLASS_NAME, "cUnQKe")
            except Exception as e:
                logger.info(f"Không tìm thấy suggestions_container cho {keyword}. Dừng lại và không tạo file CSV.")
                return 0, 0  # Stop processing if the container is not found
            
            first_suggestion = suggestions_container.find_element(By.CSS_SELECTOR, '[jsname="tJHJj"]')
            title = first_suggestion.find_element(By.CLASS_NAME, "CSkcDe").text.strip()
            driver.execute_script("arguments[0].click();", first_suggestion)
            if status_callback:
                status_callback(f"Click {click_count + 1}/{initial_clicks} - Mở cho {keyword}")
            time.sleep(2)
            driver.execute_script("arguments[0].click();", first_suggestion)
            if status_callback:
                status_callback(f"Click {click_count + 1}/{initial_clicks} - Đóng cho {keyword}")
            time.sleep(2)
            
            if progress_callback:
                progress = (click_count + 1) / (initial_clicks * 2) * 100
                progress_callback(progress)
        
        time.sleep(3)
        try:
            suggestions_container = driver.find_element(By.CLASS_NAME, "cUnQKe")
        except Exception as e:
            logger.info(f"Không tìm thấy suggestions_container cho {keyword}. Dừng lại và không tạo file CSV.")
            return 0, 0  # Stop processing if the container is not found
        
        suggestion_divs = suggestions_container.find_elements(By.CSS_SELECTOR, '[jsname="yEVEwb"]')
        suggestions_count = len(suggestion_divs)
        
        if suggestions_count == 0:
            logger.info(f"Không tìm thấy suggestions cho {keyword}. Bỏ qua tạo file CSV.")
            return 0, 0
        
        if status_callback:
            status_callback(f"Tìm thấy {suggestions_count} suggestions cho {keyword}")
            status_callback(f"Phase 2: Thu thập dữ liệu cho {keyword}...")
        
        # Tạo tên file từ keyword
        sanitized_keyword = sanitize_filename(keyword)
        filename = f"{sanitized_keyword}_suggestions.csv"
        
        for index, div in enumerate(suggestion_divs):
            if stop_event and stop_event.is_set():
                if status_callback:
                    status_callback("Quá trình thu thập đã bị dừng.")
                break
            
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
            
            # Lưu dữ liệu vào file CSV
            with open(filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=["title", "content", "link"])
                if file.tell() == 0:
                    writer.writeheader()
                writer.writerow(result)
            
            total_results += 1
            processed_titles.add(title)
            
            if status_callback:
                status_callback(f"Thu thập: {title} cho {keyword}")
            
            if progress_callback:
                base_progress = 50
                phase2_progress = (index + 1) / suggestions_count * 50
                total_progress = base_progress + phase2_progress
                progress_callback(total_progress)
                
    except Exception as e:
        if status_callback:
            status_callback(f"Lỗi cho {keyword}: {str(e)}")
    
    return total_results, suggestions_count