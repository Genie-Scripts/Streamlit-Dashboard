
// main.js (初期表示自動化・リサイズ安定化版)
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
            
            if (deptSelector) deptSelector.style.display = selectorId === 'dept-selector' ? 'flex' : 'none';
            if (wardSelector) wardSelector.style.display = selectorId === 'ward-selector' ? 'flex' : 'none';
            
            if (selectorId) {
                // セレクターボタンが押されたら、対応するサマリー(一覧)を読み込む
                if (selectorId === 'dept-selector' && deptSelector) {
                    deptSelector.value = ""; // ドロップダウンをリセット
                    loadContent('fragments/dept-summary.html');
                } else if (selectorId === 'ward-selector' && wardSelector) {
                    wardSelector.value = ""; // ドロップダウンをリセット
                    loadContent('fragments/ward-summary.html');
                }
            } else if (fragment) {
                // それ以外のボタンは通常通りフラグメントを読み込む
                loadContent(fragment);
            }
        });
    });
    
    // セレクトボックスのイベントリスナー
    const handleSelectChange = (event) => {
        const selectedOption = event.target.options[event.target.selectedIndex];
        const fragment = selectedOption.dataset.fragment;
        if (fragment) {
            loadContent(fragment);
        }
    };
    
    if (deptSelector) deptSelector.addEventListener('change', handleSelectChange);
    if (wardSelector) wardSelector.addEventListener('change', handleSelectChange);

    // ===== 初期表示実行 =====
    // デバッグ: ボタンの情報を出力
    console.log('利用可能なクイックボタン:');
    quickButtons.forEach((btn, index) => {
        console.log(`ボタン${index + 1}: テキスト="${btn.textContent}", data-fragment="${btn.dataset.fragment}"`);
    });
    
    // DOMContentLoaded直後に病院全体を表示
    initializeDefaultView();

    // ウィンドウリサイズ時の再描画（debounce処理）
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            resizePlots(document.getElementById('dynamic-content'));
        }, 250);
    });
    
    // ===== 追加: ページ表示後の確実な描画 =====
    // window.onloadでも再度チャートをリサイズ（念のため）
    window.addEventListener('load', () => {
        setTimeout(() => {
            resizePlots(document.getElementById('dynamic-content'));
        }, 500);
    });
});
