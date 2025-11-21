import os
import sys
import json
import re
import google.generativeai as genai

# 環境変数チェック
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Error: API Key not found")
    sys.exit(1)

genai.configure(api_key=API_KEY)

def process_site_update(base_html, user_instruction):
    # モデル設定（最新のFlashを使用）
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # プロンプト：JSON形式でファイル名とコードを返させる
    prompt = f"""
    あなたはWebサイト管理AIです。
    ユーザーの指示に基づき、既存ページの修正、または新規ページの作成を行ってください。
    
    # 重要なルール
    1. 出力は必ず **JSON形式のみ** にしてください。
    2. キーは "filename" と "html" の2つです。
    3. 新規作成の場合、既存のHTML（index.html）のデザイン（ヘッダー、フッター、CSS読み込みなど）を継承してください。
    4. 既存ページの修正の場合、filenameは既存のもの（例: index.html）を指定してください。

    # JSONの出力例
    {{
      "filename": "about.html",
      "html": "<!DOCTYPE html>..."
    }}

    # 既存のデザイン（参考用 index.html）
    {base_html}

    # ユーザーの指示
    {user_instruction}
    """
    
    try:
        # JSONモードを意識させる（modelによっては response_mime_type='application/json' が使えるが、汎用的にテキストで受ける）
        response = model.generate_content(prompt)
        text = response.text
        
        # Markdownの ```json ... ``` を除去して純粋なJSONにする処理
        clean_text = re.sub(r"```json|```", "", text).strip()
        
        # JSONとして解析
        data = json.loads(clean_text)
        return data

    except Exception as e:
        print(f"AI Error: {e}")
        print(f"Raw response: {text}") # デバッグ用
        return None

if __name__ == "__main__":
    # GitHub Issuesの本文を引数として受け取る
    if len(sys.argv) > 1:
        instruction = sys.argv[1]
    else:
        print("No instruction provided")
        sys.exit(1)

    # デザインの参考にするために index.html を読む
    # (index.htmlが無い場合は空文字にする)
    base_file = "index.html"
    base_content = ""
    if os.path.exists(base_file):
        with open(base_file, "r", encoding="utf-8") as f:
            base_content = f.read()

    # AI処理実行
    result = process_site_update(base_content, instruction)

    if result and "filename" in result and "html" in result:
        target_filename = result["filename"]
        new_html = result["html"]
        
        # ファイル書き込み（新規作成 または 上書き）
        with open(target_filename, "w", encoding="utf-8") as f:
            f.write(new_html)
            
        print(f"SUCCESS: {target_filename} has been generated/updated.")
    else:
        print("FAILED: Could not parse AI response.")
        sys.exit(1)