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
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import logging
from datetime import datetime

def setup_logging():
    """Thiết lập hệ thống logging"""
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join(log_directory, f"scraper_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def web_driver():
    """Khởi tạo và cấu hình WebDriver"""
    logger = logging.getLogger(__name__)
    
    chrome_driver_path = '/home/hoanglinh/CrawlData/chromedriver-linux64/chromedriver'
    chrome_binary_path = '/usr/bin/google-chrome'
    
    # Kiểm tra đường dẫn
    if not os.path.exists(chrome_driver_path):
        logger.error(f"Không tìm thấy chromedriver tại {chrome_driver_path}")
        raise FileNotFoundError(f"Không tìm thấy chromedriver tại {chrome_driver_path}")
    if not os.access(chrome_driver_path, os.X_OK):
        logger.error(f"Không có quyền thực thi chromedriver tại {chrome_driver_path}")
        raise PermissionError(f"Không có quyền thực thi chromedriver")
    if not os.path.exists(chrome_binary_path):
        logger.error(f"Không tìm thấy Chrome browser tại {chrome_binary_path}")
        raise FileNotFoundError(f"Không tìm thấy Chrome browser")
    if not os.access(chrome_binary_path, os.X_OK):
        logger.error(f"Không có quyền thực thi Chrome browser tại {chrome_binary_path}")
        raise PermissionError(f"Không có quyền thực thi Chrome browser")
    
    # Cấu hình Chrome options
    service = ChromeService(chrome_driver_path)
    options = Options()
    options.binary_location = chrome_binary_path
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-notifications')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_argument('--disable-extensions')
    
    try:
        logger.info("Khởi tạo WebDriver...")
        driver = webdriver.Chrome(service=service, options=options)
        logger.info("WebDriver đã được khởi tạo thành công")
        return driver
    except Exception as e:
        logger.error(f"Lỗi khởi tạo WebDriver: {str(e)}")
        raise

def google_search(driver, keyword):
    """Thực hiện tìm kiếm Google"""
    logger = logging.getLogger(__name__)
    
    try:
        url = "https://www.google.com/"
        logger.info(f"Truy cập {url}")
        driver.get(url)
        time.sleep(2)
        
        logger.info(f"Tìm kiếm với từ khóa: {keyword}")
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        
        logger.info("Tìm kiếm thành công")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi tìm kiếm: {str(e)}")
        return False

def save_result(result, filename="google_suggestions.csv", is_new=False):
    """Lưu kết quả vào file CSV"""
    logger = logging.getLogger(__name__)
    
    try:
        mode = 'w' if is_new else 'a'
        with open(filename, mode, newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=["title", "content", "link"])
            if is_new:
                writer.writeheader()
                logger.info(f"Đã tạo file {filename} mới")
            else:
                writer.writerow(result)
                logger.debug(f"Đã lưu một kết quả vào {filename}")
        return True
    except Exception as e:
        logger.error(f"Lỗi khi lưu vào CSV: {str(e)}")
        return False

def wait_for_new_suggestions(driver, timeout=10):
    """Đợi và kiểm tra có gợi ý mới không"""
    logger = logging.getLogger(__name__)
    
    old_height = driver.execute_script("return document.body.scrollHeight")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    logger.debug(f"Đã cuộn trang, chiều cao cũ: {old_height}")

    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.body.scrollHeight") > old_height
        )
        new_height = driver.execute_script("return document.body.scrollHeight")
        logger.debug(f"Tìm thấy nội dung mới, chiều cao mới: {new_height}")
        return True
    except TimeoutException:
        logger.debug("Không tìm thấy nội dung mới sau khi cuộn")
        return False

def scrape_suggestions(driver, filename="google_suggestions.csv"):
    """Thu thập các gợi ý từ Google"""
    logger = logging.getLogger(__name__)
    processed_titles = set()
    processed_urls = set()
    processed_content = set()
    total_results = 0
    
    # Tạo file mới với header
    save_result({}, filename, is_new=True)
    
    try:
        while True:
            wait = WebDriverWait(driver, 10)
            
            # Thu thập các gợi ý trực tiếp
            try:
                suggestions_container = wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "cUnQKe"))
                )
                suggestion_divs = suggestions_container.find_elements(By.CSS_SELECTOR, '[jsname="tJHJj"]')
                if suggestion_divs:
                    logger.info(f"Tìm thấy {len(suggestion_divs)} gợi ý trực tiếp")
                    total_results = process_suggestions(driver, suggestion_divs, processed_titles, 
                                                     processed_urls, processed_content, total_results, filename)
            except TimeoutException:
                logger.debug("Không tìm thấy gợi ý trực tiếp")
            
            # Thu thập các gợi ý liên quan
            try:
                # Cuộn xuống cuối trang
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Tìm các gợi ý liên quan
                related_containers = driver.find_elements(By.CSS_SELECTOR, "div.g")
                if related_containers:
                    logger.info(f"Tìm thấy {len(related_containers)} gợi ý liên quan")
                    total_results = process_related_suggestions(driver, related_containers, processed_titles, 
                                                             processed_urls, processed_content, total_results, filename)
            except Exception as e:
                logger.debug(f"Không tìm thấy gợi ý liên quan: {str(e)}")
            
            # Tìm và click nút "Xem thêm" nếu có
            try:
                more_button = driver.find_element(By.CSS_SELECTOR, "a#pnnext")
                if more_button:
                    logger.info("Tìm thấy nút 'Xem thêm'")
                    driver.execute_script("arguments[0].click();", more_button)
                    time.sleep(3)
                    continue
            except NoSuchElementException:
                logger.info("Không còn nút 'Xem thêm'")
                break
            
            if not wait_for_new_suggestions(driver):
                logger.info("Không còn gợi ý mới")
                break
    
    except Exception as e:
        logger.error(f"Lỗi trong quá trình scraping: {str(e)}")
    finally:
        processed_titles.clear()
        processed_content.clear()
        processed_urls.clear()
    
    return total_results

def process_suggestions(driver, divs, processed_titles, processed_urls, processed_content, total_results, filename):
    """Xử lý các gợi ý trực tiếp"""
    logger = logging.getLogger(__name__)
    wait = WebDriverWait(driver, 10)
    
    for div in divs:
        try:
            title = div.find_element(By.CLASS_NAME, "CSkcDe").text.strip()
            
            if title in processed_titles:
                logger.debug(f"Bỏ qua tiêu đề đã xử lý: {title}")
                continue
            
            logger.info(f"Đang xử lý tiêu đề: {title}")
            
            driver.execute_script("arguments[0].click();", div)
            time.sleep(1)
            
            main_content = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "bCOlv"))
            )
            
            content = main_content.find_element(By.CLASS_NAME, "hgKElc").text.strip()
            link = main_content.find_element(By.TAG_NAME, 'a').get_attribute("href")
            
            if not content or content in processed_content or link in processed_urls:
                logger.warning(f"Nội dung hoặc link trùng lặp cho tiêu đề: {title}")
                driver.execute_script("arguments[0].click();", div)
                time.sleep(1)
                continue
            
            result = {"title": title, "content": content, "link": link}
            if save_result(result, filename):
                total_results += 1
                processed_titles.add(title)
                processed_content.add(content)
                processed_urls.add(link)
                logger.info(f"Đã lưu kết quả {total_results}: {title}")
            
            driver.execute_script("arguments[0].click();", div)
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý gợi ý {title if 'title' in locals() else 'unknown'}: {str(e)}")
            continue
    
    return total_results

def process_related_suggestions(driver, containers, processed_titles, processed_urls, processed_content, total_results, filename):
    """Xử lý các gợi ý liên quan"""
    logger = logging.getLogger(__name__)
    
    for container in containers:
        try:
            # Tìm tiêu đề và link trong gợi ý liên quan
            title_element = container.find_element(By.CSS_SELECTOR, "h3")
            title = title_element.text.strip()
            
            if title in processed_titles:
                logger.debug(f"Bỏ qua tiêu đề liên quan đã xử lý: {title}")
                continue
            
            logger.info(f"Đang xử lý tiêu đề liên quan: {title}")
            
            # Tìm link và snippet
            link = container.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
            try:
                content = container.find_element(By.CSS_SELECTOR, "div.VwiC3b").text.strip()
            except NoSuchElementException:
                content = "Không có mô tả"
            
            if not content or content in processed_content or link in processed_urls:
                logger.warning(f"Nội dung hoặc link trùng lặp cho tiêu đề liên quan: {title}")
                continue
            
            result = {"title": title, "content": content, "link": link}
            if save_result(result, filename):
                total_results += 1
                processed_titles.add(title)
                processed_content.add(content)
                processed_urls.add(link)
                logger.info(f"Đã lưu kết quả liên quan {total_results}: {title}")
            
        except Exception as e:
            logger.error(f"Lỗi khi xử lý gợi ý liên quan {title if 'title' in locals() else 'unknown'}: {str(e)}")
            continue
    
    return total_results
def main():
    # Khởi tạo logging
    logger = setup_logging()
    logger.info("Bắt đầu chương trình")
    
    keyword = input("Nhập từ khóa tìm kiếm: ")
    filename = "google_suggestions.csv"
    driver = None
    
    try:
        logger.info("Đang khởi động trình duyệt...")
        driver = web_driver()
        logger.info(f"Đang tìm kiếm với từ khóa: {keyword}")
        
        if google_search(driver, keyword):
            logger.info("Bắt đầu thu thập dữ liệu...")
            total_results = scrape_suggestions(driver, filename)
            
            if total_results > 0:
                logger.info(f"Hoàn thành! Đã thu thập và lưu {total_results} kết quả vào {filename}")
            else:
                logger.warning("Không tìm thấy kết quả nào")
    except Exception as e:
        logger.error(f"Lỗi chương trình: {str(e)}")
    finally:
        if driver:
            driver.quit()
            logger.info("Đã đóng trình duyệt")

if __name__ == "__main__":
    main()