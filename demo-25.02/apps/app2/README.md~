# simpleclient

## あらまし

BlindX のシンプルなクライアントのデモです。以下の処理を対話的に行います

- テキスト入力と非同期に推論を実行
- モードレスにリアルタイムでかな漢字変換
- tkinter (python 標準の GUI) で結果を表示
- 推論はクライアント側でローカルに実行します

![gif](../screenshots/simpleclient.gif)

プログラムには以下のものがあります

| file path | description |
| ---- | ---- |
| romhira.py | ローマ字からひらがな変換 | 
| local_inference.py | T5 推論器のラッパー|
| inference_server.py | 推論を非同期に実行するためのバックエンド |
| test_client.py | すべてをあわせたデモプログラム |
| misc.py | ファイル入出力 |
| settings.json | 設定ファイル |

## デモプログラムの実験法

プログラムを実行するまでの手順を示します

### 環境設定

仮想環境の下で必要なモジュールをインストールします。

```
% cd BlindX/simpleclient
% pip install -r requirements.txt
```
この他、必要であれば、python-tk を apt 経由でインストールしておきます (linux のみ）

```
% sudo apt install python3-tk
```

### モデルデータのダウンロード

モデルファイルは学習内容によっていくつかあります。以下からダウンロードしてディレクトリ直下におきます。

[aozoracc256geo_16_2000000_-5](https://drive.google.com/drive/folders/0AO1DTVxOhUQGUk9PVA)

[aozoracc256geo_16_2000000_-5-20240530T140927Z-001](https://drive.google.com/drive/folders/1-Ck75eXnony7-eeT5nWuXG2z5w1E1rtm?usp=sharing)

あるいはすでに simpledemo フォルダにダウンロードしているものがあれば、同じものが使用できます

```
% ln -s ../simpledemo/aozoracc256geo_16_2000000_-5 .
% ln -s ../simpledemo/aozoracc256geo_16_2000000_-5-20240530T140927Z-001 .
```

### ローマ字をひらがなに変換する 

romhira.py は、フロントエンドを介さず直接文字コードを読み出し、その都度ひらがなへの変換を行います。

```bash
% python3 roomhira.py
    input=ookinanopponofurudokeioziisannnotokei
    result=おおきなのっぽのふるどけいおじいさんのとけい

```

### ひらがなを漢字まじり文に推論する

local_inference.py はローカル（クライアント側）で推論を行います。

```bash
% python3 local_inference.py
(snip)
convert:
    input=おおきなのっぽのふるどけいおじいさんのとけい
    result=大きなのっぽの古時計おじいさんの時計
```

remote_inference.py はリモート（サーバ側）で推論を行います。
動作にあたって settings.json にサーバのアドレスを指定した上で、サーバを起動しておく必要があります。（後述）

```bash
% python3 remote_inference.py
(snip)
convert:
    input=おおきなのっぽのふるどけいおじいさんのとけい
    result=大きなのっぽの古時計おじいさんの時計
```


#### 推論に使用するモデルを変更する

推論のモデルのパスを変更するには直下のディレクトリの settings.json を編集します
settings.json
```json
{
    "Inference": "Local",
    "-Inference": "http://localhost:8000", 
    "Pretrained": "aozoracc256geo_16_2000000_-5",
    "-Pretrained": "aozoracc256geo_32_all_-5-20240614T030558Z-001"
}
```
ここの "Pretrained" エントリに使用するモデルのパスを指定します。
なお json のパーサーは無効な key-value は単に無視するだけなのでキーの先頭に '#' なり '-' なり付加すればコメントアウトできます。

### 推論を非同期に行う

inference_server.py はキー入力と非同期に推論を行います。入力途中の文字列をバックグラウンドで変換し置き換えます。

```bash
% python3 inference.py
...
convert:
    input=じんみんのじ
    result=人民之地
    callback
...
convert:
    input=じんみんのじんみんによるじんみ
    result=人民の人民による人身
    callback
...
convert:
    input=じんみんのじんみんによるじんみんのためのせいじ
    result=人民の人民による人民のための政治
    callback
```


### これらをまとめる 

以上をまとめたテストクライアントを実行します。

```bash
% python3 test_client.py
```
単純なウィンドウが表示され入力されたローマ字列がリアルタイムで変換されます。

 - 入力された文字をローマ字として解釈しひらがな文字列に変換します。
 - どの状態からでも 'q' をタイプしたら終了
 - モードレス。特殊文字はバックスペースとリターンのみ。バックスペースで一文字消去、リターンで改行
 - 現在は半角英数字と混在はできません。（すべて変換される）
 - 翻訳はパラグラフではなく、文単位。ピリオド '.' で変換が確定されます。
 - 現在は再変換では翻訳単位の先頭まで巻き戻されてしまいます。（※要検討）
 - 内部に変換確定後でもひらがな表現は保持されいるので、確定後の文字列も巻き戻って再変換できます。
 - ただしバックスペースしかないので巻き戻ってからの部分修正などはできません（※要検討）


### 変換のレイテンシについて

極端に短い文字列での誤変換を抑制するため、クライアント側である程度の文字数がバッファされています。ここの部分の遅れを差し引いた
推論器自身の裸のレイテンシにつては標準出力の値を参照ください

~~~ bash
convert:
    input=おおきなのっぽのふるどけいおじいさんのとけい
    result=大きなのっぽの古時計おじいさんの時計
    msec=497
~~~

### Update

#### 06/11
- first checkint

#### 06/14
- サーバサイドの推論器追加 (remote_inference.py)
- ファイル名の変更 (inference.py -> local_inference.py)
- settings.json の導入


#### 08/15
- 東京理科大オープンキャンパス版

#### 10/01
- サーバサイドの推論機を demo0 に移した上で廃止
