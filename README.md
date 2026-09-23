# Hyundai Motor Group HINT 1기 - SW 보안 및 OTA

현대자동차그룹 HINT 1기 SW 보안 및 OTA 학습용 저장소입니다.

해시, AES 암호화, HTTP 파일 제공, OTA 다운로드, 펌웨어 해시 검증 흐름을 Python으로 실습합니다.

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

## 3. OTA Hash Verify

서버는 파일A와 파일A의 SHA-256 값을 함께 제공합니다.

서버 실행:

```powershell
python .\ota_hash_verify\server_firmware.py
```

제공 URL:

```text
http://192.168.0.60:8001/fileA_firmware.bin
http://192.168.0.60:8001/fileA_firmware.bin.sha256
```

클라이언트 실행:

```powershell
python .\ota_hash_verify\client_verify.py
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
saved: ...\work\device\fileA_firmware.bin
```

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

## 포트 설명

- `192.168.0.60`은 서버 PC의 IP 주소입니다.
- `:8000`, `:8001`은 서버 프로그램이 사용하는 포트 번호입니다.
- `basic_http/test1.py`는 8000번 포트를 사용합니다.
- `ota_hash_verify/server_firmware.py`는 8001번 포트를 사용합니다.
- `http://192.168.0.60/123.txt`처럼 포트를 생략하면 기본 HTTP 포트인 80번으로 접속합니다.
