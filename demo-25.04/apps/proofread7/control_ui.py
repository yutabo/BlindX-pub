import gradio as gr
from pathlib import Path
import subprocess
import datetime
import mimetypes

# MIMEの追加（.htmlがリンクで開けるように）
mimetypes.add_type('text/html', '.html')

# ファイルの中身を読み込む関数
def load_hotwords(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""

def save_and_run(global_text, local_text, files):
    # hotwords.txt を保存
    
    hotwords_text = global_text.strip() + "\n" + local_text.strip()
    all_hotwords = list(set(global_text.strip().splitlines() + local_text.strip().splitlines()))
    if not hotwords_text.endswith("\n"):
        hotwords_text += "\n"
    with open("hotwords.txt", "w", encoding="utf-8") as f:
        f.write(hotwords_text)
    
    hotword_path = Path("hotwords.txt")
    hotword_path.write_text("\n".join(all_hotwords), encoding="utf-8")

    output_dir = Path("output_html")
    output_dir.mkdir(exist_ok=True)

    output_files = []
    logs = []

    for file in files:
        input_path = Path(file.name)
        output_path = output_dir / f"{input_path.name}.html"

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cmd = [
            "python3", "main_cui.py",
            "-i", str(input_path),
            "--output", str(output_path),
            "--hotfile", str(hotword_path)
        ]
        logs.append(f"[{timestamp}] 実行: {' '.join(cmd)}")

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            output_files.append(str(output_path))  # ← ここが今回の重要修正点
        else:
            logs.append(f"⚠️ エラー: {result.stderr.strip()}")

    return output_files, "\n".join(logs)


with gr.Blocks(css="""
#input-pane .gr-file {
    height: 620px;
    overflow-y: auto;
}
#output-links-box {
    border: 1px solid #ccc;
    padding: 10px;
    min-height: 620px;
}
""") as app:
    gr.Markdown("## 📝 校正ツール Web UI")

    # hotwords.txt をここで読む
    try:
        hotword_text = Path("hotwords.txt").read_text(encoding="utf-8")
#        print(f"hotwords.txt : {hotword_text}")  # ログファイルや別表示にもしたければここを拡張  
    except Exception:
        hotword_text = f""  # UIに表示させたいなら "" にしておく（ログ出力は別途）
        print(f"hotwords.txt の読み込み失敗: {e}")  # ログファイルや別表示にもしたければここを拡張

    with gr.Row():
        start_button = gr.Button("▶ START")
        stop_button = gr.Button("⏸ STOP")
        resume_button = gr.Button("⏵ 再開")

    with gr.Row():
        with gr.Column(scale=15):
            global_hotwords = gr.Textbox(label="🌍 Global Hotwords", lines=30, interactive=True)
        with gr.Column(scale=15):
            local_hotwords = gr.Textbox(
                label="📄 Local Hotwords",
                lines=30,
                interactive=True,
                value= hotword_text)  # ← ここで読み込む

        with gr.Column(scale=30):
            gr.Markdown("### 📂 INPUT ファイル")
            input_files = gr.File(label="", file_types=[".txt", ".h"], file_count="multiple", elem_id="input-pane")
        with gr.Column(scale=30):
            gr.Markdown("### 📁 出力ファイル（クリックで表示）")
            output_files_display = gr.File(file_types=[".html"], file_count="multiple")

    result_text = gr.Textbox(label="ログ", lines=10, interactive=False)

    start_button.click(
        fn=save_and_run,
        inputs=[global_hotwords, local_hotwords, input_files],
        outputs=[output_files_display, result_text]
    )

app.launch()
