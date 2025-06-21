
import clip
import torch
from torchvision import transforms
from PIL import Image
import os
import torch.nn.functional as F


# CLIP settings
if torch.cuda.is_available():
    device = "cuda" 
else:
    device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# 경로
# base_path = "C:/Coding/ssipduck_intelligence/SI_DB/recommends/originals"      # recommend_images/애니제목/이미지들
base_path = "C:/Coding/ssipduck_intelligence/SI_DB/test_rcmd"
output_path = "C:/Coding/ssipduck_intelligence/SI_DB/recommends/embeddings/recommend_vectors.pt"      # 이미지 버전별로 이거 수정하기
# 저장용 딕셔너리
recommend_vectors = {}




# 애니 폴더별 처리
for anime_name in os.listdir(base_path):
    anime_folder = os.path.join(base_path, anime_name)
    if not os.path.isdir(anime_folder):
        continue  # 혹시 폴더가 아닌 파일이 있을 경우 생략

    # 이미지 불러오기
    image_paths = [os.path.join(anime_folder, f) for f in os.listdir(anime_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if len(image_paths) == 0:
        continue  # 이미지가 없다면 건너뜀

    # 이미지 전처리 및 텐서화
    img_tensors = []
    for path in image_paths:
        try:
            image = preprocess(Image.open(path).convert("RGB"))
            img_tensors.append(image)
        except:
            print(f"Error loading image: {path}")
            continue

    if len(img_tensors) == 0:
        continue  # 전처리 실패 시 건너뜀

    # 배치로 묶기
    batch = torch.stack(img_tensors).to(device)

    # 벡터화
    with torch.no_grad():
        features = model.encode_image(batch)  # shape: [n, 512]
        features = F.normalize(features, dim=1)  # 정규화 (선택 사항이지만 추천)

    # 평균 벡터 계산
    mean_vector = features.mean(dim=0)  # shape: [512]
    recommend_vectors[anime_name] = mean_vector.cpu()

# 저장
torch.save(recommend_vectors, output_path)
print(f"Saved recommend vectors to {output_path}")
