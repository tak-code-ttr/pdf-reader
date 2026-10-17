# PDFリーダー

ブラウザで動く PDF 閲覧アプリ。マーカー・ペン・メモで書き込めます。PDF.js を内蔵しているのでオフラインでも動きます。

- Web版（PWA）: https://<ユーザー名>.github.io/pdf-reader/ を開き、iPad/iPhone では「ホーム画面に追加」するとオフラインで起動できます
- ローカル版: `pdf-reader.html` をダウンロードしてブラウザで開きます

PDF はすべて端末内で処理され、どこにも送信されません。注釈はブラウザ内（localStorage）に保存されます。

## 構成

| パス | 内容 |
|---|---|
| `src/pdf-reader.src.html` | アプリ本体（編集するのはここ） |
| `pwa/` | Service Worker・manifest・アイコン |
| `vendor/pdfjs-dist-3.11.174/` | PDF.js（Apache-2.0） |
| `build.py` | PDF.js を埋め込んで `pdf-reader.html` と `docs/`（GitHub Pages 公開用）を生成 |

## 更新手順

```sh
python3 build.py
git add -A && git commit -m "更新内容" && git push
```
