# piepy

<a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
<img src="https://img.shields.io/badge/python-3.14%2B-blue" alt="Python: 3.14+">

---

> 디스코드봇 파이

파이썬으로 작성된 편리하고 간결한 기능의 뮤직봇입니다.
핵심 유튜브 스크래핑, 다운로드는
라이브러리 [ydpy](https://github.com/ityeri/ydpy), [yspy](https://github.com/ityeri/yspy) 에 의존합니다

## commands

* `/재생 <url 또는 검색어>`

음악을 바로 재생하거나 다른 음악이 재생중인 경우, 대기열에 추가합니다

* `/나가`

나가

* `/제거`

재생목록에서 음악을 하나 뺍니다. 명령어 사용시 뺄 항목을 선택하는 패널이 표시됩니다

* `/다음`

원하는 특정 음악으로 건너 뜁니다.
명령어 사용시 재생할 음악을 선택할수 있는 패널이 표시되고, 바로 다음 음악으로 가는 옵션을 고를수도 있습니다

## run

빌드 시스템으로 uv 를 사용합니다

```shell
uv run piepy
```

linux, macOS 를 위한 opus 의존성을 포함하는 `flake.nix` 파일을 사용하면 라이브러리 의존성 문제 없이 바로 실행할수 있습니다

```shell
nix run
```

```
docker-compose up -d
```

# TODO

* pannel