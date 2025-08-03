
// main.js (情報パネル対応・一覧表示対応版)
document.addEventListener('DOMContentLoaded', () => {
    const dynamicContent = document.getElementById('dynamic-content');
    const deptSelector = document.getElementById('dept-selector');
    const wardSelector = document.getElementById('ward-selector');
    const quickButtons = document.querySelectorAll('.quick-button');
    const loader = document.getElementById('loader');
    const initialContentHTML = dynamicContent.innerHTML;

    const getBasePath = () => {
        const path = window.location.pathname;
        const repoName = path.split('/')[1] || '';
        return window.location.hostname.includes('github.io') ? `/${repoName}` : '';
    };
    const basePath = getBasePath();

    // 情報パネル関連の関数
    window.toggleInfoPanel = function() {
        const panel = document.getElementById('info-panel');
        if (panel) {
            panel.classList.toggle('active');
        }
    };

    window.showInfoTab = function(tabName) {
        // すべてのタブとパネルを非アクティブに
        document.querySelectorAll('.info-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // 選択されたタブとパネルをアクティブに
        const activeTab = document.querySelector(`.info-tab[onclick*="${tabName}"]`);
        if (activeTab) {
            activeTab.classList.add('active');
        }
        
        const activePane = document.getElementById(tabName + '-tab');
        if (activePane) {
            activePane.classList.add('active');
        }
    };

    // パネル外クリックで閉じる
    const infoPanel = document.getElementById('info-panel');
    if (infoPanel) {
        infoPanel.addEventListener('click', function(e) {
            if (e.target === this) {
                toggleInfoPanel();
            }
        });
    }

    const executeScriptsInContainer = (container) => {
        const scripts = container.querySelectorAll('script');
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            newScript.innerHTML = oldScript.innerHTML;
            oldScript.parentNode.replaceChild(newScript, oldScript);
        });
    };

    const resizePlots = (container) => {
        if (window.Plotly) {
            const plots = container.querySelectorAll('.plotly-graph-div');
            plots.forEach(plot => Plotly.Plots.resize(plot));
        }
    };

    const loadContent = (fragmentPath) => {
        if (!fragmentPath) return;
        
        loader.style.display = 'flex';
        const fullPath = `${basePath}/${fragmentPath}`;

        fetch(fullPath)
            .then(response => {
                if (!response.ok) throw new Error(`ファイルが見つかりません: ${fragmentPath}`);
                return response.text();
            })
            .then(html => {
                dynamicContent.innerHTML = html;
                executeScriptsInContainer(dynamicContent);
            })
            .catch(error => {
                dynamicContent.innerHTML = `<div class="error">${error.message}</div>`;
                console.error(error);
            })
            .finally(() => {
                loader.style.display = 'none';
            });
    };

    quickButtons.forEach(button => {
        button.addEventListener('click', () => {
            quickButtons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            
            const fragment = button.dataset.fragment;
            const selectorId = button.dataset.selector;
            
            // セレクターの表示・非表示
            deptSelector.style.display = selectorId === 'dept-selector' ? 'flex' : 'none';
            wardSelector.style.display = selectorId === 'ward-selector' ? 'flex' : 'none';
            
            // ★★★ ここから修正 ★★★
            if(selectorId) {
              document.getElementById(selectorId).value = "";
              // セレクターボタンが押されたら、対応する一覧(サマリー)を読み込む
              if (selectorId === 'dept-selector') {
                  loadContent('fragments/dept-summary.html');
              } else if (selectorId === 'ward-selector') {
                  loadContent('fragments/ward-summary.html');
              } else {
                  dynamicContent.innerHTML = '<div class="placeholder">上記から項目を選択してください</div>';
              }
            }
            // ★★★ 修正ここまで ★★★
            
            if (fragment) {
                if (fragment.includes('view-all')) {
                    dynamicContent.innerHTML = initialContentHTML;
                    // 必要ならresizePlots(dynamicContent);を呼び出す
                } else {
                    loadContent(fragment);
                }
            }
        });
    });
    
    const handleSelectChange = (event) => {
        const selectedOption = event.target.options[event.target.selectedIndex];
        const fragment = selectedOption.dataset.fragment;
        if (fragment) {
            loadContent(fragment);
        } else {
            // ★★★ プルダウンで「項目を選択」に戻された場合、一覧を再表示 ★★★
            if(event.target.id === 'dept-selector') {
                loadContent('fragments/dept-summary.html');
            } else if (event.target.id === 'ward-selector') {
                loadContent('fragments/ward-summary.html');
            }
        }
    };
    deptSelector.addEventListener('change', handleSelectChange);
    wardSelector.addEventListener('change', handleSelectChange);

    window.addEventListener('load', () => {
        resizePlots(dynamicContent);
    });
    
    // ESCキーで情報パネルを閉じる
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const panel = document.getElementById('info-panel');
            if (panel && panel.classList.contains('active')) {
                toggleInfoPanel();
            }
        }
    });
});
