#!/bin/bash

# 入力ディレクトリ（$HOMEで書き直し）
INPUT_DIR="$HOME/Downloads/校正サンプル/03_TITLE_OE"
# 現在の日時を取得してディレクトリ名に反映
timestamp=$(date '+%d-%H')
OUTPUT_DIR="./output-$timestamp"
HOT_FILE="M03_hotfile.txt"
mkdir -p "$OUTPUT_DIR"


# ks*.txt をすべて処理
for file in "$INPUT_DIR"/*.txt; do
    filename=$(basename "$file")
    output_file="$OUTPUT_DIR/$filename.html"

    echo "$(date '+%Y-%m-%d %H:%M:%S') Processing $filename → $output_file  hotfile: $HOT_FILE"

    python main_cui.py --input "$file"  --hotfile "$HOT_FILE"  --output "$output_file"
done
