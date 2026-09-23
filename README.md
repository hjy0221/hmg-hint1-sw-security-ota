# Hyundai Motor Group HINT 1기 - SW 보안 및 OTA

현대자동차그룹 HINT 1기 SW 보안 및 OTA 학습용 저장소입니다.

해시, AES 암호화, HTTP 파일 제공, OTA 다운로드, 펌웨어 해시 검증, RSA 서명 검증, AES 복호화 흐름을 Python으로 실습합니다.

## 폴더 구성

```text
.
├── crypto/
│   ├── hash_sha256.py
│   └── aes_encrypt_hex.py
├── basic_http/
│   ├── 123.txt
│   ├── test1.py
│   └── test2.py
├── ota_hash_verify/
│   ├── server_firmware.py
│   └── client_verify.py
├── ota_downloader/
│   └── test.py
├── chunked_ota/
│   ├── prepare_chunks.py
│   ├── server_chunks.py
│   └── client_download_verify.py
└── work/
```

## 1. Crypto

SHA-256 문자열 해시:

```powershell
python .\crypto\hash_sha256.py "hello"
```

SHA-256 파일 해시:

```powershell
python .\crypto\hash_sha256.py .\sample.bin --file
```

AES-CBC 암호화:

```powershell
python .\crypto\aes_encrypt_hex.py "hello"
```

출력:

```text
key_hex: ...
iv_hex: ...
ciphertext_hex: ...
```

AES 키와 IV를 직접 지정:

```powershell
python .\crypto\aes_encrypt_hex.py "hello" --key-hex 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff --iv-hex 0102030405060708090a0b0c0d0e0f10
```

## 2. Basic HTTP

`basic_http/test1.py`는 `basic_http` 폴더를 HTTP 서버로 제공합니다.

서버 실행:

```powershell
python .\basic_http\test1.py
```

제공 파일:

```text
http://192.168.0.60:8000/123.txt
```

클라이언트 다운로드:

```powershell
python .\basic_http\test2.py
```

다운로드 결과:

```text
work/device/153.txt
```

## 3. OTA 암호화 다운로드, 해시 검증, 복호화

서버는 파일A를 AES-256-CBC로 암호화하고, 암호문에 대한 SHA-256 해시와 RSA-2048 서명을 함께 제공합니다.

사용 알고리즘:

```text
대칭키 암호화: AES-256-CBC
IV: bytes(16), 즉 0x00 16바이트
해시: SHA-256
공개키/개인키: RSA-2048
서명: RSA PKCS#1 v1.5 + SHA-256
```

서버 실행:

```powershell
python .\ota_hash_verify\server_firmware.py
```

제공 URL:

```text
http://192.168.0.60:8001/fileA_firmware.bin.enc
http://192.168.0.60:8001/fileA_firmware.bin.enc.sha256
http://192.168.0.60:8001/fileA_firmware.bin.enc.sig
http://192.168.0.60:8001/public_key.pem
```

서버가 보내는 파일:

| 파일 | 의미 |
| --- | --- |
| `fileA_firmware.bin.enc` | AES-256-CBC로 암호화된 펌웨어 |
| `fileA_firmware.bin.enc.sha256` | 암호화된 펌웨어의 SHA-256 해시값 |
| `fileA_firmware.bin.enc.sig` | 암호화된 펌웨어에 대한 RSA-2048 서명 |
| `public_key.pem` | RSA 서명 검증에 사용할 공개키 |

클라이언트 실행:

```powershell
python .\ota_hash_verify\client_verify.py
```

클라이언트 동작:

1. 암호화된 펌웨어 `fileA_firmware.bin.enc` 다운로드
2. 서버 해시 `fileA_firmware.bin.enc.sha256` 다운로드
3. RSA 서명 `fileA_firmware.bin.enc.sig` 다운로드
4. RSA 공개키 `public_key.pem` 다운로드
5. 다운로드한 암호문을 직접 SHA-256 계산
6. 서버가 제공한 SHA-256 값과 비교
7. 공개키로 RSA 서명 검증
8. AES-256-CBC로 암호문 복호화
9. 검증과 복호화가 성공하면 `work/device/fileA_firmware.bin`에 저장

클라이언트 검증 기준:

| 단계 | 성공 조건 | 실패 시 의미 |
| --- | --- | --- |
| SHA-256 해시 검증 | 서버 해시와 클라이언트 계산 해시가 같음 | 다운로드 중 파일이 깨졌거나 암호문이 변경됨 |
| RSA 서명 검증 | 공개키로 서명이 정상 검증됨 | 서버가 만든 파일이 아니거나 서명이 변경됨 |
| AES 복호화 | 패딩 오류 없이 복호화됨 | 키, IV, 암호문 중 하나가 올바르지 않음 |

성공 예:

```text
expected: bcd5cc1031c4bb88719149b81bd5d2d90cc4bdd454063b1807e0643f7764f5de
actual:   bcd5cc1031c4bb88719149b81bd5d2d90cc4bdd454063b1807e0643f7764f5de
result: hash ok, rsa signature ok, decrypt ok
encrypted saved: ...\work\device\fileA_firmware.bin.enc
decrypted saved: ...\work\device\fileA_firmware.bin
```

흐름 요약:

```text
[서버]
원본 파일A 생성
  -> AES-256-CBC로 암호화
  -> 암호문 SHA-256 계산
  -> 암호문 해시에 RSA-2048 개인키로 서명
  -> 암호문, 해시, 서명, 공개키를 HTTP로 제공

[클라이언트]
암호문 다운로드
  -> SHA-256 재계산 후 서버 해시와 비교
  -> 공개키로 RSA 서명 검증
  -> AES-256-CBC로 복호화
  -> 성공하면 복호화된 파일 저장
```

주의: 학습용 예제라 AES 키가 코드에 고정되어 있습니다. 실제 OTA 시스템에서는 대칭키를 코드에 직접 넣지 않고 안전한 키 관리 방식과 인증서 체계를 사용합니다.

## 4. OTA Downloader

URL을 직접 지정해서 펌웨어를 다운로드합니다.

```powershell
python .\ota_downloader\test.py --url http://192.168.0.64:8080/firmware.bin
```

저장 경로 지정:

```powershell
python .\ota_downloader\test.py --url http://192.168.0.64:8080/firmware.bin --dest .\work\device\active.bin
```

로컬 HTTPS 테스트 서버가 self-signed 인증서를 사용하는 경우:

```powershell
python .\ota_downloader\test.py --insecure
```

## 5. Chunked OTA

100MiB 파일을 만들고, 1MiB 단위로 나눈 뒤 각 조각마다 SHA-256과 RSA-2048 서명을 생성합니다. 서버/클라이언트 사이의 전송 구간은 TLS 소켓으로 암호화합니다. 클라이언트는 조각을 순차적으로 다운로드하면서 서명 검증과 해시 검증을 수행하고, 마지막에 하나의 파일로 합쳐 원본과 동일한지 확인합니다.

파일 역할:

| 파일 | 역할 |
| --- | --- |
| `prepare_chunks.py` | 100MiB 원본 생성, 1MiB 분할, SHA-256 생성, RSA 서명 생성, TLS 인증서 생성 |
| `server_chunks.py` | TLS 소켓 서버 실행, 클라이언트가 요청한 manifest/청크/해시/서명 파일 전송 |
| `client_download_verify.py` | TLS 접속, 청크 순차 다운로드, RSA 서명 검증, SHA-256 검증, 병합, 원본 동일성 확인 |

사용 알고리즘:

```text
파일 크기: 100MiB
청크 크기: 1MiB
해시: SHA-256
서명: RSA-2048 PKCS#1 v1.5 + SHA-256
전송 암호화: TLS over TCP socket
```

실행 순서 요약:

```powershell
# 1. 준비: 100MiB 원본, 청크, 해시, 서명, TLS 인증서 생성
python .\chunked_ota\prepare_chunks.py

# 2. 서버 실행: 이 터미널은 켜둔 상태로 유지
python .\chunked_ota\server_chunks.py

# 3. 클라이언트 실행: 새 터미널에서 실행
python .\chunked_ota\client_download_verify.py
```

1단계. 100MiB 원본 파일 생성, 1MiB 분할, 해시/서명/TLS 인증서 생성:

```powershell
python .\chunked_ota\prepare_chunks.py
```

생성 위치:

```text
work/chunked_ota/source_100MiB.bin
work/chunked_ota_server/manifest.json
work/chunked_ota_server/chunks/chunk_0000.bin
work/chunked_ota_server/chunks/chunk_0000.bin.sha256
work/chunked_ota_server/chunks/chunk_0000.bin.sha256.sig
work/chunked_ota_server/server_cert.pem
...
```

`server_cert.pem`은 기존 RSA 개인키를 활용해 생성한 학습용 self-signed TLS 인증서입니다.

2단계. TLS 청크 서버 실행:

```powershell
python .\chunked_ota\server_chunks.py
```

서버:

```text
localhost:8002
```

이 예제는 HTTP가 아니라 TLS로 감싼 TCP 소켓을 사용합니다. 클라이언트는 `server_cert.pem`을 CA 파일처럼 로드해서 서버 인증서를 검증합니다.

3단계. 클라이언트 TLS 접속, 순차 다운로드, 서명 검증, 해시 검증, 병합:

```powershell
python .\chunked_ota\client_download_verify.py
```

클라이언트 동작:

1. TLS 소켓으로 서버에 접속
2. 서버 인증서 검증
3. `manifest.json` 다운로드
4. RSA 공개키 다운로드
5. 청크를 `chunk_0000.bin`부터 순차 다운로드
6. 각 청크의 `.sha256` 다운로드
7. 각 청크의 `.sha256.sig` 다운로드
8. 공개키로 `.sha256` 서명 검증
9. 다운로드한 청크의 SHA-256을 직접 계산해 `.sha256` 값과 비교
10. 검증된 청크를 순서대로 합쳐 `merged_100MiB.bin` 생성
11. 병합 파일 SHA-256과 원본 파일 SHA-256 비교

성공 예:

```text
chunk 0000: tls ok, signature ok, hash ok
...
chunk 0099: tls ok, signature ok, hash ok
expected merged sha256: ...
actual merged sha256:   ...
source compare: identical
result: all chunks verified and merged
```

## 포트 설명

- README의 `192.168.0.60`은 예시 서버 IP 주소입니다.
- 서버와 클라이언트를 같은 PC에서 실행하면 `localhost`를 사용해도 됩니다.
- 다른 PC에서 서버에 접속하려면 `192.168.0.60` 대신 서버 PC의 실제 IP 주소를 사용해야 합니다.
- `:8000`, `:8001`, `:8002`는 서버 프로그램이 사용하는 포트 번호입니다.
- `basic_http/test1.py`는 8000번 포트를 사용합니다.
- `ota_hash_verify/server_firmware.py`는 8001번 포트를 사용합니다.
- `chunked_ota/server_chunks.py`는 8002번 포트를 사용합니다.
- `http://192.168.0.60/123.txt`처럼 포트를 생략하면 기본 HTTP 포트인 80번으로 접속합니다.

예:

```text
같은 PC에서 접속: http://localhost:8001/fileA_firmware.bin.enc
다른 PC에서 접속: http://<서버_PC_IP>:8001/fileA_firmware.bin.enc
```
