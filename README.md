# Hyundai Motor Group HINT 1기 - SW 보안 및 OTA

현대자동차그룹 HINT 1기 SW 보안 및 OTA 학습용 저장소입니다.

이 저장소는 해시, AES 암호화, HTTP 파일 제공, OTA 다운로드, 펌웨어 해시 검증 흐름을 Python으로 실습합니다.

## 파일 구성

| 파일 | 설명 |
| --- | --- |
| `hash_sha256.py` | 문자열 또는 파일의 SHA-256 해시를 hex로 출력 |
| `aes_encrypt_hex.py` | AES-CBC로 문자열을 암호화하고 key, IV, ciphertext를 hex로 출력 |
| `test1.py` | 현재 폴더를 HTTP 서버로 제공 |
| `test2.py` | `test1.py` 서버의 `123.txt`를 다운로드해 저장 |
| `server_firmware.py` | 파일A 펌웨어와 SHA-256 해시 파일을 만들고 HTTP로 제공 |
| `client_verify.py` | 파일A와 해시를 다운로드한 뒤 SHA-256 검증 후 저장 |
| `test.py` | URL을 직접 지정할 수 있는 범용 OTA 다운로드 예제 |
| `123.txt` | HTTP 다운로드 실습용 텍스트 파일 |

## 1. SHA-256 해시

문자열 해시:

```powershell
python .\hash_sha256.py "hello"
```

파일 해시:

```powershell
python .\hash_sha256.py .\sample.bin --file
```

## 2. AES 암호화

랜덤 AES-256 키와 IV를 생성해 암호화:

```powershell
python .\aes_encrypt_hex.py "hello"
```

출력:

```text
key_hex: ...
iv_hex: ...
ciphertext_hex: ...
```

키와 IV를 직접 지정:

```powershell
python .\aes_encrypt_hex.py "hello" --key-hex 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff --iv-hex 0102030405060708090a0b0c0d0e0f10
```

## 3. 단순 HTTP 파일 제공

서버 실행:

```powershell
python .\test1.py
```

서버는 현재 폴더를 HTTP로 제공합니다.

```text
http://192.168.0.60:8000/123.txt
```

클라이언트 다운로드:

```powershell
python .\test2.py
```

다운로드된 파일:

```text
work/device/153.txt
```

## 4. OTA 파일A 다운로드 및 해시 검증

서버는 파일A와 파일A의 SHA-256 값을 함께 제공합니다.

서버 실행:

```powershell
python .\server_firmware.py
```

제공 URL:

```text
http://192.168.0.60:8001/fileA_firmware.bin
http://192.168.0.60:8001/fileA_firmware.bin.sha256
```

클라이언트 실행:

```powershell
python .\client_verify.py
```

클라이언트 동작:

1. `fileA_firmware.bin` 다운로드
2. `fileA_firmware.bin.sha256` 다운로드
3. 다운로드한 파일A를 직접 SHA-256 계산
4. 서버가 제공한 해시와 비교
5. 같으면 `work/device/fileA_firmware.bin`에 저장

성공 예:

```text
expected: 504ef4637a8f11389f601987e8ed9bea1e3ad500e9ea20ea1e0501875b2a8da8
actual:   504ef4637a8f11389f601987e8ed9bea1e3ad500e9ea20ea1e0501875b2a8da8
result: hash ok
saved: work\device\fileA_firmware.bin
```

## 5. 범용 OTA 다운로드

URL을 직접 지정해서 펌웨어를 다운로드:

```powershell
python .\test.py --url http://192.168.0.64:8080/firmware.bin
```

저장 경로 지정:

```powershell
python .\test.py --url http://192.168.0.64:8080/firmware.bin --dest .\work\device\active.bin
```

로컬 HTTPS 테스트 서버가 self-signed 인증서를 사용하는 경우:

```powershell
python .\test.py --insecure
```

## 포트 설명

- `192.168.0.60`은 서버 PC의 IP 주소입니다.
- `:8000`, `:8001`은 서버 프로그램이 사용하는 포트 번호입니다.
- `test1.py`는 8000번 포트, `server_firmware.py`는 8001번 포트를 사용합니다.
- `http://192.168.0.60/123.txt`처럼 포트를 생략하면 기본 HTTP 포트인 80번으로 접속합니다.
