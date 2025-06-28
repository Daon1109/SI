
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import unicodedata
from PIL import Image
import os
import requests
import time
import random
from concurrent.futures import ThreadPoolExecutor
from selenium.common.exceptions import TimeoutException



def get_anisearch_url(anime_name: str) -> str:          # 추천 검색어 최상단 링크 불러옴
    # 1. 브라우저 열기
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 브라우저 창 안 띄우고 실행 (원하면 빼도 됨)
    driver = webdriver.Chrome(options=options)

    try:
        # 2. 사이트 접속
        driver.get("https://www.anisearch.com/anime")

        # 3. 검색창 찾고 제목 입력
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "qsearch"))
        )
        search_box.send_keys(anime_name)

        # 4. 자동완성 결과가 뜰 때까지 대기
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ul.ui-autocomplete li a"))
        )

        # 5. 자동완성 첫 번째 결과 추출
        suggestions = driver.find_elements(By.CSS_SELECTOR, "ul.ui-autocomplete li a")
        if not suggestions:
            print("검색 결과가 없습니다.")
            return None

        first_result = suggestions[0]
        url = first_result.get_attribute("href")
        return url

    except Exception as e:
        print("오류 발생:", e)
        return None

    finally:
        driver.quit()



def webp_2_jpg(anime_name):       # ㅈㄱㄴ

    input_folder = f"C:/Coding/doodles/ssipduck_intelligence/SI_DB/recommends/webp/{anime_name}"
    output_folder = f"C:/Coding/doodles/ssipduck_intelligence/SI_DB/recommends/jpg/{anime_name}"

    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(".webp"):
            path = os.path.join(input_folder, filename)
            img = Image.open(path).convert("RGB")
            new_name = os.path.splitext(filename)[0] + ".jpg"
            img.save(os.path.join(output_folder, new_name), "JPEG")



def slugmaker(anime_title):     # 애니 이름 slug 형태로 바꿔줌

    title = unicodedata.normalize("NFKD", anime_title)  # Unicode to ASCII (영어 뺴고 다 날림)
    title = title.encode("ascii", "ignore").decode("ascii")
    title = title.lower()                           # 소문자 변환
    title = re.sub(r"[^a-z0-9\s-]", "", title)      # 특수문자 제거 (알파벳/숫자/공백/하이픈만 남김)
    title = re.sub(r"[\s]+", "-", title)            # 공백 to 하이픈
    title = re.sub(r"-+", "-", title)               # 하이픈 여러 개 하나로 만듦
    return title.strip("-")                         # 양끝 하이픈 제거



def get_image_links_from_screenshots_page(url: str, max_links: int = 12) -> list[str]:      # screenshots 페이지 열고 이미지 링크랑 애니제목만 추출(selenium 기반)
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    title = None
    try:

        # 애니제목 추출
        driver.get(url)
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "htitle"))
            )
            title_elem = driver.find_element(By.ID, "htitle")
            title = title_elem.text
            print(f"\n애니 제목 추출 완료: {title}")
        except TimeoutException:
            print("\n제목 요소 로딩 실패 (htitle 없음)")
        except Exception as e:
            print(f"\n제목 추출 중 예외 발생: {e}")


        # 이미지 링크 추출
        print("\n페이지 로딩 중...")
        # a.zoom 요소가 렌더링될 때까지 최대 10초 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.zoom"))
        )

        a_tags = driver.find_elements(By.CSS_SELECTOR, "a.zoom")
        links = []
        for a in a_tags:
            href = a.get_attribute("href")
            if href and href.endswith(".webp"):
                links.append(href)
                if len(links) >= max_links:
                    break

        if not links:
            print("\n이미지 링크를 찾지 못했습니다.")
        else:
            print(f"\n{len(links)}개의 이미지 링크 수집 완료")


    finally:
        driver.quit()
        
    return links, title



def download_image(i, url, save_dir):       # 개별 이미지 다운로드(requests 기반)
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            file_path = os.path.join(save_dir, f"screenshot_{i+1}.webp")
            with open(file_path, "wb") as f:
                f.write(resp.content)
            print(f"저장 완료: {file_path}")
        else:
            print(f"실패 {resp.status_code}: {url}")
    except Exception as e:
        print(f"예외 발생: {url} ({e})")



def download_images_parallel(image_links, save_dir="screenshots", max_workers=6):       # 병렬 이미지 다운로드(속도 좀 빨라짐)
    os.makedirs(save_dir, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i, url in enumerate(image_links):
            executor.submit(download_image, i, url, save_dir)



# 인코딩용 치환 딕셔너리
ENCODE_MAP = {
    ':': '__COLON__',
    '/': '__SLASH__',
    '?': '__Q__',
    '*': '__STAR__',
    '"': '__QUOTE__',
    "'": '__APOS__',
    '\\': '__BSLASH__',
    '<': '__LT__',
    '>': '__GT__',
    '|': '__PIPE__',
}
# 역변환용 딕셔너리
DECODE_MAP = {v: k for k, v in ENCODE_MAP.items()}


def encode_filename(title: str) -> str:             # 파일명 인코딩 함수
    for char, replacement in ENCODE_MAP.items():
        title = title.replace(char, replacement)
    return title

def decode_filename(encoded: str) -> str:             # 파일명 디코딩 함수
    for replacement, char in DECODE_MAP.items():
        encoded = encoded.replace(replacement, char)
    return encoded



# 경로 설정
SAVE_ROOT = "C:/Coding/doodles/ssipduck_intelligence/SI_DB/recommends/originals"
DONE_LOG_PATH = "C:/Coding/doodles/ssipduck_intelligence/SI_DB/crawled_animes.txt"


def load_done_indexes() -> set[int]:            # 중간 저장된 인덱스 불러오기
    if not os.path.exists(DONE_LOG_PATH):
        return set()
    with open(DONE_LOG_PATH, "r", encoding="utf-8") as f:
        return set(int(line.strip()) for line in f if line.strip().isdigit())


def log_done_index(anime_id: int):              # 완료한 애니메이션 인덱스 기록
    with open(DONE_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"{anime_id}\n")







# TEST   
if __name__ == "__main__":                  # 이 파일을 직접 실행할 때만 아래 코드 실행됨(모듈로 참조 시 실행 X)
    title = "Puella Magi Madoka Magica"
    result_url = get_anisearch_url(title)
    if result_url:
        print(f"검색된 URL: {result_url}")

    ani_title_raw = input("Title: ")
    ani_title_slug = slugmaker(ani_title_raw)
    print(ani_title_slug)
