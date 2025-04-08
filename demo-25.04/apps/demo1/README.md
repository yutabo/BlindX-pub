
# DEMO3

## あらまし

これは BlindX のクライアントアプリのデモです。以下の処理を対話的に行います

- テキスト入力と非同期に推論を実行
- モードレスにリアルタイムでかな漢字変換
- 推論は HTTP を介してリモートマシンで実行
- アプリケーションのフロントエンドに統合

![gif](../screenshots/demo3.gif)


プログラムには以下のものがあります

| file path | description |
| ---- | ---- |
| romhira.py | ローマ字からひらがな変換 | 
| remote_inference.py | T5 推論器のラッパー|
| inference_backend.py | 推論を非同期に実行するためのバックエンド |
| main.py | すべてをあわせたデモプログラム |
| images | ロゴ画像 |


## 動作方法

プログラムを実行するまでの手順を示します。

### 変換サーバを起動する

デモを実行するに先立って別ターミナルでかな漢字変換サーバを起動しておきます。

[demoserver](./demoserver/README.md)


### 環境設定する

仮想環境の下で必要なモジュールをインストールします。単純な venv 仮想環境を使う場合は

```
% cd BlindX/demo3
% python3 -m .venv --prompt .
% source .venv/bin/activate 
% pip install -r requirements.txt
```

ここでは GUI フレームワークとして flet ( https://flet.dev/) を使用します。
flet のインストールは [demo0](./demo0/README.md) を参照ください

### デモを起動してみる

別ウィンドウでかな漢字変換サーバを起動した状態で

```
% chmod +x main.py
% ./main.py
```
または

```
% flet main.py
```
### 操作方法

to be filled later



























