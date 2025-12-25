# 🛠 GMS 연동 안정화 작업 기록 (Root Cause & Fix)

## 1. 개요
본 프로젝트의 **Recommend(추천)** 기능은 사용자 입력을 기반으로 **GMS(OpenAI 계열 API)**를 호출하여 결과를 생성하고, 이를 Vue.js 프론트엔드에 전달하는 구조입니다. 개발 과정에서 추천 결과가 간헐적으로 실패하거나 프론트에서 데이터가 누락되는(timeout, undefined) 문제가 발생하였으며, 본 문서는 해당 문제의 근본 원인 분석과 구조적 개선 과정을 정리한 기록입니다.

---

## 2. 주요 장애 증상
### 🔴 프론트엔드 (Vue.js)
* **네트워크 오류:** `Axios timeout of 30000ms exceeded` 발생.
* **데이터 누락:** 추천 리스트가 랜덤하게 미출력되거나 상세 스펙(CPU, GPU 등)이 `undefined`로 표시됨.
* **UI 깨짐:** 이미지, 가격, 쇼핑 링크 등 연관 데이터가 동시에 렌더링되지 않음.

### 🔴 백엔드 (Django)
* **상태 코드 왜곡:** HTTP Status는 `200 OK`이나 실제 데이터는 비어있음.
* **파싱 에러:** GMS 응답 구조 변경으로 인한 `json.loads()` 실패 및 내부 예외 발생.

---

## 3. 근본 원인 분석 (Root Cause)
### "GMS 응답은 확정된 JSON이 아니다"
GMS(LLM)는 항상 일정한 규격의 JSON을 반환하지 않습니다. 다음과 같은 변칙적인 응답이 섞여 들어오는 것이 핵심 문제였습니다.
1.  **자연어 혼합:** JSON 앞뒤에 설명 텍스트가 포함됨 (예: "Here is your recommendation: { ... }").
2.  **타입 불일치:** 동일 항목의 `content` 타입이 `string`, `list`, `object` 등으로 수시로 변경됨.
3.  **구조 파괴:** 토큰 초과나 모델 불안정 시 JSON 형식이 깨진 상태로 반환됨.

**기존 구조의 문제점:**
`views.py`에서 GMS의 원본 문자열을 직접 `json.loads()` 하려 했기 때문에, 조금만 형식이 틀어져도 전체 로직이 중단되고 응답 지연이 발생했습니다.

---

## 4. 해결 전략
> **핵심 원칙:** GMS를 "신뢰할 수 없는 API"로 가정하고, 내부 로직 진입 전 완벽하게 정제한다.

### ✅ 실행 사항
* **경계 레이어(Boundary Layer) 구축:** `gms_client.py`에서 파싱 및 정제 로직을 전담.
* **데이터 강제 규격화:** 마크다운 코드 블록(` ```json `) 제거 및 순수 JSON 추출 로직 적용.
* **Fallback 메커니즘:** 파싱 실패 시 예외를 던지는 대신, 빈 구조의 `dict`를 반환하여 프론트엔드 런타임 에러 방지.
* **View 로직 단순화:** `views.py` 내 `json.loads()`를 완전히 제거하고 데이터 소비자 역할만 수행.



---

## 5. 변경된 시스템 구조
### 📁 gms_client.py (Data Refiner)
```python
def call_gms_openai(prompt):
    # 1. GMS 원본 응답 수신
    # 2. 정규표현식 등을 활용해 JSON 부분만 추출
    # 3. 파싱 후 dict 타입으로 변환
    # 4. 실패 시 기본 구조(Empty dict) 반환
    return parsed_data  # 항상 안정적인 dict 반환
```

### 📁 view.py
```python
def recommend_computers(request):
    gms_data = call_gms_openai(prompt)
    # 별도의 파싱이나 타입 검사 없이 get() 메서드로 안전하게 접근
    recommends = gms_data.get("recommends", [])
    return JsonResponse(recommends)
```

## 🚀 결과 및 핵심 교훈 (Results & Lessons Learned)

### 1. 기술적 개선 결과 (Technical Improvements)
* **런타임 안정성:** GMS 응답이 깨지거나 비정상적인 텍스트가 섞여 들어와도 백엔드에서 즉시 정제하여 **프론트엔드(Vue)의 런타임 에러(undefined)를 원천 차단**했습니다.
* **네트워크 지연 해소:** View 레이어에서의 불필요한 예외 처리 대기 시간을 줄여, 원인 불명의 **Axios Timeout 발생 빈도를 획기적으로 낮췄습니다.**
* **데이터 정합성 유지:** 응답 구조가 부분적으로 누락되더라도 기본값(Default Value)을 반환하는 로직을 통해 **CPU, GPU, 가격 등 핵심 UI 컴포넌트가 항상 렌더링**되도록 보장했습니다.

### 2. 핵심 교훈 (Key Insight)
> **"AI API는 규격화된 JSON API가 아니다."**

이번 트러블슈팅의 핵심은 GMS 자체의 결함이 아니라, **비확정적인 AI의 응답을 확정적인 JSON 데이터로 간주하고 로직을 설계한 구조적 오류**에 있었습니다.

* **경계 레이어의 중요성:** LLM과 같은 외부 비정형 데이터 소스를 다룰 때는 반드시 **경계 레이어(GMS Client)**에서 데이터를 완벽하게 정제(Sanitize)한 뒤 내부 로직(View)으로 넘겨야 합니다.
* **안정적인 아키텍처:** 데이터 소비자(View)는 데이터가 어떤 과정을 거쳐 파싱되었는지 몰라야 하며, 오직 **약속된 Dict 객체**만 전달받는 구조가 가장 안정적입니다.



---
**💡 한 줄 요약:** 문제의 본질은 "GMS의 불안정성"이 아니라 **"GMS를 대하는 백엔드 구조의 유연성 부족"**에 있었으며, 이를 정제 레이어 분리를 통해 해결했습니다.