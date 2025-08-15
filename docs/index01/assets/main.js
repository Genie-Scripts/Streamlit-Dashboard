
// main.js (初期表示自動化・リサイズ安定化版)
// main.js (初期表示自動化・リサイズ安定化版 + 情報パネル機能追加)
document.addEventListener('DOMContentLoaded', () => {
    const dynamicContent = document.getElementById('dynamic-content');
    const deptSelector = document.getElementById('dept-selector');
    const wardSelector = document.getElementById('ward-selector');
    const quickButtons = document.querySelectorAll('.quick-button');
    const loader = document.getElementById('loader');

    const executeScriptsInContainer = (container) => {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            newScript.innerHTML = oldScript.innerHTML;
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    };

    const resizePlots = (container) => {
        if (window.Plotly && container) {
            const plots = container.querySelectorAll('.plotly-graph-div');
            plots.forEach(plot => {
                try {
                    Plotly.Plots.resize(plot);
                } catch (e) {
                    console.warn('Plotly resize error:', e);
                }
            });
        }
    };

    const loadContent = (fragmentPath, isInitialLoad = false) => {
        if (!fragmentPath) return;
        
        // 初期ロード時はローダーを表示しない（ちらつき防止）
        if (!isInitialLoad) {
            loader.style.display = 'flex';
        }
        
        const basePath = window.location.hostname.includes('github.io') ? 
            (window.location.pathname.split('/')[1] ? `/${window.location.pathname.split('/')[1]}` : '') : '';
        const fullPath = `${basePath}/${fragmentPath}`;

        fetch(fullPath)
            .then(response => {
                if (!response.ok) throw new Error(`ファイルが見つかりません: ${fragmentPath}`);
                return response.text();
            })
            .then(html => {
                dynamicContent.innerHTML = html;
                executeScriptsInContainer(dynamicContent);
                
                // チャート描画の確実な実行（複数回試行）
                setTimeout(() => resizePlots(dynamicContent), 100);
                setTimeout(() => resizePlots(dynamicContent), 300);
                setTimeout(() => resizePlots(dynamicContent), 500);
            })
            .catch(error => {
                console.error('Fragment load error:', error);
                dynamicContent.innerHTML = `<div class="error"><h3>コンテンツの読み込みに失敗</h3><p>${error.message}</p></div>`;
            })
            .finally(() => {
                if (!isInitialLoad) {
                    loader.style.display = 'none';
                }
            });
    };

    // ===== 初期表示の自動実行 =====
    // ページロード時に病院全体のデータを自動的に表示
    const initializeDefaultView = () => {
        // 病院全体ボタンを探す（view-allも含めて検索）
        const hospitalButton = Array.from(quickButtons).find(btn => {
            const fragment = btn.dataset.fragment;
            const text = btn.textContent || btn.innerText;
            // ボタンのテキストまたはdata-fragment属性で病院全体を識別
            // view-all.htmlも病院全体として認識
            return (fragment && (fragment.includes('hospital') || fragment.includes('view-all'))) ||
                   (text && text.includes('病院全体'));
        });
        
        if (hospitalButton) {
            // 病院全体ボタンをアクティブに設定
            hospitalButton.classList.add('active');
            
            // 病院全体のフラグメントを読み込み（初期ロードフラグ付き）
            const fragment = hospitalButton.dataset.fragment;
            if (fragment) {
                console.log('初期表示: 病院全体データを読み込み中...', fragment);
                // 実際のボタンから取得したフラグメントパスを使用
                loadContent(fragment, true);
            } else {
                console.warn('病院全体ボタンのdata-fragment属性が見つかりません');
            }
        } else {
            // ボタンが見つからない場合、view-all.htmlを直接読み込み
            console.warn('病院全体ボタンが見つかりません。view-all.htmlを直接読み込みます。');
            // フォールバック: fragments/view-all.html を直接読み込み
            loadContent('fragments/view-all.html', true);
        }
    };

    // クイックボタンのイベントリスナー設定
    quickButtons.forEach(button => {
        button.addEventListener('click', () => {
            quickButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const fragment = button.dataset.fragment;
            const selectorId = button.dataset.selector;
            
            if (deptSelector) deptSelector.style.display = selectorId === 'dept-selector' ? 'block' : 'none';
            if (wardSelector) wardSelector.style.display = selectorId === 'ward-selector' ? 'block' : 'none';
            
            if (!selectorId) {
                if (deptSelector) deptSelector.selectedIndex = 0;
                if (wardSelector) wardSelector.selectedIndex = 0;
            }
            
            if (fragment) loadContent(fragment);
        });
    });

    // セレクタのイベントリスナー設定
    const handleSelectorChange = (selector) => {
        const selectedOption = selector.options[selector.selectedIndex];
        const fragment = selectedOption.dataset.fragment;
        if (fragment) loadContent(fragment);
    };

    if (deptSelector) {
        deptSelector.addEventListener('change', () => handleSelectorChange(deptSelector));
    }
    
    if (wardSelector) {
        wardSelector.addEventListener('change', () => handleSelectorChange(wardSelector));
    }

    // ウィンドウリサイズ時にグラフをリサイズ
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => resizePlots(dynamicContent), 250);
    });

    // ===== ここで初期表示を実行 =====
    initializeDefaultView();
});

// ===== 情報パネル関連の関数 =====
// toggleInfoPanel関数をグローバルスコープに定義
window.toggleInfoPanel = function() {
    const infoPanel = document.getElementById('info-panel');
    if (infoPanel) {
        const isActive = infoPanel.classList.contains('active');
        if (isActive) {
            infoPanel.classList.remove('active');
            infoPanel.style.display = 'none';
        } else {
            infoPanel.classList.add('active');
            infoPanel.style.display = 'block';
        }
    } else {
        console.warn('情報パネル(#info-panel)が見つかりません');
    }
};

// showInfoTab関数をグローバルスコープに定義
window.showInfoTab = function(tabName) {
    // すべてのタブボタンとタブパネルを取得
    const tabButtons = document.querySelectorAll('.info-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // すべてのタブボタンから active クラスを削除
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // すべてのタブパネルから active クラスを削除
    tabPanes.forEach(pane => {
        pane.classList.remove('active');
    });
    
    // 指定されたタブのボタンとパネルに active クラスを追加
    const targetButton = Array.from(tabButtons).find(btn => 
        btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`'${tabName}'`)
    );
    const targetPane = document.getElementById(`${tabName}-tab`);
    
    if (targetButton) {
        targetButton.classList.add('active');
    }
    
    if (targetPane) {
        targetPane.classList.add('active');
    } else {
        console.warn(`タブパネル '${tabName}-tab' が見つかりません`);
    }
};
