import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import base64
from pathlib import Path
import time
import re
import os
import hashlib

class HTMLDashboardPublisher:
    """外部HTMLファイルを統合してGitHub Pagesに公開するクラス"""

    def __init__(self, repo_owner: str, repo_name: str, token: str, branch: str = "main"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.token = token
        self.branch = branch
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

    def create_dashboard_index(self, html_files: List[Dict[str, str]], config: Dict, enable_ga: bool = False) -> str:
        """統合ダッシュボードのindex.htmlを生成"""

        # Google Analytics Tag (G-58EZXED4D4)
        google_analytics_tag = """
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-58EZXED4D4"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());

      gtag('config', 'G-58EZXED4D4');
    </script>
""" if enable_ga else ""

        dashboard_items = ""
        for file_info in html_files:
            dashboard_items += f"""
            <div class="dashboard-card" onclick="window.location.href='{file_info['filename']}'">
                <div class="card-icon">{file_info.get('icon', '📊')}</div>
                <div class="card-content">
                    <h3>{file_info['title']}</h3>
                    <p>{file_info.get('description', '')}</p>
                    <span class="update-time">更新: {file_info.get('update_time', '不明')}</span>
                </div>
                <div class="card-arrow">›</div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.get('dashboard_title', 'ダッシュボード')}</title>
    {google_analytics_tag}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif;
            background: #f5f7fa;
            color: #333;
            line-height: 1.6;
        }}

        .header {{
            background: linear-gradient(135deg, {{config.get('primary_color', '#667eea')}} 0%, {{config.get('secondary_color', '#764ba2')}} 100%);
            color: white;
            padding: 60px 20px 40px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}

        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }}

        .dashboard-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            display: flex;
            align-items: center;
            gap: 20px;
            position: relative;
            overflow: hidden;
        }}

        .dashboard-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }}

        .dashboard-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: linear-gradient(135deg, {{config.get('primary_color', '#667eea')}} 0%, {{config.get('secondary_color', '#764ba2')}} 100%);
            transition: width 0.3s ease;
        }}

        .dashboard-card:hover::before {{
            width: 8px;
        }}

        .card-icon {{
            font-size: 3em;
            min-width: 60px;
            text-align: center;
        }}

        .card-content {{
            flex: 1;
        }}

        .card-content h3 {{
            font-size: 1.3em;
            margin-bottom: 8px;
            color: #2d3748;
            font-weight: 600;
        }}

        .card-content p {{
            color: #718096;
            font-size: 0.95em;
            line-height: 1.5;
            margin-bottom: 10px;
        }}

        .update-time {{
            font-size: 0.85em;
            color: #a0aec0;
            display: inline-block;
            background: #f7fafc;
            padding: 4px 10px;
            border-radius: 20px;
        }}

        .card-arrow {{
            font-size: 2em;
            color: #cbd5e0;
            margin-left: 10px;
        }}

        .dashboard-card:hover .card-arrow {{
            color: {{config.get('primary_color', '#667eea')}};
            transform: translateX(5px);
            transition: all 0.3s ease;
        }}

        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}

        .stat-box {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        .stat-box h4 {{
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 5px;
            font-weight: normal;
        }}

        .stat-box .stat-value {{
            font-size: 2em;
            font-weight: 700;
            color: {{config.get('primary_color', '#667eea')}};
        }}

        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: #718096;
            border-top: 1px solid #e2e8f0;
            margin-top: 60px;
        }}

        .footer p {{
            margin-bottom: 10px;
        }}

        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 2em;
            }}

            .dashboard-grid {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}

            .dashboard-card {{
                padding: 20px;
            }}

            .card-icon {{
                font-size: 2.5em;
            }}

            .stats-container {{
                grid-template-columns: 1fr;
            }}
        }}

        /* アニメーション */
        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .dashboard-card {{
            animation: fadeIn 0.5s ease-out;
        }}

        .dashboard-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .dashboard-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .dashboard-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .dashboard-card:nth-child(4) {{ animation-delay: 0.4s; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{config.get('header_icon', '🏥')} {config.get('dashboard_title', 'ダッシュボード')}</h1>
        <p>{config.get('dashboard_subtitle', '統合ダッシュボード')}</p>
    </div>

    <div class="container">
        {f'''
        <div class="stats-container">
            <div class="stat-box">
                <h4>総ダッシュボード数</h4>
                <div class="stat-value">{len(html_files)}</div>
            </div>
            <div class="stat-box">
                <h4>最終更新</h4>
                <div class="stat-value">{datetime.now().strftime('%m/%d')}</div>
            </div>
            <div class="stat-box">
                <h4>ステータス</h4>
                <div class="stat-value">✅</div>
            </div>
        </div>
        ''' if config.get('show_stats', True) else ''}

        <div class="dashboard-grid">
            {dashboard_items}
        </div>
    </div>

    <div class="footer">
        <p>{config.get('footer_text', '© 2025 Dashboard System')}</p>
        <p>最終更新: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    </div>
</body>
</html>"""

        return html_content

    def process_html_file(self, html_content: str, filename: str) -> str:
        """HTMLファイルを処理（レスポンシブ対応、ホームボタン追加など）"""

        # レスポンシブCSS追加
        responsive_css = """
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* レスポンシブ対応 */
            @media (max-width: 768px) {
                body { font-size: 14px; }
                table { font-size: 12px; }
                .container { padding: 10px; }
            }

            /* ホームボタン */
            .home-button {
                position: fixed;
                bottom: 30px;
                right: 30px;
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                text-decoration: none;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: all 0.3s ease;
                z-index: 9999;
                font-size: 1.5em;
            }

            .home-button:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 20px rgba(0,0,0,0.4);
            }

            @media print {
                .home-button { display: none; }
            }
        </style>
        """

        # ホームボタン追加
        home_button = """
        <a href="./index.html" class="home-button" title="ホームに戻る">🏠</a>
        """

        # HTMLの処理
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{responsive_css}</head>')
        else:
            # headタグがない場合は追加
            html_content = f'<head>{responsive_css}</head>' + html_content

        if '</body>' in html_content:
            html_content = html_content.replace('</body>', f'{home_button}</body>')
        else:
            # bodyタグがない場合は追加
            html_content = html_content + f'{home_button}'

        return html_content

    def upload_file(self, content: str, filename: str) -> Tuple[bool, str]:
        """GitHubにファイルをアップロード"""

        try:
            file_path = f"docs/{filename}"
            url = f"{self.base_url}/contents/{file_path}"

            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # 既存ファイルのSHA取得
            response = requests.get(url, headers=headers)
            sha = response.json().get("sha") if response.status_code == 200 else None

            # コンテンツのBase64エンコード
            content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')

            # アップロードデータ
            data = {
                "message": f"Update {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "content": content_encoded,
                "branch": self.branch
            }
            if sha:
                data["sha"] = sha

            # アップロード実行
            response = requests.put(url, json=data, headers=headers)

            if response.status_code in [200, 201]:
                return True, f"Successfully uploaded: {filename}"
            else:
                return False, f"Upload failed: {response.json().get('message', 'Unknown error')}"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_public_url(self) -> str:
        """GitHub PagesのURLを取得"""
        return f"https://{self.repo_owner}.github.io/{self.repo_name}/"

class DashboardMetadataManager:
    """ダッシュボードのメタデータを管理するクラス"""

    def __init__(self):
        self.metadata_template = {
            'button_name': '',
            'short_description': '',
            'long_description': '',
            'icon': '📊',
            'category': '未分類',
            'tags': [],
            'priority': 100,
            'visible': True,
            'update_frequency': '日次',
            'responsible_person': '',
            'data_source': '',
            'last_updated': '',
            'custom_css_class': ''
        }

    def create_metadata_form(self, file_info: Dict, index: int) -> Dict:
        """メタデータ入力フォームを作成"""

        with st.expander(f"📄 {file_info['filename']} の詳細設定", expanded=True):
            col1, col2, col3 = st.columns([2, 2, 1])

            with col1:
                # ボタン名（必須）
                button_name = st.text_input(
                    "ボタン表示名 *",
                    value=file_info.get('title', file_info['filename'].replace('.html', '')),
                    key=f"btn_name_{index}",
                    help="ダッシュボード一覧で表示される名前"
                )

                # 短い説明（必須）
                short_desc = st.text_input(
                    "短い説明 *",
                    value=file_info.get('description', ''),
                    key=f"short_desc_{index}",
                    help="ボタンの下に表示される1行説明"
                )

                # カテゴリ
                category = st.selectbox(
                    "カテゴリ",
                    ["経営分析", "診療実績", "病棟管理", "財務報告", "品質指標", "その他"],
                    key=f"category_{index}"
                )

                # 更新頻度
                update_freq = st.selectbox(
                    "更新頻度",
                    ["リアルタイム", "日次", "週次", "月次", "四半期", "年次", "不定期"],
                    key=f"update_freq_{index}"
                )

            with col2:
                # アイコン選択
                icon = st.selectbox(
                    "アイコン",
                    ["📊", "📈", "📉", "🏥", "🏨", "💊", "🩺", "📋", "📑", "💰", "🎯", "⚡", "🔍", "📅", "🌟"],
                    key=f"icon_{index}"
                )

                # 詳細説明
                long_desc = st.text_area(
                    "詳細説明",
                    value='',
                    key=f"long_desc_{index}",
                    height=100,
                    help="より詳しい説明（オプション）"
                )

                # タグ
                tags_input = st.text_input(
                    "タグ（カンマ区切り）",
                    value='',
                    key=f"tags_{index}",
                    help="検索用のタグ: 例）入院,診療科,月次"
                )

                # データソース
                data_source = st.text_input(
                    "データソース",
                    value='',
                    key=f"data_source_{index}",
                    help="データの出所やシステム名"
                )

            with col3:
                # 優先度
                priority = st.number_input(
                    "表示優先度",
                    min_value=1,
                    max_value=999,
                    value=100,
                    key=f"priority_{index}",
                    help="小さい数字ほど上位表示"
                )

                # 表示/非表示
                visible = st.checkbox(
                    "表示する",
                    value=True,
                    key=f"visible_{index}"
                )

                # 責任者
                responsible = st.text_input(
                    "責任者",
                    value='',
                    key=f"responsible_{index}"
                )

                # カスタムCSS
                css_class = st.text_input(
                    "CSSクラス",
                    value='',
                    key=f"css_class_{index}",
                    help="カスタムスタイル用"
                )

            # プレビュー
            if st.checkbox("プレビュー", key=f"preview_meta_{index}"):
                st.markdown("### カードプレビュー")
                self._render_card_preview(
                    button_name=button_name,
                    short_desc=short_desc,
                    icon=icon,
                    category=category,
                    update_time=datetime.now().strftime('%Y/%m/%d %H:%M')
                )

            # メタデータを返す
            return {
                'filename': file_info['filename'],
                'button_name': button_name,
                'short_description': short_desc,
                'long_description': long_desc,
                'icon': icon,
                'category': category,
                'tags': [tag.strip() for tag in tags_input.split(',') if tag.strip()],
                'priority': priority,
                'visible': visible,
                'update_frequency': update_freq,
                'responsible_person': responsible,
                'data_source': data_source,
                'last_updated': datetime.now().isoformat(),
                'custom_css_class': css_class
            }

    def _render_card_preview(self, button_name: str, short_desc: str,
                           icon: str, category: str, update_time: str):
        """カードのプレビューを表示"""

        preview_html = f"""
        <div style="
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-left: 4px solid #667eea;
            cursor: pointer;
            transition: all 0.3s ease;
            max-width: 400px;
        ">
            <div style="display: flex; align-items: center; gap: 15px;">
                <div style="font-size: 2.5em;">{icon}</div>
                <div style="flex: 1;">
                    <h3 style="margin: 0 0 5px 0; color: #2d3748; font-size: 1.1em;">
                        {button_name}
                    </h3>
                    <p style="margin: 0 0 8px 0; color: #718096; font-size: 0.9em;">
                        {short_desc}
                    </p>
                    <div style="display: flex; gap: 10px; font-size: 0.8em;">
                        <span style="background: #f7fafc; padding: 2px 8px; border-radius: 10px; color: #4a5568;">
                            {category}
                        </span>
                        <span style="color: #a0aec0;">
                            更新: {update_time}
                        </span>
                    </div>
                </div>
                <div style="font-size: 1.5em; color: #cbd5e0;">›</div>
            </div>
        </div>
        """

        st.markdown(preview_html, unsafe_allow_html=True)

class FileNameConflictHandler:
    """ファイル名の競合を処理するクラス"""

    # 予約されたファイル名（システムで使用）
    RESERVED_NAMES = [
        'index.html',
        'index.htm',
        '404.html',
        'robots.txt',
        'sitemap.xml',
        '.htaccess'
    ]

    # 変換ルール
    RENAME_RULES = {
        'index.html': 'main-dashboard.html',
        'index.htm': 'main-dashboard.html',
        'home.html': 'home-dashboard.html',
        'default.html': 'default-dashboard.html'
    }

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """ファイル名をサニタイズ（安全な形式に変換）"""

        # 拡張子を分離
        name, ext = os.path.splitext(filename)

        # 特殊文字を置換
        name = re.sub(r'[<>:"/\\|?*]', '_', name)
        name = re.sub(r'[\s]+', '_', name)  # 空白をアンダースコアに
        name = re.sub(r'[^\w\-_\.]', '', name)  # 英数字、ハイフン、アンダースコア、ドット以外を削除
        name = re.sub(r'_{2,}', '_', name)  # 連続するアンダースコアを1つに

        # 先頭・末尾の特殊文字を削除
        name = name.strip('._-')

        # 空になった場合はデフォルト名
        if not name:
            name = f'file_{hashlib.md5(filename.encode()).hexdigest()[:8]}'

        # 拡張子を戻す
        return f"{name}{ext}"

    @staticmethod
    def check_conflict(filename: str, existing_files: List[str]) -> Tuple[bool, str]:
        """ファイル名の競合をチェック"""

        # 小文字で比較（大文字小文字を区別しないシステム対応）
        filename_lower = filename.lower()

        # 予約名チェック
        if filename_lower in [name.lower() for name in FileNameConflictHandler.RESERVED_NAMES]:
            return True, "システム予約ファイル名"

        # 既存ファイルとの競合チェック
        if filename_lower in [f.lower() for f in existing_files]:
            return True, "既存ファイルと競合"

        return False, ""

    @staticmethod
    def resolve_conflict(filename: str, existing_files: List[str]) -> str:
        """競合を解決して新しいファイル名を生成"""

        # まず変換ルールをチェック
        if filename.lower() in FileNameConflictHandler.RENAME_RULES:
            new_name = FileNameConflictHandler.RENAME_RULES[filename.lower()]
            if new_name.lower() not in [f.lower() for f in existing_files]:
                return new_name

        # 番号付けで解決
        name, ext = os.path.splitext(filename)
        counter = 1

        while True:
            new_filename = f"{name}_{counter}{ext}"
            if new_filename.lower() not in [f.lower() for f in existing_files]:
                return new_filename
            counter += 1

    @staticmethod
    def generate_unique_id(filename: str) -> str:
        """ファイル名からユニークIDを生成"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_part = hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()[:6]
        return f"{timestamp}_{hash_part}"


def create_conflict_aware_uploader():
    """競合処理機能付きのファイルアップローダー"""

    st.header("📤 安全なHTMLアップロード")

    # 既存ファイルリストの管理
    if 'uploaded_files_list' not in st.session_state:
        st.session_state.uploaded_files_list = []

    # 競合ハンドラー
    handler = FileNameConflictHandler()

    # ファイルアップロード
    uploaded_files = st.file_uploader(
        "HTMLファイルを選択（複数可）",
        type=['html', 'htm'],
        accept_multiple_files=True,
        help="index.htmlなどの予約名は自動的にリネームされます"
    )

    if uploaded_files:
        st.info(f"{len(uploaded_files)}個のファイルを処理中...")

        # 処理結果を格納
        processing_results = []

        for file in uploaded_files:
            original_name = file.name

            # ファイル名のサニタイズ
            sanitized_name = handler.sanitize_filename(original_name)

            # 競合チェック
            has_conflict, conflict_reason = handler.check_conflict(
                sanitized_name,
                st.session_state.uploaded_files_list
            )

            if has_conflict:
                # 競合解決
                resolved_name = handler.resolve_conflict(
                    sanitized_name,
                    st.session_state.uploaded_files_list
                )

                processing_results.append({
                    'original': original_name,
                    'sanitized': sanitized_name,
                    'final': resolved_name,
                    'status': 'renamed',
                    'reason': conflict_reason,
                    'file': file
                })
            else:
                processing_results.append({
                    'original': original_name,
                    'sanitized': sanitized_name,
                    'final': sanitized_name,
                    'status': 'ok',
                    'reason': '',
                    'file': file
                })

        # 処理結果の表示
        st.markdown("### 📋 ファイル名処理結果")

        # 問題のあるファイルを先に表示
        renamed_files = [r for r in processing_results if r['status'] == 'renamed']
        ok_files = [r for r in processing_results if r['status'] == 'ok']

        if renamed_files:
            st.warning(f"⚠️ {len(renamed_files)}個のファイルがリネームされます")

            for result in renamed_files:
                with st.expander(f"🔄 {result['original']} → {result['final']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**変更理由:**")
                        st.write(f"- {result['reason']}")
                        if result['original'] != result['sanitized']:
                            st.write(f"- サニタイズ: {result['original']} → {result['sanitized']}")

                    with col2:
                        st.markdown("**最終ファイル名:**")
                        st.code(result['final'])

        if ok_files:
            st.success(f"✅ {len(ok_files)}個のファイルは問題ありません")

            with st.expander("問題のないファイル一覧"):
                for result in ok_files:
                    st.write(f"- {result['final']}")

        # 確認と実行
        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("✅ この内容で処理を続行", type="primary", use_container_width=True):
                # ファイルリストを更新
                for result in processing_results:
                    if result['final'] not in st.session_state.uploaded_files_list:
                        st.session_state.uploaded_files_list.append(result['final'])

                # セッション状態に保存
                st.session_state.processed_files = processing_results
                st.success("ファイル処理が完了しました！")

                # 次のステップへの案内
                st.info("「ダッシュボード管理」タブで各ファイルの詳細設定を行ってください")

        with col2:
            if st.button("❌ キャンセル", use_container_width=True):
                st.info("処理をキャンセルしました")
                st.rerun()


def create_batch_rename_tool():
    """一括リネームツール"""

    st.header("🔄 一括ファイル名変更")

    st.info("""
    外部システムから取得したHTMLファイルの名前を一括で変更できます。
    特に `index.html` などの競合しやすいファイル名を安全な名前に変更します。
    """)

    # リネームルールの設定
    st.subheader("📝 リネームルール設定")

    col1, col2 = st.columns(2)

    with col1:
        prefix = st.text_input(
            "プレフィックス（接頭辞）",
            value="dashboard_",
            help="ファイル名の先頭に追加する文字列"
        )

        suffix = st.text_input(
            "サフィックス（接尾辞）",
            value="",
            help="拡張子の前に追加する文字列"
        )

    with col2:
        naming_pattern = st.selectbox(
            "命名パターン",
            [
                "オリジナル名を保持",
                "連番を付与",
                "日付を付与",
                "ハッシュを付与"
            ]
        )

        replace_index = st.checkbox(
            "index.htmlを自動変換",
            value=True,
            help="index.htmlは必ずmain-dashboard.htmlに変換"
        )

    # テスト用のファイル名リスト
    st.subheader("🧪 リネームテスト")

    test_filenames = st.text_area(
        "テスト用ファイル名（1行に1つ）",
        value="index.html\nhome.html\nreport_2024.html\n診療科別.html\nward-performance.html",
        height=150
    )

    if st.button("🔍 リネーム結果をプレビュー"):
        filenames = [f.strip() for f in test_filenames.split('\n') if f.strip()]

        handler = FileNameConflictHandler()
        results = []

        for i, filename in enumerate(filenames):
            # サニタイズ
            sanitized = handler.sanitize_filename(filename)

            # パターンに応じた変換
            if naming_pattern == "連番を付与":
                name, ext = os.path.splitext(sanitized)
                new_name = f"{prefix}{i+1:03d}_{name}{suffix}{ext}"
            elif naming_pattern == "日付を付与":
                name, ext = os.path.splitext(sanitized)
                date_str = datetime.now().strftime('%Y%m%d')
                new_name = f"{prefix}{date_str}_{name}{suffix}{ext}"
            elif naming_pattern == "ハッシュを付与":
                name, ext = os.path.splitext(sanitized)
                hash_str = hashlib.md5(filename.encode()).hexdigest()[:6]
                new_name = f"{prefix}{name}_{hash_str}{suffix}{ext}"
            else:  # オリジナル名を保持
                name, ext = os.path.splitext(sanitized)
                new_name = f"{prefix}{name}{suffix}{ext}"

            # index.html の特別処理
            if replace_index and filename.lower() == 'index.html':
                new_name = 'main-dashboard.html'

            results.append({
                'original': filename,
                'sanitized': sanitized,
                'final': new_name
            })

        # 結果表示
        st.markdown("### 変換結果")

        # データフレームで表示
        import pandas as pd
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        # 変換ルールのエクスポート
        if st.button("📥 変換ルールをエクスポート"):
            rules = {
                'prefix': prefix,
                'suffix': suffix,
                'pattern': naming_pattern,
                'replace_index': replace_index,
                'mappings': {r['original']: r['final'] for r in results}
            }

            st.download_button(
                "ルールファイルをダウンロード",
                json.dumps(rules, indent=2, ensure_ascii=False),
                file_name=f"rename_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


def add_conflict_handling_to_main_app():
    """メインアプリに競合処理機能を追加"""

    tab1, tab2, tab3 = st.tabs([
        "📤 安全アップロード",
        "🔄 一括リネーム",
        "📋 競合チェッカー"
    ])

    with tab1:
        create_conflict_aware_uploader()

    with tab2:
        create_batch_rename_tool()

    with tab3:
        st.header("🔍 ファイル名競合チェッカー")

        st.info("アップロード前にファイル名の競合をチェックできます")

        # ファイル名入力
        check_filename = st.text_input(
            "チェックしたいファイル名",
            value="index.html",
            help="競合の可能性があるか確認します"
        )

        if st.button("🔍 チェック実行"):
            handler = FileNameConflictHandler()

            # サニタイズ
            sanitized = handler.sanitize_filename(check_filename)

            # 競合チェック
            is_reserved = check_filename.lower() in [n.lower() for n in handler.RESERVED_NAMES]

            # 結果表示
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📊 チェック結果")

                if is_reserved:
                    st.error("❌ システム予約ファイル名です")
                    st.warning("このファイル名は使用できません")
                else:
                    st.success("✅ 使用可能なファイル名です")

                if check_filename != sanitized:
                    st.info(f"サニタイズ後: {sanitized}")

            with col2:
                st.markdown("### 💡 推奨される代替名")

                if is_reserved and check_filename.lower() in handler.RENAME_RULES:
                    st.write(f"• {handler.RENAME_RULES[check_filename.lower()]}")

                # その他の代替案
                name, ext = os.path.splitext(sanitized)
                alternatives = [
                    f"{name}_dashboard{ext}",
                    f"{name}_page{ext}",
                    f"{name}_{datetime.now().strftime('%Y%m%d')}{ext}",
                    f"custom_{name}{ext}"
                ]

                for alt in alternatives:
                    st.write(f"• {alt}")

        # 予約ファイル名一覧
        with st.expander("📋 システム予約ファイル名一覧"):
            for reserved in FileNameConflictHandler.RESERVED_NAMES:
                st.write(f"• {reserved}")

            st.info("""
            これらのファイル名は特別な用途で使用されるため、
            アップロードファイルには使用できません。
            """)

class GitHubConnectionTester:
    """GitHub接続をテストするクラス"""

    @staticmethod
    def test_connection(token: str, repo_name: str) -> Dict:
        """GitHub接続の詳細テスト"""

        results = {
            'connection': False,
            'authentication': False,
            'repository_access': False,
            'write_permission': False,
            'github_pages': False,
            'branch_info': {},
            'rate_limit': {},
            'errors': []
        }

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        try:
            # 1. 認証テスト
            with st.spinner("認証情報を確認中..."):
                auth_response = requests.get(
                    'https://api.github.com/user',
                    headers=headers,
                    timeout=10
                )

                if auth_response.status_code == 200:
                    results['authentication'] = True
                    user_info = auth_response.json()
                    results['user_info'] = {
                        'login': user_info.get('login'),
                        'name': user_info.get('name'),
                        'email': user_info.get('email')
                    }
                else:
                    results['errors'].append(f"認証エラー: {auth_response.status_code}")
                    return results

            # 2. リポジトリアクセステスト
            with st.spinner("リポジトリアクセスを確認中..."):
                repo_url = f"https://api.github.com/repos/{repo_name}"
                repo_response = requests.get(repo_url, headers=headers, timeout=10)

                if repo_response.status_code == 200:
                    results['repository_access'] = True
                    repo_info = repo_response.json()
                    results['repo_info'] = {
                        'name': repo_info.get('full_name'),
                        'private': repo_info.get('private'),
                        'default_branch': repo_info.get('default_branch'),
                        'created_at': repo_info.get('created_at'),
                        'size': repo_info.get('size')
                    }

                    # 書き込み権限チェック
                    permissions = repo_info.get('permissions', {})
                    results['write_permission'] = permissions.get('push', False)
                else:
                    results['errors'].append(f"リポジトリアクセスエラー: {repo_response.status_code}")
                    return results

            # 3. ブランチ情報取得
            with st.spinner("ブランチ情報を取得中..."):
                branches_url = f"{repo_url}/branches"
                branches_response = requests.get(branches_url, headers=headers, timeout=10)

                if branches_response.status_code == 200:
                    branches = branches_response.json()
                    results['branch_info'] = {
                        'count': len(branches),
                        'names': [b['name'] for b in branches]
                    }

            # 4. GitHub Pages状態確認
            with st.spinner("GitHub Pages設定を確認中..."):
                pages_url = f"{repo_url}/pages"
                pages_response = requests.get(pages_url, headers=headers, timeout=10)

                if pages_response.status_code == 200:
                    results['github_pages'] = True
                    pages_info = pages_response.json()
                    results['pages_info'] = {
                        'url': pages_info.get('html_url'),
                        'status': pages_info.get('status'),
                        'source': pages_info.get('source')
                    }
                elif pages_response.status_code == 404:
                    results['github_pages'] = False
                    results['pages_info'] = {'status': '未設定'}

            # 5. APIレート制限確認
            rate_limit_response = requests.get(
                'https://api.github.com/rate_limit',
                headers=headers,
                timeout=10
            )

            if rate_limit_response.status_code == 200:
                rate_data = rate_limit_response.json()
                core_rate = rate_data.get('rate', {})
                results['rate_limit'] = {
                    'limit': core_rate.get('limit'),
                    'remaining': core_rate.get('remaining'),
                    'reset': datetime.fromtimestamp(core_rate.get('reset', 0)).strftime('%Y-%m-%d %H:%M:%S')
                }

            results['connection'] = True

        except requests.exceptions.Timeout:
            results['errors'].append("接続タイムアウト")
        except requests.exceptions.ConnectionError:
            results['errors'].append("ネットワーク接続エラー")
        except Exception as e:
            results['errors'].append(f"予期しないエラー: {str(e)}")

        return results

    @staticmethod
    def display_test_results(results: Dict):
        """テスト結果を見やすく表示"""

        if results['connection']:
            st.success("✅ GitHub接続成功！")

            # 詳細情報の表示
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 👤 認証情報")
                if results['authentication']:
                    user_info = results.get('user_info', {})
                    st.success(f"✓ ユーザー: {user_info.get('login', 'N/A')}")
                    if user_info.get('name'):
                        st.info(f"名前: {user_info['name']}")

                st.markdown("### 📁 リポジトリ情報")
                if results['repository_access']:
                    repo_info = results.get('repo_info', {})
                    st.success(f"✓ {repo_info.get('name', 'N/A')}")
                    st.info(f"ブランチ: {repo_info.get('default_branch', 'N/A')}")

                    if results['write_permission']:
                        st.success("✓ 書き込み権限あり")
                    else:
                        st.error("✗ 書き込み権限なし")

            with col2:
                st.markdown("### 🌐 GitHub Pages")
                if results['github_pages']:
                    pages_info = results.get('pages_info', {})
                    st.success("✓ 有効")
                    if pages_info.get('url'):
                        st.info(f"URL: {pages_info['url']}")
                else:
                    st.warning("⚠️ GitHub Pages未設定")
                    st.caption("公開時に自動設定されます")

                st.markdown("### 📊 API使用状況")
                rate_limit = results.get('rate_limit', {})
                if rate_limit:
                    remaining = rate_limit.get('remaining', 0)
                    limit = rate_limit.get('limit', 0)
                    percentage = (remaining / limit * 100) if limit > 0 else 0

                    st.metric(
                        "残りAPI呼び出し",
                        f"{remaining:,} / {limit:,}",
                        f"{percentage:.1f}%"
                    )
                    st.caption(f"リセット: {rate_limit.get('reset', 'N/A')}")

        else:
            st.error("❌ GitHub接続に失敗しました")

            if results['errors']:
                st.markdown("### エラー詳細")
                for error in results['errors']:
                    st.error(f"• {error}")

            # トラブルシューティング
            with st.expander("🔧 トラブルシューティング"):
                st.markdown("""
                **よくある問題と解決方法:**

                1. **認証エラー (401)**
                   - Personal Access Tokenが正しいか確認
                   - トークンの有効期限を確認
                   - 必要な権限（repo）があるか確認

                2. **リポジトリが見つからない (404)**
                   - リポジトリ名の形式: `username/repository-name`
                   - プライベートリポジトリの場合はrepo権限が必要

                3. **アクセス拒否 (403)**
                   - APIレート制限に達した可能性
                   - トークンの権限不足

                4. **ネットワークエラー**
                   - インターネット接続を確認
                   - ファイアウォール設定を確認
                """)


def create_enhanced_dashboard_app():
    """拡張版ダッシュボード管理アプリ"""

    st.set_page_config(
        page_title="Dashboard Publisher Pro",
        page_icon="🚀",
        layout="wide"
    )

    st.title("🚀 ダッシュボード統合管理システム Pro")

    # デフォルトで表示するダッシュボードの情報を定義
    default_dashboards = [
        {
            'filename': 'https://genie-scripts.github.io/Streamlit-Dashboard/index01/',
            'button_name': '入院分析レポート',
            'short_description': '過去12週間の入院患者数や在院日数のトレンドを分析します。',
            'icon': '🏥',
            'category': '主要レポート',
            'tags': ['manual', 'admission-analysis'],
            'priority': 1,
            'visible': True,
            'update_frequency': '週次',
            'responsible_person': '分析チーム',
            'data_source': 'DWH',
            'last_updated': datetime.now().isoformat(),
            'custom_css_class': ''
        },
        {
            'filename': 'https://genie-scripts.github.io/Streamlit-Dashboard/index02/',
            'button_name': '入院分析レポート', # 同じボタン名でも可
            'short_description': '最新の評価基準に基づいた入院状況の分析レポートです。',
            'icon': '📊',
            'category': '主要レポート',
            'tags': ['manual', 'evaluation-criteria'],
            'priority': 2,
            'visible': True,
            'update_frequency': '週次',
            'responsible_person': '分析チーム',
            'data_source': 'DWH',
            'last_updated': datetime.now().isoformat(),
            'custom_css_class': ''
        }
    ]

    # セッション状態にメタデータリストがなければ、デフォルト値で初期化
    if 'dashboard_metadata' not in st.session_state:
        st.session_state.dashboard_metadata = default_dashboards

    # サイドバー - GitHub設定と接続テスト
    with st.sidebar:
        st.header("⚙️ GitHub設定")

        github_token = st.text_input(
            "Personal Access Token",
            type="password",
            help="repo権限を持つトークン",
            value="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"  # ★変更点: デフォルト値を設定
        )

        repo_name = st.text_input(
            "リポジトリ名",
            value="Genie-Scripts/Streamlit-Dashboard",  # ★変更点: デフォルト値を設定
            help="例: john-doe/dashboard-site"
        )

        # 接続テストボタン（強調表示）
        st.markdown("---")
        if st.button("🔍 GitHub接続テスト", type="primary", use_container_width=True):
            if github_token and repo_name:
                tester = GitHubConnectionTester()

                with st.spinner("接続テスト実行中..."):
                    results = tester.test_connection(github_token, repo_name)

                # 結果を表示
                tester.display_test_results(results)

                # 成功時はセッション状態に保存
                if results['connection'] and results['write_permission']:
                    st.session_state.github_connected = True
                    st.session_state.github_token = github_token
                    st.session_state.repo_name = repo_name
                    st.session_state.connection_results = results
            else:
                st.error("GitHubトークンとリポジトリ名を入力してください")

        # 接続状態の表示
        if st.session_state.get('github_connected'):
            st.success("✅ 接続済み")
            if st.button("🔄 再接続", use_container_width=True):
                st.session_state.github_connected = False
                st.rerun()
        else:
            st.info("👆 接続テストを実行してください")

    # メインエリア
    tab1, tab2, tab3, tab4 = st.tabs([
        "📤 ファイルアップロード",
        "📝 メタデータ設定",
        "👀 プレビュー",
        "🚀 公開"
    ])

    metadata_manager = DashboardMetadataManager()

    with tab1:
        st.header("HTMLファイルアップロード")

        # FileNameConflictHandlerをインスタンス化
        handler = FileNameConflictHandler()

        uploaded_files = st.file_uploader(
            "HTMLファイルを選択",
            type=['html', 'htm'],
            accept_multiple_files=True
        )

        if uploaded_files:
            processed_files = []
            # 既存のファイル名を把握するために空のリストから始める
            existing_filenames = []

            for file in uploaded_files:
                original_name = file.name

                # 1. ファイル名を安全な形式に変換
                sanitized_name = handler.sanitize_filename(original_name)

                # 2. 競合（予約語 or 重複）をチェック
                has_conflict, reason = handler.check_conflict(sanitized_name, existing_filenames)

                if has_conflict:
                    # 3. 競合があれば自動でリネーム
                    final_name = handler.resolve_conflict(sanitized_name, existing_filenames)
                    st.warning(f"ファイル名が競合/予約語のためリネームされました: 「{original_name}」 → 「**{final_name}**」 ({reason})")
                else:
                    final_name = sanitized_name

                # 処理結果を保存
                processed_files.append({
                    'original_filename': original_name,
                    'filename': final_name,  # ★後続処理で使うファイル名
                    'size': f"{file.size / 1024:.1f} KB",
                    'file_object': file
                })
                # 次のファイルのために、確定したファイル名を追加
                existing_filenames.append(final_name)

            # 処理結果をデータフレームで表示
            st.markdown("#### ファイル処理結果")
            df_display = pd.DataFrame([
                {'元ファイル名': r['original_filename'], '公開ファイル名': r['filename']}
                for r in processed_files
            ])
            st.dataframe(df_display, use_container_width=True)

            if st.button("次へ: メタデータ設定", type="primary"):
                # ★リネーム後の情報を含むリストをセッションに保存
                st.session_state.uploaded_files_data = processed_files
                st.session_state.current_tab = "metadata"
                st.rerun()

    with tab2:
        st.header("メタデータ設定")

        if 'uploaded_files_data' not in st.session_state:
            st.warning("まずファイルをアップロードしてください")
        else:
            files_data = st.session_state.uploaded_files_data

            st.info(f"{len(files_data)}個のファイルの詳細情報を設定します")

            # 一括設定
            with st.expander("⚡ 一括設定"):
                col1, col2, col3 = st.columns(3)

                with col1:
                    bulk_category = st.selectbox(
                        "全てのカテゴリ",
                        ["変更しない", "経営分析", "診療実績", "病棟管理", "財務報告", "品質指標", "その他"]
                    )

                with col2:
                    bulk_frequency = st.selectbox(
                        "全ての更新頻度",
                        ["変更しない", "リアルタイム", "日次", "週次", "月次", "四半期", "年次", "不定期"]
                    )

                with col3:
                    bulk_responsible = st.text_input("全ての責任者")

                if st.button("一括適用"):
                    st.success("一括設定を適用しました")

            # 個別設定
            metadata_list = []

            for i, file_info in enumerate(files_data):
                metadata = metadata_manager.create_metadata_form(file_info, i)
                metadata_list.append(metadata)

            # 保存ボタン
            col1, col2 = st.columns(2)

            with col1:
                if st.button("メタデータを保存", type="primary", use_container_width=True):
                    st.session_state.dashboard_metadata = metadata_list
                    st.success("メタデータを保存しました")

                    # JSONエクスポート
                    metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
                    st.download_button(
                        "📥 メタデータをエクスポート",
                        metadata_json,
                        file_name=f"dashboard_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )

            with col2:
                if st.button("次へ: プレビュー", use_container_width=True):
                    st.session_state.current_tab = "preview"
                    st.rerun()

    with tab3:
        st.header("ダッシュボードプレビュー")

        if 'dashboard_metadata' not in st.session_state:
            st.warning("メタデータを設定してください")
        else:
            metadata_list = st.session_state.dashboard_metadata

            # フィルタリング
            col1, col2, col3 = st.columns(3)

            with col1:
                filter_category = st.selectbox(
                    "カテゴリでフィルタ",
                    ["すべて"] + list(set(m['category'] for m in metadata_list))
                )

            with col2:
                sort_by = st.selectbox(
                    "並び順",
                    ["優先度順", "名前順", "更新日順", "カテゴリ順"]
                )

            with col3:
                view_mode = st.radio(
                    "表示モード",
                    ["カード", "リスト", "グリッド"],
                    horizontal=True
                )

            # フィルタリングと並び替え
            filtered_metadata = metadata_list

            if filter_category != "すべて":
                filtered_metadata = [m for m in filtered_metadata if m['category'] == filter_category]

            if sort_by == "優先度順":
                filtered_metadata.sort(key=lambda x: x['priority'])
            elif sort_by == "名前順":
                filtered_metadata.sort(key=lambda x: x['button_name'])
            elif sort_by == "更新日順":
                filtered_metadata.sort(key=lambda x: x['last_updated'], reverse=True)
            elif sort_by == "カテゴリ順":
                filtered_metadata.sort(key=lambda x: x['category'])

            # 表示
            st.markdown(f"### {len(filtered_metadata)}個のダッシュボード")

            if view_mode == "カード":
                # カード表示
                cols = st.columns(3)
                for i, metadata in enumerate(filtered_metadata):
                    with cols[i % 3]:
                        card_html = f"""
                        <div style="
                            background: white;
                            border-radius: 10px;
                            padding: 20px;
                            margin-bottom: 20px;
                            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                            border-left: 4px solid #667eea;
                            height: 200px;
                            display: flex;
                            flex-direction: column;
                        ">
                            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                                <span style="font-size: 2em;">{metadata['icon']}</span>
                                <h4 style="margin: 0; flex: 1;">{metadata['button_name']}</h4>
                            </div>
                            <p style="color: #666; flex: 1;">{metadata['short_description']}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px;">
                                <span style="background: #f0f0f0; padding: 4px 8px; border-radius: 4px; font-size: 0.8em;">
                                    {metadata['category']}
                                </span>
                                <span style="color: #999; font-size: 0.8em;">
                                    {metadata['update_frequency']}
                                </span>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)

            elif view_mode == "リスト":
                # リスト表示
                for metadata in filtered_metadata:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([1, 3, 2, 1])

                        with col1:
                            st.markdown(f"### {metadata['icon']}")

                        with col2:
                            st.markdown(f"**{metadata['button_name']}**")
                            st.caption(metadata['short_description'])

                        with col3:
                            st.caption(f"カテゴリ: {metadata['category']}")
                            st.caption(f"更新: {metadata['update_frequency']}")

                        with col4:
                            st.caption(f"優先度: {metadata['priority']}")

                        st.markdown("---")

            else:  # グリッド表示
                # データフレーム表示
                df_display = pd.DataFrame([
                    {
                        'アイコン': m['icon'],
                        'ボタン名': m['button_name'],
                        '説明': m['short_description'],
                        'カテゴリ': m['category'],
                        '更新頻度': m['update_frequency'],
                        '優先度': m['priority']
                    }
                    for m in filtered_metadata
                ])

                st.dataframe(df_display, use_container_width=True)

    with tab4:
        st.header("GitHub Pages公開")

        if not st.session_state.get('github_connected'):
            st.error("❌ GitHubに接続されていません")
            st.info("サイドバーでGitHub接続テストを実行してください")

        elif 'dashboard_metadata' not in st.session_state:
            st.error("❌ メタデータが設定されていません")

        else:
            st.success("✅ 公開準備完了！")

            # 公開設定
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📊 公開内容")
                metadata_list = st.session_state.dashboard_metadata
                st.metric("ダッシュボード数", len(metadata_list))
                st.metric("カテゴリ数", len(set(m['category'] for m in metadata_list)))

                # 表示されるダッシュボード
                visible_count = sum(1 for m in metadata_list if m['visible'])
                st.metric("表示ダッシュボード", visible_count)

            with col2:
                st.markdown("### ⚙️ 公開オプション")

                branch = st.selectbox(
                    "ブランチ",
                    ["main", "gh-pages", "master"],
                    help="GitHub Pagesで使用するブランチ"
                )

                minify_html = st.checkbox(
                    "HTMLを最小化",
                    value=False,
                    help="ファイルサイズを削減"
                )

                create_sitemap = st.checkbox(
                    "サイトマップ生成",
                    value=True,
                    help="SEO対策用のsitemap.xml"
                )

                enable_analytics = st.checkbox(
                    "アクセス解析",
                    value=True,  # ★変更点: デフォルトでONに
                    help="Google Analytics等の追加"
                )

            st.markdown("---")

            # 公開前の最終確認
            with st.expander("📋 公開前チェックリスト", expanded=True):
                checks = {
                    "GitHub接続": st.session_state.get('github_connected', False),
                    "書き込み権限": st.session_state.get('connection_results', {}).get('write_permission', False),
                    "メタデータ設定": 'dashboard_metadata' in st.session_state,
                    "ファイルアップロード": 'uploaded_files_data' in st.session_state,
                    "必須項目入力": all(m['button_name'] and m['short_description'] for m in metadata_list)
                }

                all_checks_passed = all(checks.values())

                for check_name, check_status in checks.items():
                    if check_status:
                        st.success(f"✅ {check_name}")
                    else:
                        st.error(f"❌ {check_name}")

                if not all_checks_passed:
                    st.warning("全てのチェックをパスしてから公開してください")

            # 公開実行ボタン
            if st.button("🚀 GitHub Pagesに公開", type="primary", use_container_width=True,
                        disabled=not all_checks_passed):

                with st.spinner("公開処理を実行中..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()

                    try:
                        # GitHubパブリッシャーのインスタンス作成
                        publisher = HTMLDashboardPublisher(
                            repo_owner=st.session_state.repo_name.split('/')[0],
                            repo_name=st.session_state.repo_name.split('/')[1],
                            token=st.session_state.github_token,
                            branch=branch
                        )

                        # 1. index.htmlの生成と公開
                        status_text.text("メインページを生成中...")

                        config = {
                            'dashboard_title': '🏥 統合ダッシュボード',
                            'dashboard_subtitle': 'すべてのレポートとダッシュボード',
                            'primary_color': '#667eea',
                            'secondary_color': '#764ba2',
                            'show_stats': True,
                            'footer_text': '© 2025 Dashboard System'
                        }

                        # メタデータをHTML生成用に変換
                        html_files_info = []
                        for metadata in metadata_list:
                            if metadata['visible']:
                                html_files_info.append({
                                    'filename': metadata['filename'],
                                    'title': metadata['button_name'],
                                    'icon': metadata['icon'],
                                    'description': metadata['short_description'],
                                    'update_time': datetime.now().strftime('%Y/%m/%d %H:%M')
                                })

                        # ★変更点: enable_analyticsの値を渡す
                        index_html = publisher.create_dashboard_index(html_files_info, config, enable_ga=enable_analytics)
                        success, message = publisher.upload_file(index_html, "index.html")

                        if not success:
                            st.error(f"メインページの公開に失敗: {message}")
                            return

                        progress_bar.progress(20)

                        # 2. 各HTMLファイルの公開
                        files_data = st.session_state.uploaded_files_data
                        total_files = len(files_data)

                        for i, (file_data, metadata) in enumerate(zip(files_data, metadata_list)):
                            if metadata['visible']:
                                status_text.text(f"ファイルを公開中... ({i+1}/{total_files})")

                                # ファイル内容を読み込み
                                file_obj = file_data['file_object']
                                content = file_obj.read().decode('utf-8')
                                file_obj.seek(0)

                                # HTMLを処理
                                processed_html = publisher.process_html_file(content, metadata['filename'])

                                # メタデータをHTMLに注入
                                meta_injection = f"""
                                <meta name="dashboard-name" content="{metadata['button_name']}">
                                <meta name="dashboard-description" content="{metadata['short_description']}">
                                <meta name="dashboard-category" content="{metadata['category']}">
                                <meta name="dashboard-update-frequency" content="{metadata['update_frequency']}">
                                """

                                if '</head>' in processed_html:
                                    processed_html = processed_html.replace('</head>', f'{meta_injection}</head>')

                                # アップロード
                                success, message = publisher.upload_file(processed_html, metadata['filename'])

                                if not success:
                                    st.warning(f"{metadata['filename']}の公開に失敗: {message}")

                                progress = 20 + int((i + 1) / total_files * 60)
                                progress_bar.progress(progress)

                        # 3. 追加ファイルの生成
                        status_text.text("追加ファイルを生成中...")

                        # サイトマップ生成
                        if create_sitemap:
                            sitemap_content = generate_sitemap(publisher.get_public_url(), html_files_info)
                            publisher.upload_file(sitemap_content, "sitemap.xml")

                        # robots.txt生成
                        robots_content = f"""User-agent: *
Allow: /

Sitemap: {publisher.get_public_url()}sitemap.xml
"""
                        publisher.upload_file(robots_content, "robots.txt")

                        progress_bar.progress(90)

                        # 4. 設定ファイルの保存
                        status_text.text("設定を保存中...")

                        dashboard_config = {
                            'metadata': metadata_list,
                            'config': config,
                            'last_updated': datetime.now().isoformat(),
                            'total_dashboards': len(metadata_list),
                            'visible_dashboards': sum(1 for m in metadata_list if m['visible'])
                        }

                        config_json = json.dumps(dashboard_config, indent=2, ensure_ascii=False)
                        publisher.upload_file(config_json, "dashboard_config.json")

                        progress_bar.progress(100)
                        status_text.text("公開完了！")

                        # 成功メッセージと結果表示
                        public_url = publisher.get_public_url()

                        st.balloons()
                        st.success("🎉 公開が完了しました！")

                        col1, col2 = st.columns(2)

                        with col1:
                            st.info(f"🌐 公開URL: {public_url}")
                            st.markdown(f"[ダッシュボードを開く]({public_url})")

                        with col2:
                            st.metric("公開ファイル数", len([m for m in metadata_list if m['visible']]))
                            st.metric("総容量", f"{sum(float(f['size'].replace(' KB', '')) for f in files_data):.1f} KB")

                        # 公開履歴を保存
                        if 'publish_history' not in st.session_state:
                            st.session_state.publish_history = []

                        st.session_state.publish_history.append({
                            'timestamp': datetime.now().isoformat(),
                            'url': public_url,
                            'dashboards': len([m for m in metadata_list if m['visible']]),
                            'total_size': sum(float(f['size'].replace(' KB', '')) for f in files_data)
                        })

                        # QRコード生成オプション
                        if st.checkbox("QRコードを生成"):
                            import qrcode
                            import io

                            qr = qrcode.QRCode(version=1, box_size=10, border=5)
                            qr.add_data(public_url)
                            qr.make(fit=True)

                            img = qr.make_image(fill_color="black", back_color="white")
                            buf = io.BytesIO()
                            img.save(buf, format='PNG')

                            st.image(buf.getvalue(), width=200)
                            st.caption("スマートフォンでスキャンしてアクセス")

                    except Exception as e:
                        st.error(f"公開中にエラーが発生しました: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())

            # 公開履歴
            if 'publish_history' in st.session_state and st.session_state.publish_history:
                with st.expander("📜 公開履歴"):
                    for history in reversed(st.session_state.publish_history[-5:]):
                        timestamp = datetime.fromisoformat(history['timestamp'])
                        st.write(f"""
                        **{timestamp.strftime('%Y/%m/%d %H:%M:%S')}**
                        URL: {history['url']}
                        ダッシュボード数: {history['dashboards']}
                        総容量: {history['total_size']:.1f} KB
                        """)
                        st.markdown("---")


def generate_sitemap(base_url: str, dashboards: List[Dict]) -> str:
    """サイトマップXMLを生成"""

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{base_url}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
"""

    for dashboard in dashboards:
        sitemap += f"""    <url>
        <loc>{base_url}{dashboard['filename']}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.8</priority>
    </url>
"""

    sitemap += "</urlset>"
    return sitemap


def create_metadata_import_export():
    """メタデータのインポート/エクスポート機能"""

    st.header("📋 メタデータ管理")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📥 インポート")

        uploaded_json = st.file_uploader(
            "メタデータJSONファイル",
            type=['json'],
            help="以前エクスポートしたメタデータファイル"
        )

        if uploaded_json:
            try:
                metadata = json.load(uploaded_json)
                st.success(f"{len(metadata)}個のメタデータを読み込みました")

                # プレビュー
                with st.expander("プレビュー"):
                    for m in metadata[:3]:
                        st.write(f"• {m['icon']} {m['button_name']} - {m['short_description']}")
                    if len(metadata) > 3:
                        st.write(f"... 他 {len(metadata) - 3} 件")

                if st.button("インポート実行"):
                    st.session_state.dashboard_metadata = metadata
                    st.success("メタデータをインポートしました")
                    st.rerun()

            except Exception as e:
                st.error(f"インポートエラー: {str(e)}")

    with col2:
        st.subheader("📤 エクスポート")

        if 'dashboard_metadata' in st.session_state:
            metadata = st.session_state.dashboard_metadata

            st.info(f"{len(metadata)}個のメタデータ")

            # エクスポート形式選択
            export_format = st.selectbox(
                "エクスポート形式",
                ["JSON", "CSV", "Excel"]
            )

            if export_format == "JSON":
                json_data = json.dumps(metadata, indent=2, ensure_ascii=False)
                st.download_button(
                    "📥 JSONダウンロード",
                    json_data,
                    file_name=f"dashboard_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

            elif export_format == "CSV":
                import csv
                import io

                output = io.StringIO()
                if metadata:
                    writer = csv.DictWriter(output, fieldnames=metadata[0].keys())
                    writer.writeheader()
                    writer.writerows(metadata)

                st.download_button(
                    "📥 CSVダウンロード",
                    output.getvalue(),
                    file_name=f"dashboard_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            elif export_format == "Excel":
                df = pd.DataFrame(metadata)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Metadata')

                st.download_button(
                    "📥 Excelダウンロード",
                    output.getvalue(),
                    file_name=f"dashboard_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("エクスポートするメタデータがありません")


# メイン実行
if __name__ == "__main__":
    create_enhanced_dashboard_app()