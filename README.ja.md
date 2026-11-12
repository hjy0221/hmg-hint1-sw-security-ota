# Hyundai Motor Group HINT 1기 - SW 보안 및 OTA

[日本語](README.ja.md) · [English](README.md) · [한국어](README.ko.md)

現代自動車グループHINT第1期SWセキュリティおよびOTA学習用リポジトリです。

ハッシュ、AES暗号化、HTTPファイル提供、OTAダウンロード、ファームウェアハッシュ検証、RSA署名検証、AES復号化フローをPythonで実践します。

## フォルダの構成

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

SHA-256文字列ハッシュ：

```powershell
python .\crypto\hash_sha256.py "hello"
```

SHA-256ファイルハッシュ：

```powershell
python .\crypto\hash_sha256.py .\sample.bin --file
```

AES-CBC暗号化：

```powershell
python .\crypto\aes_encrypt_hex.py "hello"
```

出力：

```text
key_hex: ...
iv_hex: ...
ciphertext_hex: ...
```

AESキーとIVを直接指定する：

```powershell
python .\crypto\aes_encrypt_hex.py "hello" --key-hex 00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff --iv-hex 0102030405060708090a0b0c0d0e0f10
```

## 2. Basic HTTP

`basic_http/test1.py` は、`basic_http` フォルダーを HTTP サーバーとして提供します。

サーバーの実行：

```powershell
python .\basic_http\test1.py
```

提供ファイル：

```text
http://192.168.0.60:8000/123.txt
```

クライアントのダウンロード：

```powershell
python .\basic_http\test2.py
```

ダウンロード結果：

```text
work/device/153.txt
```

## 3. OTA暗号化ダウンロード、ハッシュ検証、復号化

サーバーはファイルAをAES-256-CBCで暗号化し、暗号文のSHA-256ハッシュとRSA-2048署名を一緒に提供します。

使用アルゴリズム：

```text
대칭키 암호화: AES-256-CBC
IV: bytes(16), 즉 0x00 16바이트
해시: SHA-256
공개키/개인키: RSA-2048
서명: RSA PKCS#1 v1.5 + SHA-256
```

サーバーの実行：

```powershell
python .\ota_hash_verify\server_firmware.py
```

提供URL：

```text
http://192.168.0.60:8001/fileA_firmware.bin.enc
http://192.168.0.60:8001/fileA_firmware.bin.enc.sha256
http://192.168.0.60:8001/fileA_firmware.bin.enc.sig
http://192.168.0.60:8001/public_key.pem
```

サーバーが送信するファイル：

|ファイル|意味|
| --- | --- |
| `fileA_firmware.bin.enc` | AES-256-CBCで暗号化されたファームウェア
| `fileA_firmware.bin.enc.sha256` |暗号化されたファームウェアのSHA-256ハッシュ値
| `fileA_firmware.bin.enc.sig` |暗号化されたファームウェアのRSA-2048署名|
| `public_key.pem` | RSA署名検証に使用する公開鍵|

クライアントの実行：

```powershell
python .\ota_hash_verify\client_verify.py
```

クライアントの動作：

1. 暗号化されたファームウェア `fileA_firmware.bin.enc` ダウンロード
2. サーバーハッシュ `fileA_firmware.bin.enc.sha256` ダウンロード
3. RSA署名`fileA_firmware.bin.enc.sig`のダウンロード
4. RSA公開鍵`public_key.pem`ダウンロード
5. ダウンロードした暗号文を直接SHA-256計算
6. サーバーが提供する SHA-256 値との比較
7. 公開鍵でRSA署名検証
8. AES-256-CBCによる暗号文の復号化
9. 検証と復号化が成功したら`work/device/fileA_firmware.bin`に保存

クライアント検証基準：

|ステップ|成功条件|失敗時の意味
| --- | --- | --- |
| SHA-256ハッシュ検証|サーバーハッシュとクライアント計算ハッシュが等しいダウンロード中にファイルが壊れているか、パスワードが変更されました。
| RSA署名検証|公開鍵で署名が正常に検証されました。サーバーが作成したファイルではないか、署名が変更されました。
| AES復号化|パディングエラーなしで復号化|キー、IV、暗号文のいずれかが正しくありません。

成功例：

```text
expected: bcd5cc1031c4bb88719149b81bd5d2d90cc4bdd454063b1807e0643f7764f5de
actual:   bcd5cc1031c4bb88719149b81bd5d2d90cc4bdd454063b1807e0643f7764f5de
result: hash ok, rsa signature ok, decrypt ok
encrypted saved: ...\work\device\fileA_firmware.bin.enc
decrypted saved: ...\work\device\fileA_firmware.bin
```

フローの概要：

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

注意：学習用の例AESキーはコードに固定されています。実際のOTAシステムでは、対称鍵をコードに直接配置するのではなく、安全な鍵管理スキームと証明書スキームを使用します。

## 4. OTA Downloader

URLを直接指定してファームウェアをダウンロードします。

```powershell
python .\ota_downloader\test.py --url http://192.168.0.64:8080/firmware.bin
```

ストレージパスの指定：

```powershell
python .\ota_downloader\test.py --url http://192.168.0.64:8080/firmware.bin --dest .\work\device\active.bin
```

ローカルHTTPSテストサーバーがself-signed証明書を使用している場合：

```powershell
python .\ota_downloader\test.py --insecure
```

## 5. Chunked OTA

100MiBファイルを作成し、1MiB単位で分割し、各ピースごとにSHA-256およびRSA-2048署名を生成します。サーバー/クライアント間の転送区間はTLSソケットで暗号化されます。クライアントは、フラグメントを順次ダウンロードしながら署名検証とハッシュ検証を実行し、最後に1つのファイルにまとめて元のものと同じであることを確認します。

ファイルの役割：

|ファイル|役割|
| --- | --- |
| `prepare_chunks.py` | 100MiBソース生成、1MiB分割、SHA-256生成、RSA署名生成、TLS証明書生成|
| `server_chunks.py` | TLSソケットサーバーの実行、クライアントが要求したマニフェスト/チャンク/ハッシュ/署名ファイルの転送| `client_download_verify.py` | TLS接続、チャンクシーケンシャルダウンロード、RSA署名検証、SHA-256検証、マージ、元の同一性確認

使用アルゴリズム：

```text
파일 크기: 100MiB
청크 크기: 1MiB
해시: SHA-256
서명: RSA-2048 PKCS#1 v1.5 + SHA-256
전송 암호화: TLS over TCP socket
```

実行順序の要約：

```powershell
# 1. 준비: 100MiB 원본, 청크, 해시, 서명, TLS 인증서 생성
python .\chunked_ota\prepare_chunks.py

# 2. 서버 실행: 이 터미널은 켜둔 상태로 유지
python .\chunked_ota\server_chunks.py

# 3. 클라이언트 실행: 새 터미널에서 실행
python .\chunked_ota\client_download_verify.py
```

ステップ1。 100MiBソースファイルの生成、1MiBの分割、ハッシュ/署名/TLS証明書の生成：

```powershell
python .\chunked_ota\prepare_chunks.py
```

作成場所：

```text
work/chunked_ota/source_100MiB.bin
work/chunked_ota_server/manifest.json
work/chunked_ota_server/chunks/chunk_0000.bin
work/chunked_ota_server/chunks/chunk_0000.bin.sha256
work/chunked_ota_server/chunks/chunk_0000.bin.sha256.sig
work/chunked_ota_server/server_cert.pem
...
```

`server_cert.pem`は、既存のRSA秘密鍵を使用して生成された学習用の自己署名TLS証明書です。

ステップ2。 TLSチャンクサーバーの実行：

```powershell
python .\chunked_ota\server_chunks.py
```

サーバー：

```text
localhost:8002
```

この例では、HTTPではなくTLSで包まれたTCPソケットを使用しています。クライアントは`server_cert.pem`をCAファイルのようにロードしてサーバー証明書を検証します。

ステップ3。クライアントTLS接続、シーケンシャルダウンロード、署名検証、ハッシュ検証、マージ：

```powershell
python .\chunked_ota\client_download_verify.py
```

クライアントの動作：

1. TLSソケットでサーバーに接続する
2. サーバー証明書の検証
3. `manifest.json` ダウンロード
4. RSA公開鍵のダウンロード
5.チャンクを`chunk_0000.bin`から順次ダウンロード
6. 各チャンクの`.sha256`ダウンロード
7. 各チャンクの`.sha256.sig`ダウンロード
8.公開鍵で`.sha256`署名検証
9. ダウンロードしたチャンクのSHA-256を直接計算して`.sha256`値と比較
10. 検証済みチャンクを順番に合わせて `merged_100MiB.bin` を生成
11. マージファイルSHA-256とソースファイルSHA-256の比較

成功例：

```text
chunk 0000: tls ok, signature ok, hash ok
...
chunk 0099: tls ok, signature ok, hash ok
expected merged sha256: ...
actual merged sha256:   ...
source compare: identical
result: all chunks verified and merged
```

## ポートの説明

- README の `192.168.0.60` はサーバの IP アドレスです。
- サーバーとクライアントを同じPCで実行すると、`localhost`を使用してもかまいません。
- 他のPCからサーバーに接続するには、`192.168.0.60`の代わりにサーバーPCの物理IPアドレスを使用する必要があります。
- `:8000`、`:8001`、`:8002` は、サーバープログラムが使用するポート番号です。
- `basic_http/test1.py`は8000番ポートを使用します。
- `ota_hash_verify/server_firmware.py`は8001番ポートを使用します。
- `chunked_ota/server_chunks.py`は8002番ポートを使用します。
- `http://192.168.0.60/123.txt`のようにポートを省略すると、デフォルトのHTTPポートである80番で接続します。

例:

```text
같은 PC에서 접속: http://localhost:8001/fileA_firmware.bin.enc
다른 PC에서 접속: http://<서버_PC_IP>:8001/fileA_firmware.bin.enc
```
