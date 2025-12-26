# Mr. PC Picker  
AI 기반 컴퓨터 사양 가이드 & 추천 서비스

## 📌 Project Overview
**Mr. PC Picker**는 컴퓨터 구매 시 사양 이해의 어려움을 겪는 사용자들을 위해  
AI 분석을 통해 *용도·예산·사용 기간*에 맞는 최적의 PC 사양을 추천하는 서비스입니다.

CPU, GPU, RAM 등 복잡한 하드웨어 정보를 단순 비교가 아닌  
**“이해 → 확인 → 결정”** 중심의 사용자 경험으로 재구성하는 것을 목표로 합니다. :contentReference[oaicite:0]{index=0}

---

## 👥 Team Members
| 역할 | 이름 | 담당 |
|---|---|---|
| Leader | 양새하 | 기획, DB 설계, API 연동, AI 추천 로직, 프론트/백엔드 |
| Member | 이주선 | 데이터 수집, CRUD 구현, 커뮤니티/프로필 UI |

---

## 🗓 Project Schedule
- **11월**: 기획 수립, 크롤링 테스트, DB 설계
- **12월**: AI 추천 연동(GMS), 커뮤니티 기능, 프론트엔드 구현, 배포 준비 :contentReference[oaicite:1]{index=1}

---

## 🔍 Discover
### Background
> “컴퓨터를 사고 싶은데 사양이 어느 정도 필요한지 이해하기 어렵다.”

- 사양 용어(CPU, GPU, RAM 등)에 대한 진입 장벽
- 사용 목적과 직접 연결된 설명 부족
- 단순 스펙 나열 중심의 기존 서비스 한계 :contentReference[oaicite:2]{index=2}

### 3C · SWOT 요약
- **Customer**: 컴퓨터에 익숙하지 않은 일반 사용자
- **Company**: AI 기반 맞춤 추천
- **Competitor**: 가격·스펙 나열 중심 서비스

**Strength**: AI 기반 이해 중심 추천  
**Weakness**: 초기 데이터 품질 의존  
**Opportunity**: PC 구매 수요 증가  
**Threat**: 기존 대형 비교 플랫폼 :contentReference[oaicite:3]{index=3}

---

## 🧩 Define
### Persona
- 23세 대학생
- 예산: 200만 원
- 목적: 과제 + 영상 편집
- Pain Point: “사양을 몰라도 합리적인 선택을 하고 싶다” :contentReference[oaicite:4]{index=4}

### Key Insight
> **정보 과잉 속에서는 ‘이해’보다 ‘확신’이 필요하다**

---

## 🗺 Information Architecture
### Site Map
- Home
- Needs Input → AI Analysis → AI Recommendation
- Search / Filter / Product List
- Community (게시글 · 댓글 · 좋아요)
- Profile (정보 수정, 찜 목록) :contentReference[oaicite:5]{index=5}

---

## 🚀 Develop
### Service Concept
- AI가 사용자의 입력을 해석
- “왜 이 사양이 필요한지”를 설명
- 추천 결과를 커뮤니티로 검증 :contentReference[oaicite:6]{index=6}

### Core Experience
1. Needs 입력
2. AI 사양 분석
3. AI 추천 결과 제공
4. 커뮤니티 검증
5. 구매 의사결정 지원

---

## 🎨 Brand Design
- **Color**
  - Red: 핵심 포인트
  - Black: 신뢰감
  - Blue: 기술·AI 이미지
- **Concept**
  - 전문적이지만 접근하기 쉬운 컴퓨터 가이드 서비스 :contentReference[oaicite:7]{index=7}

---

## 🔄 Service Scenario
1. 사용자가 용도·예산 입력
2. AI가 적합한 사양 분석
3. 추천 PC 리스트 제공
4. 커뮤니티 후기 확인
5. 최종 구매 결정 :contentReference[oaicite:8]{index=8}

---

## ⚙ Deliver
### Database (ERD)
- product_search
- product_detail_raw
- product_detail_spec
- user_needs
- recommendations
- articles / comments / likes :contentReference[oaicite:9]{index=9}

### Tech Stack
- **Frontend**: Vue
- **Backend**: Django REST
- **Database**: SQLite
- **AI**: GMS 기반 추천 모델
- **ETC**: 크롤링, 정규화 모델

---

## 📦 Result & Reflection
- 사양 이해 장벽을 UX로 해결
- AI 추천 + 커뮤니티 결합 구조 완성
- 향후 가격 비교 고도화 및 모델 성능 개선 예정

---

## 🔮 Future Work
- 실시간 가격 연동
- 추천 정확도 개선
- 사용자 리뷰 기반 추천 강화
