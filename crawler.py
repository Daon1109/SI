
import random
import SI_modules as sim
from selenium.common.exceptions import TimeoutException
import time
import os



# 크롤링 코드(main)
def crawl_anisearch_bulk(start_index: int, end_index: int):         # function(시작 인덱스, 종료 인덱스)
    done_indexes = sim.load_done_indexes()

    for anime_id in range(start_index, end_index + 1):
        if anime_id in done_indexes:
            print(f"[{anime_id}] - 이미 완료됨. 건너뜀.")
            continue

        try:
            url = f"https://www.anisearch.com/anime/{anime_id}/screenshots"
            print(f"\n[{anime_id}] - 크롤링 시작: {url}")

            image_links, title = sim.get_image_links_from_screenshots_page(url, max_links=8)

            if not image_links:
                print(f"[{anime_id}] - 이미지 없음. 건너뜀.")
                sim.log_done_index(anime_id)
                continue

            slug = sim.encode_filename(title)
            save_dir = os.path.join("C:/Coding/doodles/ssipduck_intelligence/SI_DB/recommends/originals", slug)
            os.makedirs(save_dir, exist_ok=True)

            print(f"[{anime_id}] - 이미지 다운로드 중...")
            sim.download_images_parallel(image_links, save_dir)

            sim.log_done_index(anime_id)
            print(f"[{anime_id}] - 완료\n")

            # 무작위로 0.5~2초 쉬기
            time.sleep(random.uniform(0.5, 2.0))

        except Exception as e:
            print(f"[{anime_id}] - 오류 발생: {e}")
            time.sleep(1)
            continue


# execution
crawl_anisearch_bulk(2001, 5000)





"""
# 크롤링 코드(일단 무작위 100개만 함)
rand_index = random.sample(range(1, 20670), 30)        # anisearch.com index는 20669까지 있음
for i in range(30):
    rand_url = f"https://www.anisearch.com/anime/{rand_index[i]}/screenshots/"

    try:
        image_links, title_raw = sim.get_image_links_from_screenshots_page(rand_url, max_links=8)
        title_encoded = sim.encode_filename(title_raw)          # 인코딩
        save_path = os.path.join(f"C:/Coding/doodles/ssipduck_intelligence/SI_DB/umm/{title_encoded}/")
        if image_links:
            print("이미지 다운로드 중...")
            sim.download_images_parallel(image_links, save_dir=save_path)
        else:
            print("스틸컷 없음")
    except TimeoutException:
        print(f"Timeout: {rand_url} (스틸컷 없음 또는 페이지 비정상)")
    except Exception as e:
        print(f"예외 발생 {rand_url}: {e}")
"""