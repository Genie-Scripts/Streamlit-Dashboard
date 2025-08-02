<div class="header">
    <a href="../index.html" class="portal-home-button">🚀 ポータルTOPへ</a>




ボタンのデザインをCSSファイル（例: docs/index01/assets/styles.css）に記述します。ヘッダー（.header）を基準に配置する

/* ヘッダーの基準位置設定 */
.header {
    position: relative; /* ポータルへ戻るボタンの基準点とする */
    padding-top: 60px; /* ボタンを置くスペースを確保 */
}

/* ポータルへ戻るボタンのスタイル */
.portal-home-button {
    position: absolute;
    top: 15px;
    left: 15px;
    background-color: rgba(255, 255, 255, 0.2);
    color: white;
    padding: 8px 16px;
    border-radius: 20px;
    text-decoration: none;
    font-weight: bold;
    font-size: 14px;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.3);
}

.portal-home-button:hover {
    background-color: rgba(255, 255, 255, 0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0,0,0,0.2);
}

/* スマートフォン用の調整 */
@media (max-width: 768px) {
    .header {
        padding-top: 50px;
    }
    .portal-home-button {
        top: 10px;
        left: 10px;
        padding: 6px 12px;
        font-size: 12px;
    }
}