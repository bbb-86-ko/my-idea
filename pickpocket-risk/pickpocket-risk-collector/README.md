# pickpocket-risk fastMCP MVP

로컬 환경에서 fastMCP 기반 MCP 서버와 Agent를 이용해 인터넷에 게시되는 소매치기 위험 장소 정보를 수집·공유하기 위한 최소 기능 제품(MVP)입니다. 빠르게 작동하는 서버·클라이언트 스켈레톤을 제공하며, 기본 도구 구현은 Google News RSS를 활용해 관련 기사에서 위험 장소를 추출하는 예시를 제공합니다.

## 구성 요소

- `mcp_server/server.py`: fastMCP `FastMCP` 서버. `collect_pickpocket_reports` 도구가 Google News RSS에서 소매치기 관련 기사를 검색해 `data/YYYY-MM-DD.jsonl` 파일에 저장합니다. 향후 더 정교한 수집 로직을 이 위치에서 커스터마이즈하세요.
- `agent/run_collector.py`: fastMCP 클라이언트 스크립트. 로컬 서버를 호출해 수집 도구를 실행하고 결과를 확인합니다. `--query` 옵션으로 지역·키워드를 추가할 수 있습니다.
- `data/`: 일별 수집 데이터 디렉터리. `.gitignore` 로 추적에서 제외되어 있습니다.
- `requirements.txt`: 필요한 Python 패키지 목록 (`fastmcp`, `httpx`).

## 준비

1. Python 3.10 이상이 설치되어 있다고 가정합니다.
2. 가상환경 생성 및 의존성 설치:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

   > 네트워크 접근이 제한된 환경이라면, 선행 설치가 가능한 네트워크에서 wheel 파일을 내려받아 오프라인 설치를 진행해야 합니다.

## 서버 실행

fastMCP CLI는 모듈 경로를 받아 로컬 MCP 서버를 실행합니다. 프로젝트 루트(`pickpocket-risk-collector/`)에서 아래 명령을 실행하세요.

> 가상환경을 활성화하면 `fastmcp` 명령이 PATH에 추가됩니다. 가상환경이 비활성화된 상태에서 `fastmcp` 가 보이지 않으면 `source .venv/bin/activate` 로 활성화한 뒤 다시 실행하세요.

```bash
fastmcp run mcp_server/server.py:app
```

원격 접근이 필요하다면 HTTP 전송 모드로 서버를 띄우세요.

```bash
fastmcp run --transport http mcp_server/server.py:app
```

이 모드에서는 기본 접속 URL이 `http://<host>:<port>/mcp` 입니다. 네트워크가 차단되어 있다면 외부 RSS 호출이 실패할 수 있으니 인터넷 연결을 확인하세요.

## 클라이언트 실행

`agent/run_collector.py` 는 fastMCP `Client` 를 활용해 MCP 서버와 직접 상호작용합니다. `--query` 로 추가 키워드를 주면 특정 지역이나 언어에 맞춰 기사를 필터링할 수 있으며, `--server` 옵션으로 원격 MCP 서버(URL, 소켓 경로 등)를 지정할 수 있습니다. HTTP 서버에 연결할 때는 `/mcp` 경로가 포함된 URL을 사용하세요.

```bash
python -m agent.run_collector --query "Seoul pickpocket" --server http://127.0.0.1:8000/mcp
```

스크립트는 도구를 호출하고, 반환된 JSON 사전을 표준 출력으로 표시합니다. 도구 호출이 성공하면 `data/YYYY-MM-DD.jsonl` 파일에 스냅샷이 누적됩니다. 외부 API 호출이 실패하면 에러 정보(JSON)가 출력되며 파일에는 기록되지 않습니다.

## 결과 확인

```bash
cat data/$(date +%F).jsonl
```

파일에는 수집 시각(`timestamp`), 사용된 검색 질의(`query`), 기사별 링크·요약·추정 위치(`guessed_locations`) 등이 JSON 객체로 줄 단위 저장됩니다. 추정 위치는 단순 규칙 기반이므로 후처리나 수동 확인이 필요할 수 있습니다.

## 확장 아이디어

- 데이터 수집 로직 교체: 언론사/커뮤니티 RSS, 오픈데이터 API, 지도 서비스 등을 파싱하여 소매치기 위험 이벤트를 확보.
- 위험도 집계: 수집된 위치 데이터에 가중치를 부여해 일별·주별 위험 지수 산출.
- 알림 연동: Slack/Discord/Webhook 등을 통해 신규 위험 지역이 발견되면 바로 알림 발송.
- 일정 실행: cron, systemd timer, 혹은 워크플로우 매니저를 이용해 매일 자동 실행.
- 데이터 스토리지 교체: 로컬 파일 대신 데이터베이스나 지리 정보 시스템(GIS)으로 전환.
