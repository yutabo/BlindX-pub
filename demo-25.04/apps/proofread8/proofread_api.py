# proofread_api.py
from flask import Flask, request, jsonify
import subprocess
import os
import uuid
from flask import Flask, request, Response

app = Flask(__name__)

@app.route("/")
def index():
    return "main_cui API is alive."

@app.route("/proofread", methods=["POST"])
def run_main_cui():
    # 1. リクエストから入力を取得
    input_text = request.json.get("text", "")
    num_beams = request.json.get("num_beams", 3)

    if not input_text:
        return jsonify({"error": "No input text provided"}), 400

    # 2. 一時ファイル名を作成して保存
    unique_id = str(uuid.uuid4())
    input_path = f"temp_input_{unique_id}.txt"
    output_path = f"output_html/{unique_id}.html"

    with open(input_path, "w", encoding="utf-8") as f:
        f.write(input_text)

    # 3. main_cui.py を実行
    cmd = ["python", "main_cui.py", "-i", input_path, "-o", output_path, "--num_beams", str(num_beams)]
    result = subprocess.run(cmd, capture_output=True, text=True)

    print("=== CMD ===", cmd)
    print("=== STDOUT ===", result.stdout)
    print("=== STDERR ===", result.stderr)

    # 4. 結果HTMLを返す
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        html = "(HTML出力が見つかりませんでした)"

    # 5. 後片付け（任意）
    os.remove(input_path)
    # os.remove(output_path) ← ファイル保存したい場合は消さない

    return Response(html, content_type="text/html; charset=utf-8")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
