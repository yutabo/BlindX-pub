import gradio as gr
import subprocess
from datetime import datetime
from pathlib import Path

# Hotwords保存
def save_hotwords(global_text, local_text, filepath="hotwords.txt"):
    combined = global_text.strip() + "\n" + local_text.strip() + "\n"
    Path(filepath).write_text(combined, encoding="utf-8")

# HTMLリンク生成
def make_html_links(paths):
    links = []
    for p in paths:
        name = Path(p).name
        href = f"/output/{name}"
        links.append(f'<a href="{href}" target="_blank">{name}</a>')
    return "<br>".join(links)

# 実行処理
def run_proofreader_stream(global_text, local_text, files):
    log = ""
    links = []

    if not files:
        log += "❌ 入力ファイルがありません\n"
        yield "", log
        return

    save_hotwords(global_text, local_text)

    output_dir = Path("output_html")
    output_dir.mkdir(exist_ok=True)

    for file in files:
        name = Path(file.name).name
        output_name = name + ".html"
        out_file = output_dir / output_name

        cmd = ["python3", "main_cui.py", "--input", file.name, "--hotfile", "hotwords.txt", "--output", str(out_file)]

        log += f"[{datetime.now().strftime('%H:%M:%S')}] 実行: {' '.join(cmd)}\n"
        yield make_html_links(links), log

        try:
            subprocess.run(cmd, check=True)
            links.append(output_name)
            log += f"✅ 完了: {name}\n"
        except subprocess.CalledProcessError:
            log += f"❌ エラー: {name}\n"

        yield make_html_links(links), log

    if not links:
        log += "⚠️ 出力ファイルが作成されませんでした\n"
        yield "", log

# Gradio UI
with gr.Blocks(css="""
#input-pane .gr-file {
    height: 620px;
    min-height: 620px;
    overflow-y: auto;
}
#output-box {
    border: 1px solid #ccc;
    padding: 10px;
    min-height: 200px;
}
""") as app:
    gr.Markdown("## 📝 校正ツール Web UI")

    with gr.Row():
        start_button = gr.Button("▶ START")
        stop_button = gr.Button("⏸ STOP")
        resume_button = gr.Button("⏵ RESUME")

    with gr.Row():
        global_hotwords = gr.Textbox(label="🌍 Global Hotwords", lines=30, scale=1)
        local_hotwords = gr.Textbox(label="📄 Local Hotwords", lines=30, scale=1)
        input_files = gr.File(label="📂 INPUT", file_types=[".txt", ".h"], file_count="multiple", elem_id="input-pane")
        output_links = gr.HTML(label="📁 出力ファイル", elem_id="output-box")

    log_text = gr.Textbox(label="ログ", lines=10, interactive=False)

    start_button.click(
        fn=run_proofreader_stream,
        inputs=[global_hotwords, local_hotwords, input_files],
        outputs=[output_links, log_text]
    )

    stop_button.click(
        lambda: ("", "⏹ STOPボタンが押されました（未実装）"),
        inputs=[],
        outputs=[output_links, log_text]
    )

    resume_button.click(
        lambda: ("", "▶ RESUMEボタンが押されました（未実装）"),
        inputs=[],
        outputs=[output_links, log_text]
    )

# FastAPIに統合
if __name__ == "__main__":
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    import uvicorn

    fastapi_app = FastAPI()
    fastapi_app.mount("/output", StaticFiles(directory="output_html"), name="output")
    gr.mount_gradio_app(fastapi_app, app, path="/")

    uvicorn.run(fastapi_app, host="0.0.0.0", port=7860)