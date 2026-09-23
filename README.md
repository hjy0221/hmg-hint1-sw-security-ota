# Hyundai Motor Group HINT 1기 - SW 보안 및 OTA

현대자동차그룹 HINT 1기 SW 보안 및 OTA 학습용 저장소입니다.

## Contents

- `hash_sha256.py`: 문자열 또는 파일의 SHA-256 해시를 hex로 출력
- `aes_encrypt_hex.py`: AES-CBC 방식으로 문자열을 암호화하고 key, IV, ciphertext를 hex로 출력

## Usage

```powershell
python .\hash_sha256.py "hello"
python .\aes_encrypt_hex.py "hello"
```

파일 해시:

```powershell
python .\hash_sha256.py .\sample.bin --file
```

AES 키와 IV를 직접 지정:

```powershell
python .\aes_encrypt_hex.py "hello" --key-hex 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff --iv-hex 0102030405060708090a0b0c0d0e0f10
```
