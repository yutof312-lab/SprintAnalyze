import streamlit as st
import time
import os
import pandas as pd
from google import genai
from google.genai import types

# ページの設定
st.set_page_config(
    page_title="SprintAnalyze - わかりやすいAI短距離走分析",
    page_icon="🏃‍♂️",
    layout="wide"
)

# タイトル
st.title("🏃‍♂️ スプリント分析")
st.subheader("スポーツ科学の根拠に基づき、あなたの走りをわかりやすく解説")
st.write("動画とベストタイムを入力するだけで、国内外の論文や研究データに基づいた本格的なアドバイスを、誰でも理解できる言葉でフィードバックします。")

# --- APIキーの設定（画像表示プログラムを完全に削除しました） ---
with st.sidebar:
    st.header("🔑 API設定")
    api_key = st.text_input("Gemini API Keyを入力してください:", type="password")
    st.caption("[Google AI Studio](https://google.com) から無料で取得できます。")

# --- メイン処理 ---
if not api_key:
    st.warning("左側のサイドバーからGemini API Key（AIzaSy...から始まる鍵）を入力してください。")
else:
    # クライアントの初期化
    client = genai.Client(api_key=api_key)

    # 画面を2カラムに分割
    col1, col2 = st.columns(2)

    with col1:
        st.header("📹 動画と走者情報の入力")
        
        # 100mベストタイム入力欄
        st.subheader("🏃‍♂️ ランナープロフィール")
        c1, c2 = st.columns(2)
        with c1:
            best_time = st.number_input("現在の100mベストタイム（秒）", min_value=9.00, max_value=20.00, value=12.50, step=0.01, format="%.2f")
        with c2:
            target_time = st.number_input("目標とする100mタイム（秒）", min_value=9.00, max_value=20.00, value=11.90, step=0.01, format="%.2f")

        # 再生スピードのヒント設定
        st.subheader("📹 動画の設定")
        playback_speed = st.selectbox(
            "動画のチェック再生速度（目安）",
            ["1.0x (通常スピード)", "0.5x (ハーフスロー)", "0.25x (スーパースロー)"],
            help="AIへスローモーションに基づいた正確なコマ送り分析を指示するために使用します。"
        )

        uploaded_file = st.file_uploader(
            "短距離走の動画ファイルを選択してください (mp4, mov, avi)", 
            type=["mp4", "mov", "avi"]
        )

        # 動画に関する説明文を入力するエリア
        video_description = st.text_area(
            "📝 この動画についての説明や、気になる点があれば教えてください（任意）",
            placeholder="例：スタートから10mの加速局面です。前傾姿勢がうまくキープできているか見てほしいです。",
        )

        if uploaded_file:
            st.video(uploaded_file)
            st.caption("💡 動画プレイヤー右下のメニューから、実際の再生速度をスローに変更して確認できます。")
            
            # 分析ボタン
            analyze_button = st.button("フォームを分析する 🚀", type="primary")

    with col2:
        st.header("📊 分析レポート")
        
        if uploaded_file and analyze_button:
            st.subheader("⏱️ タイムギャップ分析")
            
            # グラフ用のデータを作成
            time_diff = best_time - target_time
            chart_data = pd.DataFrame(
                [best_time, target_time],
                index=["現在のベスト", "目標タイム"],
                columns=["100mタイム (秒)"]
            )
            st.bar_chart(chart_data)
            
            # 表を表示
            metrics_data = {
                "項目": ["現在のベストタイム", "目標タイム", "短縮に必要なタイム"],
                "タイム (秒)": [f"{best_time:.2f}秒", f"{target_time:.2f}秒", f"{time_diff:.2f}秒"],
                "求められるアプローチ": [
                    "現在の走りのベースラインです。",
                    "達成に向けてフォームのさらなる最適化が必要です。",
                    f"目標達成まであと {time_diff:.2f}秒 です。短縮のための伸び代をAIが以下で詳しく解説します。"
                ]
            }
            df = pd.DataFrame(metrics_data)
            st.table(df)

            st.divider()

            # 分析中の画面表示（画像表示を完全に削除）
            with st.spinner("AIが動画を解析し、わかりやすい言葉で詳細に分析しています..."):
                try:
                    # 動画データを処理
                    st.text("1/2: 動画データを処理中...")
                    video_bytes = uploaded_file.read()
                    
                    # MIMEタイプの判定
                    mime_type = "video/mp4"
                    if uploaded_file.name.endswith(".mov"):
                        mime_type = "video/quicktime"
                    elif uploaded_file.name.endswith(".avi"):
                        mime_type = "video/x-msvideo"

                    video_part = types.Part.from_bytes(
                        data=video_bytes,
                        mime_type=mime_type
                    )

                    # 3. プロンプトの作成
                    st.text("2/2: わかりやすさを重視してフォームを詳細に分析中...")
                    prompt = f"あなたはスポーツ科学の知見を持つ一流の陸上短距離コーチです。現在のベストタイムは {best_time} 秒、目標タイムは {target_time} 秒、ユーザーからの相談内容は「 {video_description} 」です。アップロードされた動画を分析し、国内外の大学の研究や論文の知見を根拠として交えながら、中学生でもわかる言葉で『総合評価とロードマップ』『良いところ』『改善が必要なところ（動画の具体的な秒数を指定すること）』『明日からできる改善ドリル』をマークダウン形式で詳しくフィードバックしてください。"

                    # 4. 最新のモデルを呼び出して推論
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=[video_part, prompt]
                    )

                    # AIの分析結果の表示
                    st.success("AI의 フォーム分析が完了しました！")
                    st.markdown(response.text)

                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")
        
        elif uploaded_file:
            st.info("「フォームを分析する」ボタンを押すと、ここにグラフ・表とAI分析結果が表示されます。")
        else:
            st.info("動画をアップロードしてください。")
