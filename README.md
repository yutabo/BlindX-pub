# BlindX Show Case Installation and Execution

ここではサンプルプログラムの実行方法を説明します。

## フォルダ構成
フォルダは以下の構成をとります。
```
BlindX-pub
├── demo-25.04
│   ├── apps			クライアントアプリケーション
│   │   ├── app0		アプリ #0
│   │   ├── app1		アプリ #1
│   │   ├── app2		アプリ #2
│   │   ├── demo0		デモ #0 (under construction)
│   │   ├── demo1		デモ #1
│   │   └── requirements.txt
│   ├── assets			サンプルデータ
│   │   ├── config.txt		サーバアドレスとキー
│   │   ├── images
│   │   └── samples
│   ├── blindx			ライブラリ
│   └── servers			サーバスタブ
├── README.md			このファイル
└── screenshots			デモビデオ
```

## 必要なパッケージのインストール

### python

python 3.12.x をご使用ください。

[download python](https://www.python.org/downloads/)


## 設定ファイルの修正

[demo-25.04/assets/config.txt](./demo-25.04/assets/config.txt) を開き URI とキーを設定します。
スペースは空けずに設定してください。

~~~
% vi demo-25.04/assets/config.txt
inference_server_uri=wss://finer-charmed-dassie.ngrok-free.app
api_key=[ここにキーを書き込みます]
~~~

パーサについては [demo-25.04/blindx/misc.py](./demo-25.04/blindx/misc.py) を参照ください


## ビルドと実行

### 仮想環境の構築

仮想環境を構築します。venv を使用した場合は以下のようになります。

```
% cd demo-25.04/apps
% python3 -m venv --prompt apps .venv
% source .venv/bin/activate
% pip install -r requirement.txt
```
### fletについて
ここではプログラムの UI として flet を使用しています。
[以下の公式サイト](https://flet.dev/docs/) の通りインストールください。

なお、ubuntu 環境で、flet インストールの際に、

```
libmpv.so.1: cannot open shared object file: No such file or directory
```
とエラーが出る場合は 以下の手順で libmpv-dev をインストールしてみてください。

[flet-dev - libmpv.so.1 not found- fixable but hacky #2823](https://github.com/flet-dev/flet/issues/2823)

### プログラムの実行

同じフォルダでプログラムを実行します。

スタンドアロンのアプリとして実行する場合は

```
% flet app0 # app0
% flet app1 # app1
% flet app2 # app2
```

直接 python を実行することもできます。

```
% (cd app0; python main.py)
```

flet 経由の場合はホットリロードが使えます。詳細は以下をご覧ください

https://flet.dev/docs/reference/cli/run/

それぞれのショーケースの詳細はこちらを参照ください。

[BlindX Compare](./demo-25.04/apps/app0/README.md)

[BlindX Chat](./demo-25.04/apps/app1/README.md)

[BlindX Report](./demo-25.04/apps/app2/README.md)


### プログラムの異常終了

ubuntu でまれに flet の異常終了の際にバックエンド終了せずに残る場合があります。
その場合は

```
% ps aux | grep 'app0\/main.py' | awk '{ print $2}'
% ps aux | grep 'app1\/main.py' | awk '{ print $2}'
% ps aux | grep 'app2\/main.py' | awk '{ print $2}'
```

のように終了していないプロセスを削除してください


### 開発用アカウント

- 開発用サーバアドレスとキーはお問い合わせください。[こちら](https://axtechcare.com/company/contact-blindx/)
- 輻輳を避けるために非常に大きいトラフィックには上限が設けられます。
- また、URLとAPIキーは定期的に変更される可能性があります。その都度ご連絡いたします。
- あくまで開発・評価用としてご利用ください。実プロダクトへの利用に対しては、別途お問い合わせください。


