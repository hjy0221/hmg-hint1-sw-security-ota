# Hyundai Motor Group HINT 1기 - SW 보안 및 OTA

[日本語](README.ja.md) · [English](README.md) · [한국어](README.ko.md)

Hyundai Motor Group HINT 1st SW security and OTA learning repository.

Practice hashing, AES encryption, HTTP file serving, OTA download, firmware hash verification, RSA signature verification, and AES decryption flow in Python.

## Folder organization

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

SHA-256 string hash:

```powershell
python .\crypto\hash_sha256.py "hello"
```

SHA-256 file hash:

```powershell
python .\crypto\hash_sha256.py .\sample.bin --file
```

AES-CBC encryption:

```powershell
python .\crypto\aes_encrypt_hex.py "hello"
```

Output:

```text
key_hex: ...
iv_hex: ...
ciphertext_hex: ...
```

Specify the AES key and IV directly:

```powershell
python .\crypto\aes_encrypt_hex.py "hello" --key-hex 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff --iv-hex 0102030405060708090a0b0c0d0e0f10
```

## 2. Basic HTTP

`basic_http/test1.py` serves the `basic_http` folder as an HTTP server.

Run server:

```powershell
python .\basic_http\test1.py
```

Provided files:

```text
http://192.168.0.60:8000/123.txt
```

Client download:

```powershell
python .\basic_http\test2.py
```

Download results:

```text
work/device/153.txt
```

## 3. OTA encryption download, hash verification, decryption

The server encrypts file A with AES-256-CBC and provides a SHA-256 hash of the ciphertext and an RSA-2048 signature.

Algorithm used:

```text
대칭키 암호화: AES-256-CBC
IV: bytes(16), 즉 0x00 16바이트
해시: SHA-256
공개키/개인키: RSA-2048
서명: RSA PKCS#1 v1.5 + SHA-256
```

Run server:

```powershell
python .\ota_hash_verify\server_firmware.py
```

Provided URL:

```text
http://192.168.0.60:8001/fileA_firmware.bin.enc
http://192.168.0.60:8001/fileA_firmware.bin.enc.sha256
http://192.168.0.60:8001/fileA_firmware.bin.enc.sig
http://192.168.0.60:8001/public_key.pem
```

Files sent by the server:

| file | meaning |
| --- | --- |
| `fileA_firmware.bin.enc` | Firmware encrypted with AES-256-CBC |
| `fileA_firmware.bin.enc.sha256` | SHA-256 hash value of encrypted firmware |
| `fileA_firmware.bin.enc.sig` | RSA-2048 signatures for encrypted firmware |
| `public_key.pem` | Public key to use for RSA signature verification |

Run the client:

```powershell
python .\ota_hash_verify\client_verify.py
```

Client behavior:

1. Download encrypted firmware `fileA_firmware.bin.enc`
2. Download server hash `fileA_firmware.bin.enc.sha256`
3. Download RSA Signature `fileA_firmware.bin.enc.sig`
4. Download RSA public key `public_key.pem`
5. Calculate SHA-256 directly from the downloaded ciphertext
6. Compare with the SHA-256 value provided by the server
7. Verify RSA signature with public key
8. Decrypt ciphertext with AES-256-CBC
9. If verification and decryption are successful, save it to `work/device/fileA_firmware.bin`

Client verification criteria:

| steps | Success Conditions | What does failure mean |
| --- | --- | --- |
| SHA-256 hash verification | Server hash and client computed hash are the same | File is corrupted or ciphertext changed during download |
| RSA signature verification | Signature is successfully verified with public key | The file was not created by the server or its signature has been changed |
| AES decryption | Decrypted without padding errors | One of the key, IV, or ciphertext is incorrect |

Success example:

```text
expected: bcd5cc1031c4bb88719149b81bd5d2d90cc4bdd454063b1807e0643f7764f5de
actual:   bcd5cc1031c4bb88719149b81bd5d2d90cc4bdd454063b1807e0643f7764f5de
result: hash ok, rsa signature ok, decrypt ok
encrypted saved: ...\work\device\fileA_firmware.bin.enc
decrypted saved: ...\work\device\fileA_firmware.bin
```

Flow summary:

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

Note: As this is a learning example, the AES key is fixed in the code. In actual OTA systems, symmetric keys are not directly inserted into the code, but a secure key management method and certificate system are used.

## 4. OTA Downloader

Download the firmware by directly specifying the URL.

```powershell
python .\ota_downloader\test.py --url http://192.168.0.64:8080/firmware.bin
```

Specify storage path:

```powershell
python .\ota_downloader\test.py --url http://192.168.0.64:8080/firmware.bin --dest .\work\device\active.bin
```

If your local HTTPS test server uses a self-signed certificate:

```powershell
python .\ota_downloader\test.py --insecure
```

## 5. Chunked OTAs

Create a 100MiB file, divide it into 1MiB chunks, and generate SHA-256 and RSA-2048 signatures for each piece. The transmission section between server/client is encrypted using a TLS socket. The client downloads the pieces sequentially, performing signature verification and hash verification, and finally combining them into a single file to ensure they are identical to the original.

File role:

| file | Role |
| --- | --- |
| `prepare_chunks.py` | Create 100MiB original, 1MiB split, create SHA-256, create RSA signature, create TLS certificate |
| `server_chunks.py` | Running a TLS socket server, sending the manifest/chunk/hash/signature file requested by the client || `client_download_verify.py` | TLS connection, chunk sequential download, RSA signature verification, SHA-256 verification, merge, original identity verification |

Algorithm used:

```text
파일 크기: 100MiB
청크 크기: 1MiB
해시: SHA-256
서명: RSA-2048 PKCS#1 v1.5 + SHA-256
전송 암호화: TLS over TCP socket
```

Summary of execution order:

```powershell
# 1. 준비: 100MiB 원본, 청크, 해시, 서명, TLS 인증서 생성
python .\chunked_ota\prepare_chunks.py

# 2. 서버 실행: 이 터미널은 켜둔 상태로 유지
python .\chunked_ota\server_chunks.py

# 3. 클라이언트 실행: 새 터미널에서 실행
python .\chunked_ota\client_download_verify.py
```

Step 1. Create 100MiB original file, split 1MiB, create hash/signature/TLS certificate:

```powershell
python .\chunked_ota\prepare_chunks.py
```

Created in:

```text
work/chunked_ota/source_100MiB.bin
work/chunked_ota_server/manifest.json
work/chunked_ota_server/chunks/chunk_0000.bin
work/chunked_ota_server/chunks/chunk_0000.bin.sha256
work/chunked_ota_server/chunks/chunk_0000.bin.sha256.sig
work/chunked_ota_server/server_cert.pem
...
```

`server_cert.pem` is a self-signed TLS certificate for learning created using an existing RSA private key.

Step 2. Running a TLS chunk server:

```powershell
python .\chunked_ota\server_chunks.py
```

Server:

```text
localhost:8002
```

This example uses a TCP socket wrapped with TLS rather than HTTP. The client verifies the server certificate by loading `server_cert.pem` as a CA file.

Step 3. Client TLS connection, sequential download, signature verification, hash verification, merge:

```powershell
python .\chunked_ota\client_download_verify.py
```

Client behavior:

1. Connect to the server using a TLS socket
2. Server certificate verification
3. Download `manifest.json`
4. Download RSA public key
5. Download chunks sequentially starting from `chunk_0000.bin`
6. Download `.sha256` of each chunk
7. Download `.sha256.sig` for each chunk
8. Verify `.sha256` signature with public key
9. Directly calculate the SHA-256 of the downloaded chunk and compare it with the `.sha256` value
10. Combine verified chunks in order to create `merged_100MiB.bin`
11. Comparison of merged file SHA-256 and original file SHA-256

Success example:

```text
chunk 0000: tls ok, signature ok, hash ok
...
chunk 0099: tls ok, signature ok, hash ok
expected merged sha256: ...
actual merged sha256:   ...
source compare: identical
result: all chunks verified and merged
```

## Port Description

- `192.168.0.60` in the README is an example server IP address.
- If you run the server and client on the same PC, you can use `localhost`.
- To access the server from another PC, you must use the actual IP address of the server PC instead of `192.168.0.60`.
- `:8000`, `:8001`, `:8002` are the port numbers used by the server program.
- `basic_http/test1.py` uses port 8000.
- `ota_hash_verify/server_firmware.py` uses port 8001.
- `chunked_ota/server_chunks.py` uses port 8002.
- If you omit the port, such as `http://192.168.0.60/123.txt`, the connection is made using the default HTTP port, 80.

Example:

```text
같은 PC에서 접속: http://localhost:8001/fileA_firmware.bin.enc
다른 PC에서 접속: http://<서버_PC_IP>:8001/fileA_firmware.bin.enc
```
