#!/bin/bash

# 入力ディレクトリ（$HOMEで書き直し）
INPUT_DIR="$HOME/Downloads/校正サンプル/01_TITLE_HS"
OUTPUT_DIR="./output"
mkdir -p "$OUTPUT_DIR"

# ks*.txt をすべて処理
for file in "$INPUT_DIR"/*.h; do
    filename=$(basename "$file")
    output_file="$OUTPUT_DIR/$filename.html"

    echo "Processing $filename → $output_file"

    python main_cui.py --input "$file"  --hotfile "M01_hotwords.txt"  --output "$output_file"
done
