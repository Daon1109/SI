
import clip
import torch
from PIL import Image
from torchvision import transforms
import torch.nn.functional as F
import os
import SI_modules as sim


# 전처리 함수
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),         # 크기 통일
    transforms.ToTensor(),                 # 숫자로 바꾸기 (0~1 사이 R)
    transforms.Normalize(                  # 평균과 표준편차(CLIP)로 정규화
        mean=[0.48145466, 0.4578275, 0.40821073],
        std=[0.26862954, 0.26130258, 0.27577711]
    )
])

if torch.cuda.is_available():       # GPU 사용
    device = "cuda" 
else:                               # 글카가없는내후진노트북을위한보완코드
    device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)




# 애니 제목 입력(선택)
ani_input_choice = input("에니메이션 제목으로 검색하시겠습니까?(y/n): ")
if ani_input_choice == "Y" or ani_input_choice == "y":
    ani_title_input = input("애니메이션 제목을 입력하세요: ")
    result_url = sim.get_anisearch_url(ani_title_input)
    print(f"\n검색된 URL: {result_url}")

    # 크롤링 및 다운로드
    save_path = os.path.join("C:/Coding/doodles/ssipduck_intelligence/SI_DB/inputs/")
    image_links, title = sim.get_image_links_from_screenshots_page(result_url+"/screenshots/", max_links=8)
    if image_links:
        print("이미지 다운로드 중...")
        sim.download_images_parallel(image_links, save_dir=save_path)
elif ani_input_choice == "N" or ani_input_choice == "n":
    pass
else:
    print("ERROR: Wrong Input")

    


# 이미지 입력
input_folder_path = 'C:/Coding/doodles/ssipduck_intelligence/SI_DB/inputs/'             # 이미지 경로 리스트화
image_paths = os.listdir(input_folder_path)
for i in range(len(image_paths)):
    image_paths[i] = input_folder_path + str(image_paths[i])

img_tensors = [preprocess(Image.open(p)) for p in image_paths]      # 전처리 후 텐서 리스트
batch = torch.stack(img_tensors).to(device)         # 리스트로 만든 애들 배치로 묶기




# 벡터 변환
with torch.no_grad():       # 역전파용 메모리 저장 방지
    input_features = model.encode_image(batch)
# 임베딩 결과
print(input_features.shape)  # torch.Size([n, 512]): n개의 512차원 벡터
# input 평균내기
input_mean = input_features.mean(dim=0, keepdim=True)       # 이거 방식은 중앙값, clustering 같은 거로 갈아끼울 수 있음(이걸로도 정확도 개선 ㄱㄴ)




# embedded DB 불러오기
recommend_vectors = torch.load("C:/Coding/doodles/ssipduck_intelligence/SI_DB/recommends/embeddings/recommend_vectors.pt")  # 딕셔너리 형태     e.g. {'제목': tensor([512]), }
anime_names = list(recommend_vectors.keys())
anime_features = torch.stack([recommend_vectors[name] for name in anime_names]).to(device)  # DB에 있는 벡터 전부 쌓기

# 유사도 계산 - Cosine Similarity
input_norm = F.normalize(input_mean, dim=1)                    # normalize: 벡터 정규화 후 각도 기반으로 비교(이게 코사인유사도 방식임)
anime_norm = F.normalize(anime_features, dim=1)                
similarity = torch.matmul(anime_norm, input_norm.T).squeeze()   # 계산 결과: [N, 1](2차원인데 N*1 행렬임) // squeeze: [N](차원 날려서 리스트같은 1차원 텐서로 만듦)

# 유사도 정렬 및 출력
sorted_scores, org_index = similarity.sort(descending=True)       # 텐서라서 원래 인덱스(org_index) 추적 가능
print("\nTop 10")
for j in range(10):
    rec_ani_idx = org_index[j].item()
    print(f"{j+1}. {sim.decode_filename(anime_names[rec_ani_idx])} (cosine similarity: {sorted_scores[j].item():.4f})")     # 파일 이름 디코딩 여기서 함

