# 何のリポジトリ？
古川研究室で皆が共通して用いるライブラリを共有するためのリポジトリ．

# ディレクトリ構成

```
.
├── libs                    # ライブラリの置き場
│   ├── datasets            # データセットの生成・または読み込みを行うライブラリ
│   ├── models              # SOMなどの学習アルゴリズムのクラス置き場
│   └── visualization       # 描画用のライブラリ
├── tests                   # 開発した学習アルゴリズムが正しく動作するかどうかチェックするための実行ファイル置き場．
│                           # ペアプロの実行ファイルはここに該当する．
└── tutorials               # アルゴリズムのチュートリアルを実行するファイル置き場
```

# 使い方

## ライブラリをユーザーとして使うとき
gitの**submodule**機能を用いて自分のリポジトリにflibを1つのディレクトリとして導入してください．
submoduleは簡単に言うとリポジトリの中にリポジトリを入れる機能です．これを使うと以下のようなことができます
- 自分の研究プロジェクトのリポジトリ内に1つのフォルダとしてflibを入れることができる（つまり自分のリポジトリからflibにあるライブラリを利用できる）
- リモートのflibでプッシュがあるとそれをフェッチしてマージできる（もちろんそれをしないことも可能）

ネット上ではコマンドラインからの導入の解説がほどんどですが，ある程度source treeで管理することもできます．

詳しくは以下をチェックしてください．  
[Git submodule の基礎 - Qiita](https://qiita.com/sotarok/items/0d525e568a6088f6f6bb)  
[Git submoduleの押さえておきたい理解ポイントのまとめ - Qiita](https://qiita.com/kinpira/items/3309eb2e5a9a422199e9)
## 機能を追加するとき
編集中…
