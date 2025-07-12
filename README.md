# Final-Product
# ルート検索アプリ - Route Finder App

このアプリは、Google Maps Directions API を使用して、指定した出発地と目的地の最適ルートを検索・表示するデスクトップアプリケーションです。Tkinter による 
GUI で操作が簡単、地図の昼夜テーマ切替や、HTMLブラウザでの地図表示も可能です。

---

##  主な機能

- 出発地・目的地の入力によるルート検索
- 出発時刻の指定（日時を手動入力）
- 交通手段の選択（車・徒歩・自転車・公共交通）
- 地図テーマ切替（ライト・ダーク）
- 経路のステップバイステップ表示
- 静的地図画像の表示
- ブラウザでの Google Maps 経路表示

---

## 使用技術

- Python 3.x
- Tkinter（GUI）
- Google Maps  API
- Visual Studio Code
- 
---

## 事前準備

1. Google Cloud Console から [APIキー](https://console.cloud.google.com/) を取得してください。
2. Google Maps API  を有効化してください。
3. このスクリプト内の以下の行を、取得したAPIキーに置き換えてください：

```python
API_KEY = "YOUR_API_KEY"  # ← ここにご自身のAPIキーを記述
