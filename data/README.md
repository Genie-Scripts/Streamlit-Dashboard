# README.md
# 📊 HTML Dashboard Publisher

複数のHTMLファイルをGitHub Pagesで統合ダッシュボードとして自動公開するStreamlitアプリケーションです。

## 🌟 主な機能

- **複数HTMLファイル対応**: 一度に複数のHTMLファイルをアップロード・管理
- **自動インデックス生成**: 美しいランディングページを自動生成
- **GitHub Pages自動公開**: ワンクリックでWebダッシュボードを公開
- **モバイル対応**: レスポンシブデザインで全デバイス対応
- **プレビュー機能**: 公開前にローカルでプレビュー可能

## 🚀 セットアップ

### 1. 必要な準備

1. **GitHubアカウント**: GitHub Pagesで公開するため
2. **Personal Access Token**: 
   - GitHub Settings > Developer settings > Personal access tokens
   - `repo` 権限が必要
3. **公開用リポジトリ**: Publicリポジトリを作成

### 2. インストール

```bash
# リポジトリをクローン
git clone <this-repo>
cd html-dashboard-publisher

# 依存関係をインストール
pip install -r requirements.txt

# アプリケーション起動
streamlit run app.py
```

## 📖 使用方法

### Step 1: GitHub設定
1. サイドバーでGitHub Personal Access Tokenを入力
2. リポジトリ名を `owner/repo-name` 形式で入力
3. 「🧪 接続テスト」で設定を確認

### Step 2: HTMLファイルアップロード
1. メイン画面で複数のHTMLファイルを選択
2. アップロード後、プレビューで内容を確認

### Step 3: ダッシュボード設定
1. タイトル・サブタイトルを設定
2. 説明文・フッターをカスタマイズ
3. 「👀 インデックスプレビュー」で確認

### Step 4: 公開実行
1. 「📤 GitHub Pagesに公開」をクリック
2. 数分後、`https://owner.github.io/repo-name/` でアクセス可能

## 🎨 カスタマイズ

### インデックスページのデザイン変更
`generate_index_html()` 関数のCSSを編集してデザインをカスタマイズできます：

```python
# グラデーション背景の変更
background: linear-gradient(135deg, #your-color1, #your-color2);

# カードデザインの変更
.dashboard-item {
    background: your-background;
    border-radius: your-radius;
}
```

### ファイル構成の追加
新しいファイルタイプに対応する場合：

```python
# ファイルアップロードの拡張
uploaded_files = st.file_uploader(
    "ファイルを選択",
    type=['html', 'htm', 'pdf', 'jpg'],  # 新しいタイプを追加
    accept_multiple_files=True
)
```

## 🔧 高度な設定

### 環境変数での設定
```bash
# .env ファイル
GITHUB_TOKEN=your_token_here
DEFAULT_REPO=your-username/your-repo
```

### 自動デプロイの設定
GitHub Actionsワークフローを追加：

```yaml
# .github/workflows/deploy.yml
name: Deploy Dashboard
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Pages
        run: |
          # 自動デプロイスクリプト
```

## 📱 対応ブラウザ

- ✅ Chrome (推奨)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ モバイルブラウザ

## 🐛 トラブルシューティング

### よくある問題

1. **403 Forbidden エラー**
   - Personal Access Tokenの権限を確認
   - リポジトリがPublicか確認

2. **ファイルが表示されない**
   - GitHub Pages設定でブランチを確認
   - 数分待ってからアクセス

3. **日本語が文字化け**
   - HTMLファイルのエンコーディングをUTF-8に設定

### デバッグモード

```python
# ログレベルを変更
logging.getLogger().setLevel(logging.DEBUG)
```

## 📄 ライセンス

MIT License

## 🤝 コントリビューション

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 サポート

問題や質問がある場合は、GitHubのIssuesでお知らせください。