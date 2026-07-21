# 📊 지역별 인구 구조 대시보드

행정안전부 주민등록 연령별 인구현황 데이터를 기반으로, 전국 행정구역(읍면동 포함)의 연령별 인구 구조를 시각화하고, 인구 구조가 유사한 지역을 찾아주는 Streamlit 웹 애플리케이션입니다.

## 🔗 배포 링크

[Streamlit Cloud에서 앱 열기](https://share.streamlit.io) *(배포 후 실제 URL로 교체)*

## ✨ 주요 기능

### 1. 지역별 인구 구조 조회 (메인 페이지)
- 검색어 입력 + 드롭다운 선택을 결합한 지역 선택 (읍면동 단위까지 지원)
- 연령별 인구수를 Plotly 꺾은선 그래프로 시각화
- 전체(계) / 남성 / 여성 / 남녀 비교 4가지 모드 전환
- 총인구수, 평균 연령(추정), 65세 이상 비율 등 핵심 지표 표시

### 2. 인구 구조 유사 지역 Top N (서브 페이지)
- 선택한 지역과 연령대별 인구 구성비가 가장 비슷한 전국 지역을 코사인 유사도(Cosine Similarity)로 산출
- 절대 인구수 기준 / 구성비(%) 기준 두 가지 비교 그래프 제공
- Top 3~10위까지 슬라이더로 조절 가능
- 유사도 순위표(테이블) 함께 제공

## 📁 폴더 구조
├── app.py # 메인 페이지 (지역별 인구 구조)
├── utils.py # 공통 함수 (데이터 로딩, 유사도 계산 등)
├── requirements.txt # 의존 패키지 목록
├── 202606_202606_연령별인구현황_월간.csv # 원본 데이터
└── pages/
└── 1_유사지역_Top5.py # 서브 페이지 (유사 지역 Top N)

## 🛠 기술 스택

- **Frontend/App Framework**: Streamlit
- **시각화**: Plotly
- **데이터 처리**: Pandas, NumPy
- **배포**: Streamlit Community Cloud

## 📦 requirements.txt
streamlit
pandas
plotly
numpy


## 🚀 로컬 실행 방법

```bash
git clone <이 저장소 URL>
cd <저장소 폴더>
pip install -r requirements.txt
streamlit run app.py
```

## ☁️ Streamlit Cloud 배포 방법

1. GitHub 저장소에 `app.py`, `utils.py`, `requirements.txt`, CSV 데이터 파일, `pages/` 폴더를 모두 루트 기준으로 push
2. [share.streamlit.io](https://share.streamlit.io)에서 New app 클릭
3. 저장소, 브랜치, Main file path를 `app.py`로 지정 후 Deploy
4. 배포 후 사이드바에서 `pages/` 폴더 내 서브페이지가 자동으로 메뉴로 표시됨

## 📌 데이터 처리 방식

- 원본 CSV는 `cp949` 인코딩, 숫자에 쉼표(,)가 포함된 형식이라 `thousands=","` 옵션으로 파싱
- 일부 행에서 필드 수 불일치가 발생해 `on_bad_lines="skip"` 옵션으로 예외 행 제외
- 행정구역명에서 코드 괄호(예: `(1.1e+09)`)를 정규식으로 제거해 지역명만 추출
- 연령별 인구를 전체 인구로 나눠 구성비(%)로 정규화한 뒤 코사인 유사도를 계산해 규모가 다른 지역끼리도(서울시 전체 vs 소규모 읍면동) 비교 가능하게 처리

## ⚠️ 주의사항 (트러블슈팅)

- `pages/` 폴더는 반드시 `app.py`와 같은 루트 레벨에 있어야 하며, 폴더명 대소문자를 정확히 `pages`로 지정해야 함
- 서브페이지 파일명에 **공백을 포함하면 인식되지 않을 수 있음** — 언더스코어(`_`)나 하이픈(`-`)만 사용 권장 (예: `1_유사지역_Top5.py`)
- 파일명이 `_`로 시작하면 Streamlit이 숨김 파일로 처리해 사이드바에 표시하지 않음
- CSV 파일이 100MB를 초과할 경우 Git LFS 설정 필요

## 📄 라이선스

이 프로젝트는 개인 학습 및 포트폴리오 목적으로 제작되었습니다.
