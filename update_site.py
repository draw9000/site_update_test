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
    # 賢いモデルを使用
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    あなたはWebサイト管理AIです。
    ユーザーの指示に基づき、1つまたは複数のファイルの作成・修正を行ってください。
    
    # 重要なルール
    1. 出力は必ず **JSONのリスト形式 ([{{...}}, {{...}}])** にしてください。
    2. 各オブジェクトは "filename" と "html" のキーを持ちます。
    3. 既存ファイル（index.htmlなど）を修正する場合は、そのファイル名を使用してください。
    4. 新規ファイルを作る場合は、既存のデザイン（ヘッダー/フッター/CSS等）を継承してください。
    
    # JSONの出力例
    [
      {{
        "filename": "index.html",
        "html": "..."
      }},
      {{
        "filename": "about.html",
        "html": "..."
      }}
    ]

    # 既存のサイト構造（参考用 index.html）
    {base_html}

    # ユーザーの指示
    {user_instruction}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text
        
        # Markdown記法などを除去
        clean_text = re.sub(r"```json|```", "", text).strip()
        
        # JSONロード
        data = json.loads(clean_text)
        
        # もしAIがリストではなく単体のオブジェクトを返してきた場合、リストに変換してあげる優しさ
        if isinstance(data, dict):
            data = [data]
            
        return data

    except Exception as e:
        print(f"AI Error: {e}")
        # デバッグ用に生データを表示（エラー時のみ）
        # print(f"Raw response: {text}") 
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        instruction = sys.argv[1]
    else:
        print("No instruction provided")
        sys.exit(1)

    # index.html を参考情報として読み込む
    base_file = "index.html"
    base_content = ""
    if os.path.exists(base_file):
        with open(base_file, "r", encoding="utf-8") as f:
            base_content = f.read()

    # AI実行
    results = process_site_update(base_content, instruction)

    if results:
        print(f"🔄 AI returned {len(results)} file(s) to update.")
        
        # ループで全ファイルを書き込み
        for item in results:
            if "filename" in item and "html" in item:
                fname = item["filename"]
                code = item["html"]
                
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(code)
                print(f"✅ SUCCESS: Updated/Created {fname}")
            else:
                print("⚠️ SKIP: Invalid data format in one of the items.")
    else:
        print("❌ FAILED: Could not parse AI response.")
        sys.exit(1)