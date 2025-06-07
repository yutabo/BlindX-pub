import gradio as gr
from pathlib import Path
from proofreader import Proofreader
import chardet
import datetime

def load_hotwords(file_path):
    path = Path(file_path)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""

def save_hotwords(text, file_path):
    path = Path(file_path)
    path.write_text(text, encoding="utf-8")

def robust_decode(raw):
    detected = chardet.detect(raw)
    encoding = detected.get("encoding", "utf-8")
    try:
        return raw.decode(encoding)
    except Exception:
        return raw.decode("utf-8", errors="ignore")

def make_html_links(paths):
    links = []
    for p in paths:
        name = Path(p).name
        href = f"/file={p}"
        links.append(f'<a href="{href}" target="_blank">{name}</a>')
    return "<br>".join(links)

def run_proofreader(global_hotwords_text, local_hotwords_text, files):
    if not files:
        return "", "❌ ファイルが選択されていません"

    save_hotwords(global_hotwords_text, "global_hotwords.txt")
    save_hotwords(local_hotwords_text, "local_hotwords.txt")

    global_hotwords = global_hotwords_text.strip().split("\n")
    local_hotwords = local_hotwords_text.strip().split("\n")
    all_hotwords = list(set(global_hotwords + local_hotwords))

    output_files = []
    output_dir = Path("output_html")
    output_dir.mkdir(exist_ok=True)

    logs = []
    for file in files:
        orig_name = getattr(file, "orig_name", file.name)
        filename = Path(orig_name).name + ".html"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"[{timestamp}] ▶ 処理: {orig_name}")

        raw = file.read()
        text = robust_decode(raw)
        pf = Proofreader(hotwords=all_hotwords)
        result = pf.process(text)

        out_path = output_dir / filename
        out_path.write_text(result, encoding="utf-8")
        output_files.append(str(out_path))

    return make_html_links(output_files), "\n".join(logs + [f"✅ {len(output_files)} 件のファイルを処理しました"])

# --- UI 構築 ---
with gr.Blocks(css="""
#output-links-box {
    border: 1px solid #ccc;
    padding: 10px;
    min-height: 620px;
    background-color: #f9f9f9;
}
""") as app:
    gr.Markdown("## 📝 校正ツール Web UI")

    with gr.Row():
        start_button = gr.Button("▶ START")
        stop_button = gr.Button("⏸ STOP")
        resume_button = gr.Button("⏵ 再開")

    with gr.Row():
        global_hotwords = gr.Textbox(
            label="🌍 Global Hotwords (1行1語)",
            lines=30,
            interactive=True,
            scale=1,
            value=load_hotwords("global_hotwords.txt")
        )
        local_hotwords = gr.Textbox(
            label="📄 Local Hotwords (1行1語)",
            lines=30,
            interactive=True,
            scale=1,
            value=load_hotwords("local_hotwords.txt")
        )

    with gr.Row():
        with gr.Column(scale=2):
            gr.Markdown("### 📂 ファイルをドロップ")
            input_files = gr.File(
                label="ここに .txt や .h ファイルをドロップ",
                file_types=[".txt", ".h"],
                file_count="multiple"
            )

        with gr.Column(scale=2):
            gr.Markdown("### 📁 出力ファイル（クリックで表示）")
            output_links = gr.HTML(elem_id="output-links-box")

    result_text = gr.Textbox(label="ログ", lines=10, interactive=False)

    start_button.click(
        fn=run_proofreader,
        inputs=[global_hotwords, local_hotwords, input_files],
        outputs=[output_links, result_text]
    )

app.launch()