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

## 포트 설명

- `192.168.0.60`은 서버 PC의 IP 주소입니다.
- `:8000`, `:8001`은 서버 프로그램이 사용하는 포트 번호입니다.
- `basic_http/test1.py`는 8000번 포트를 사용합니다.
- `ota_hash_verify/server_firmware.py`는 8001번 포트를 사용합니다.
- `http://192.168.0.60/123.txt`처럼 포트를 생략하면 기본 HTTP 포트인 80번으로 접속합니다.
