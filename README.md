pie_py
===
디스코드봇 파이

## build
파이는 빌드시스템으로 poetry 를 사용합니다

```shell
python3 -m pip install --no-cache-dir poetry
poetry build
python3 -m pip install --no-cache-dir dist/*.whl
```

`-m` 옵션을 통해 실행할수 있습니다

```shell
python3 -m pie_py
```

TODO
===
censorship