# 최신 데이터 수집 후 배포 가이드

이 문서는 로컬에서 최신 데이터를 수집하고, GitHub 푸시를 통해 Vercel 자동 배포까지 진행하는 절차를 정리합니다.

## 전제

- 작업 디렉터리: `/Users/eugene/Downloads/modoo`
- 원격 저장소: `origin/main` (현재 `https://github.com/koreatommy/research.git`)
- Vercel은 Git 연동되어 있어 `main` 푸시 시 자동 배포됨

## 1) 로컬에서 최신 데이터 수집

```bash
cd /Users/eugene/Downloads/modoo
python3 crawl_modoo_all.py
```

- 수집 결과로 `modoo_all_ideas.json`이 갱신됩니다.

## 2) 배포용 데이터 파일 생성

```bash
python3 export_for_research.py
```

- 아래 파일이 최신 상태로 갱신됩니다.
  - `research/data/ideas.json`
  - `research/data/analytics.json`

## 3) 변경사항 확인

```bash
git status
```

- 보통 `research/data/ideas.json`, `research/data/analytics.json` 변경이 보입니다.

## 4) 커밋 및 푸시

```bash
git add research/data/ideas.json research/data/analytics.json
git commit -m "data: 최신 아이디어 데이터 갱신"
git push origin main
```

## 5) 배포 확인

- 푸시 후 1~2분 내 Vercel 자동 배포
- 확인 URL
  - 메인: `https://research-theta-indol.vercel.app`
  - 분석: `https://research-theta-indol.vercel.app/analytics`

## 자주 쓰는 원라인 명령어

```bash
cd /Users/eugene/Downloads/modoo && \
python3 crawl_modoo_all.py && \
python3 export_for_research.py && \
git add research/data/ideas.json research/data/analytics.json && \
git commit -m "data: 최신 아이디어 데이터 갱신" && \
git push origin main
```

## 문제 해결

- `nothing to commit`:
  - 데이터 변경이 없으면 정상입니다. 필요 시 `git status`로 확인하세요.
- `/analytics` 404:
  - 배포 완료 전일 수 있습니다. 잠시 후 새로고침(강력 새로고침)하세요.
- 수집 실패:
  - 네트워크 상태 확인 후 `python3 crawl_modoo_all.py` 재실행.

