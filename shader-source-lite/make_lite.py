#!/usr/bin/env python3
"""軽量版シェーダー(Golden Hour Lite)を、本編の golden_hour.wgsl から作る。
重い処理を、定数で切り、その分岐の中に、重い計算を閉じ込めて、実行時に走らないようにする(GPU の負荷が、大きく下がる)。
  切るもの: 空中の落ち葉・雪(視線に沿った 8〜12 回の繰り返し)/ 水の波紋・水しぶき(3x3 区画の繰り返し)/ 凹凸(微分 + 5 回の画像読み)/ 光の筋(5 回の影の読み)/
            雲の影・木漏れ日・水面の雲・細かいさざ波(ノイズ計算)/ 草の風の明暗。
  残すもの: 色・光・影・金属の質感・水の吸収と反射・空気のかすみ・葉と草のゆれ(頂点のみ、非 strict)。
使い方: python make_lite.py <入力 golden_hour.wgsl> <出力のフォルダ>"""
import os
import re
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert s.count(old) >= 1, "見つからない: " + old[:60]
    s = s.replace(old, new, count)


def const(name, value):
    global s
    m = re.search(r"(const %s: f32 = )([\d.]+)(;)" % re.escape(name), s)
    assert m, name
    s = s[:m.start(2)] + value + s[m.end(2):]


# 1) 定数で、重い機能を切る
for n in ["LEAF_BITS", "SNOW_FALL", "WATER_RINGS", "WATER_SPLASH", "SHAFT", "CLOUD_SHADOW", "DAPPLE", "GUST", "WATER_CLOUDS", "WATER_MICRO", "RELIEF_DEPTH", "CAVITY"]:
    const(n, "0.0")

# 2) 重い計算を、定数の分岐の中へ
sub("fn reliefInfo(light: BloxdLightIn) -> vec4f {\n", "fn reliefInfo(light: BloxdLightIn) -> vec4f {\n    if (RELIEF_DEPTH <= 0.0 && CAVITY <= 0.0) {\n        return vec4f(normalize(light.normal), 0.0);\n    }\n")
sub("fn shafts(light: BloxdLightIn, sun: vec3f, sunColour: vec3f) -> vec3f {\n", "fn shafts(light: BloxdLightIn, sun: vec3f, sunColour: vec3f) -> vec3f {\n    if (SHAFT <= 0.0) {\n        return vec3f(0.0);\n    }\n")
sub("fn rippleField(p: vec2f, t: f32) -> vec3f {\n", "fn rippleField(p: vec2f, t: f32) -> vec3f {\n    if (WATER_RINGS <= 0.0) {\n        return vec3f(0.0);\n    }\n")
sub("    let dappleSpots = smoothstep(0.55, 0.75, vnoise(wp.xz * 0.7 + vec2f(t * 0.25, t * 0.10)));",
    "    var dappleSpots = 0.0;\n    if (DAPPLE > 0.0) {\n        dappleSpots = smoothstep(0.55, 0.75, vnoise(wp.xz * 0.7 + vec2f(t * 0.25, t * 0.10)));\n    }")
sub("    let cloudNoise = fbm(wp.xz * CLOUD_SCALE + vec2f(t * CLOUD_SPEED, t * CLOUD_SPEED * 0.35));",
    "    var cloudNoise = 0.0;\n    if (CLOUD_SHADOW > 0.0) {\n        cloudNoise = fbm(wp.xz * CLOUD_SCALE + vec2f(t * CLOUD_SPEED, t * CLOUD_SPEED * 0.35));\n    }")
sub("    let cl = smoothstep(0.52, 0.80, fbm(cp)) * smoothstep(0.02, 0.25, r.y);",
    "    var cl = 0.0;\n    if (WATER_CLOUDS > 0.0) {\n        cl = smoothstep(0.52, 0.80, fbm(cp)) * smoothstep(0.02, 0.25, r.y);\n    }")
# 細かいさざ波(ノイズ 3 回)
sub("    let m0 = vnoise(q);\n    let mx = vnoise(q + vec2f(e * 5.0, 0.0));\n    let my = vnoise(q + vec2f(0.0, e * 5.0));\n    let micro = vec2f(mx - m0, my - m0) / e * WATER_MICRO * detail;",
    "    var micro = vec2f(0.0);\n    if (WATER_MICRO > 0.0) {\n        let m0 = vnoise(q);\n        let mx = vnoise(q + vec2f(e * 5.0, 0.0));\n        let my = vnoise(q + vec2f(0.0, e * 5.0));\n        micro = vec2f(mx - m0, my - m0) / e * WATER_MICRO * detail;\n    }")
# 水しぶき(泡): 切る
sub("    if (abs(light.normal.y) > 0.5 && eyeDist < 60.0) {\n        let foam", "    if (WATER_RINGS > 0.0 && abs(light.normal.y) > 0.5 && eyeDist < 60.0) {\n        let foam")

s = "// Golden Hour Lite: 軽量版(make_lite.py で、本編から自動生成)。 落ち葉・雪・波紋・凹凸・光の筋・雲の影などを切って、GPU の負荷を下げた。\n" + s
os.makedirs(out, exist_ok=True)
open(os.path.join(out, "golden_hour.wgsl"), "w", encoding="utf-8").write(s)
open(os.path.join(out, "pack.json"), "w", encoding="utf-8").write('{"apiVersion":5,"name":"Golden Hour Lite"}')
print("軽量版を書き出した →", out, len(s) // 1024, "KB")
