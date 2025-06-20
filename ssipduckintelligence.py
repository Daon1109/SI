
import clip
import torch
from PIL import Image
from torchvision import transforms
import os


# 전처리 함수 정의
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

########## 나중에는 애니 제목 입력해서 웹크롤링으로 긁어와서 DB에 저장하는 형식으로 가기
########## 웹크롤링 기준은 긁어온 사진별 모델 비교시키면서 정하기

# 입력
input_folder_path = 'C:/Coding/SI_DB/input/'             # 이미지 경로 리스트화
image_paths = os.listdir(input_folder_path)
for i in range(len(image_paths)):
    image_paths[i] = input_folder_path + str(image_paths[i])

img_tensors = [preprocess(Image.open(p)) for p in image_paths]      # 전처리 후 텐서 리스트
batch = torch.stack(img_tensors).to(device)         # 리스트로 만든 애들 배치로 묶기

# 벡터 변환
with torch.no_grad():       # 역전파용 메모리 저장 방지
    input_features = model.encode_image(batch)
# Result
print(input_features.shape)  # torch.Size([n, 512]): n개의 512차원 벡터


# 애니 DB 만들기
# 비교 코드 짜기
# DB 손보기(이때 웹크롤링 기준도 대충 세우기)
# 코드 손보기(평균, 클러스터링, 벡터 비교 방식 등등..)
# DB 다시 손보고 웹크롤링 기준 정립
# 웹크롤링 feature 추가(input DB, 추천용 DB 둘 다)
