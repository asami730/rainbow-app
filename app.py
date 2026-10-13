from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)
DB_NAME = "rainbow.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 画像データ（Base64）を保存するテーブル
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rainbow_gallery (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            image_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ホーム画面（ギャラリーと描画画面を一緒に表示）
@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # 最新の作品から最大10個まで取得
    cursor.execute('SELECT image_data FROM rainbow_gallery ORDER BY id DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()
    
    # 取得した画像をリストにする
    images = [row[0] for row in rows]
    return render_template('index.html', images=images)

# 作品を保存するAPI
@app.route('/save_artwork', methods=['POST'])
def save_artwork():
    data = request.json
    image_data = data.get('image_data')

    if not image_data:
        return jsonify({"status": "error", "message": "画像データがありません"}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # データを保存
    cursor.execute('INSERT INTO rainbow_gallery (image_data) VALUES (?)', (image_data,))
    
    # 古いデータ（10個を超えた分）を削除する処理
    cursor.execute('''
        DELETE FROM rainbow_gallery WHERE id NOT IN (
            SELECT id FROM rainbow_gallery ORDER BY id DESC LIMIT 10
        )
    ''')
    
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)