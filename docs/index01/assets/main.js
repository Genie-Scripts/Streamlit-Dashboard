
// main.js (修正版: 重複読み込み防止、情報パネル追加)
document.addEventListener('DOMContentLoaded', () => {
    const dynamicContent = document.getElementById('dynamic-content');
    const deptSelector = document.getElementById('dept-selector');
    const wardSelector = document.getElementById('ward-selector');
    const quickButtons = document.querySelectorAll('.quick-button');
    const loader = document.getElementById('loader');
    
    let currentLoadingPath = null; // 重複読み込み防止

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
        if (!fragmentPath || currentLoadingPath === fragmentPath) return;
        
        currentLoadingPath = fragmentPath; // 重複読み込み防止
        
        if (!isInitialLoad) {
            loader.style.display = 'flex';
        }

        fetch(fragmentPath)
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
                currentLoadingPath = null; // ロード完了
                if (!isInitialLoad) {
                    loader.style.display = 'none';
                }
            });
    };

    // ===== 初期表示の自動実行 =====
    const initializeDefaultView = () => {
        const hospitalButton = Array.from(quickButtons).find(btn => {
            const fragment = btn.dataset.fragment;
            const text = btn.textContent || btn.innerText;
            return (fragment && fragment.includes('view-all')) ||
                   (text && text.includes('病院全体'));
        });
        
        if (hospitalButton) {
            hospitalButton.classList.add('active');
            const fragment = hospitalButton.dataset.fragment;
            if (fragment) {
                console.log('初期表示: 病院全体データを読み込み中...', fragment);
                loadContent(fragment, true);
            }
        } else {
            console.warn('病院全体ボタンが見つかりません。view-all.htmlを直接読み込みます。');
            loadContent('fragments/view-all.html', true);
        }
    };

    // クイックボタンのイベントリスナー設定
    quickButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // 情報ボタンの場合は別処理
            if (button.classList.contains('info-button')) {
                return; // toggleInfoPanel()は別途処理
            }
            
            quickButtons.forEach(btn => {
                if (!btn.classList.contains('info-button')) {
                    btn.classList.remove('active');
                }
            });
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

    // 初期表示を実行
    initializeDefaultView();
});

// ===== 情報パネル関連の関数 =====
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
    }
};

window.showInfoTab = function(tabName) {
    const tabButtons = document.querySelectorAll('.info-tab');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabButtons.forEach(btn => btn.classList.remove('active'));
    tabPanes.forEach(pane => pane.classList.remove('active'));
    
    const targetButton = Array.from(tabButtons).find(btn => 
        btn.getAttribute('onclick') && btn.getAttribute('onclick').includes(`'${tabName}'`)
    );
    const targetPane = document.getElementById(`${tabName}-tab`);
    
    if (targetButton) targetButton.classList.add('active');
    if (targetPane) targetPane.classList.add('active');
};
