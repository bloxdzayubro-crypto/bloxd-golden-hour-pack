# Golden Hour — Bloxd.io shader & texture pack

Bloxd.io 用の、リアルで立体的なシェーダーパック(WebGPU / apiVersion 5)とテクスチャパック。軽量版つき。**非公式のファンメイド**。

**ダウンロード・見た目・入れ方は、公開ページへ:** (GitHub Pages — `docs/index.html`)

| ファイル(Releases) | 内容 |
|---|---|
| `GoldenHour-Shader.zip` | シェーダー(本編) |
| `GoldenHour-Shader-Lite.zip` | シェーダー(軽量版) |
| `GoldenHour-Textures-64-All.zip` | テクスチャパック全部入り(約 41 MB) |
| `GoldenHour-Textures-Lite.zip` | テクスチャパック軽量版(約 18 MB) |

## ソース
- `shader-source/` … シェーダー本編のソース(`golden_hour.wgsl`)と、調整の記録。 先頭の「調整用の値」で、強さを変えられる。
- `shader-source-lite/` … 軽量版(`make_lite.py` が、本編から自動で作る)。
- `texture-tools/` … テクスチャの生成スクリプトと、UI の CSS(ゲームの取り込みの制限を再現する `pack_css_check.py` つき)。 元の素材(Bloxd の標準テクスチャ・モデル)は、このリポジトリには入れていない。

## 注意
- Bloxd.io とは関係ありません。テクスチャ・モデルは、Bloxd.io の標準のテクスチャ・モデルを元に、加工したものです。権利は、それぞれの権利者に帰属します。権利者からの要請があれば、速やかに、取り下げます。
- 使用は、自己責任で。シェーダーは、シェーダーパックを許可しているゲームでだけ効きます。
