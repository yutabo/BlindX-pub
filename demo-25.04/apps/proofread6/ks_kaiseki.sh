#!/bin/bash

# 入力ディレクトリ（$HOMEで書き直し）
INPUT_DIR="$HOME/Downloads/校正サンプル/02_TITLE_MM"
OUTPUT_DIR="./output"
mkdir -p "$OUTPUT_DIR"

# ks*.txt をすべて処理
for file in "$INPUT_DIR"/ks*.txt; do
    filename=$(basename "$file")
    output_file="$OUTPUT_DIR/$filename.html"

    echo "Processing $filename → $output_file"

    python main_cui.py --input "$file"  --hotwords 棺 夏目 菊池 リョウ みどり マミヤ 湊 オレ 貴方 周防 景人 鮫島聡 --output "$output_file"
done
