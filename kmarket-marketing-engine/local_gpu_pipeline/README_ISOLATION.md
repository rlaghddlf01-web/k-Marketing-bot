# 🛡️ [완전 분리형 로컬 GPU AI 생성 파이프라인]
## local_gpu_pipeline

### 1. 설계 및 격리 원칙
* 본 디렉토리는 기존 K-Market/EasyTax 마케팅 봇 코드와 **100% 완벽하게 분리된 독립 모듈**입니다.
* 기존 `modules/shorts_kmarket.py`, `core/` 등의 순정 코드를 일절 수정하거나 침범하지 않습니다.
* **언제든지 이 `local_gpu_pipeline` 폴더만 우클릭 삭제(Delete)하면 기존 시스템에 어떠한 영향도 없이 100% 즉시 원상 복구됩니다.**

### 2. 구동 기술
* **GPU**: NVIDIA GeForce RTX 5060 Ti 16GB (Blackwell sm_120, PyTorch cu130)
* **엔진**: HuggingFace Diffusers 0.40.0 + Realistic Vision + IP-Adapter Face
* **동작 방식**: 
  1. 씬 5번 주인공 사진에서 얼굴 특징 임베딩을 추출
  2. 디퓨전 교차 주의집중(Cross-Attention)에 얼굴 특징을 주입
  3. 프롬프트("공원 앞 버스 탑승")에 맞춰 그래픽카드가 배경, 버스, 몸, 옷을 바닥부터 100% 새로 렌더링
