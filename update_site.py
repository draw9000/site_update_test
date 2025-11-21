import os
import sys
import google.generativeai as genai

# GitHub Actionsの環境変数からキーを取得
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("Error: API Keyが見つかりません")
    sys.exit(1)

genai.configure(api_key=API_KEY)

def process_html_update(html_content, user_instruction):
    # ▼▼▼ ここを修正しました！リストにあった最新モデルを指定 ▼▼▼
    model_name = 'gemini-2.5-flash'
    
    print(f"Using model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        あなたはWeb開発者です。以下のHTMLを指示に従って修正し、修正後のHTMLのみ出力してください。
        Markdown記法は不要です。
        
        ### 指示
        {user_instruction}
    
        ### 現在のHTML
        {html_content}
        """
        
        response = model.generate_content(prompt)
        return response.text.replace("```html", "").replace("```", "").strip()
        
    except Exception as e:
        print(f"Error generating content: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        instruction = sys.argv[1]
    else:
        print("指示がありません")
        sys.exit(1)

    target_file = "index.html"
    
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            original = f.read()
        
        updated = process_html_update(original, instruction)
        
        if updated:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(updated)
            print("Update Success")
        else:
            sys.exit(1)
    else:
        print("File not found")
        sys.exit(1)