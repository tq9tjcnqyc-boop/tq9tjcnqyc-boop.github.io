import * as params from '@params';

const resList = document.getElementById('searchResults');
const sInput = document.getElementById('searchInput');
const searchBox = document.getElementById('searchbox');

let fuse;
let currentElement = null;
let firstResult = null;
let lastResult = null;

const defaultFuseOptions = {
    distance: 100,
    threshold: 0.4,
    ignoreLocation: true,
    /* 2026-08-12: keys 精简 — index.json 已去掉 summary(与content重叠的全文),
       permalink 匹配无意义。只搜 title + content, Fuse 少扫一个大字段, 提速明显 */
    keys: ['title', 'content']
};

const buildFuseOptions = () => {
    if (!params.fuseOpts) {
        return defaultFuseOptions;
    }

    return {
        isCaseSensitive: params.fuseOpts.iscasesensitive ?? false,
        includeScore: params.fuseOpts.includescore ?? false,
        includeMatches: params.fuseOpts.includematches ?? false,
        minMatchCharLength: params.fuseOpts.minmatchcharlength ?? 1,
        shouldSort: params.fuseOpts.shouldsort ?? true,
        findAllMatches: params.fuseOpts.findallmatches ?? false,
        ignoreFieldNorm: true, /* 2026-08-12: 大索引提速(206篇全文), 排序精度影响无感 */
        keys: params.fuseOpts.keys ?? defaultFuseOptions.keys,
        location: params.fuseOpts.location ?? 0,
        threshold: params.fuseOpts.threshold ?? defaultFuseOptions.threshold,
        distance: params.fuseOpts.distance ?? defaultFuseOptions.distance,
        ignoreLocation: params.fuseOpts.ignorelocation ?? defaultFuseOptions.ignoreLocation
    };
};

/* 2026-08-11: 防抖/IME 逻辑已删除 — 按钮确认制下输入过程零搜索,
   不需要任何中间态处理。 */

const reset = () => {
    currentElement = null;
    firstResult = null;
    lastResult = null;
    resList.innerHTML = '';
    sInput.value = '';
    hideStatus();
    if (typeof updateClear === 'function') updateClear();
    sInput.focus();
};

const setActiveResult = (element) => {
    document.querySelectorAll('.focus').forEach((item) => item.classList.remove('focus'));

    if (!element) {
        return;
    }

    element.focus();
    element.parentElement?.classList.add('focus');
    currentElement = element;
};

const renderResults = (results) => {
    if (!Array.isArray(results) || results.length === 0) {
        resList.innerHTML = '';
        firstResult = lastResult = currentElement = null;
        hideStatus();
        return;
    }

    const fragment = document.createDocumentFragment();

    for (const result of results) {
        const li = document.createElement('li');
        const titleText = document.createTextNode(result.item.title);
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '24');
        svg.setAttribute('height', '24');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.setAttribute('stroke-linecap', 'round');
        svg.setAttribute('stroke-linejoin', 'round');
        svg.classList.add('feather', 'feather-chevrons-right');

        svg.innerHTML = '<polyline points="13 17 18 12 13 7"></polyline><polyline points="6 17 11 12 6 7"></polyline>';

        const link = document.createElement('a');
        link.className = 'entry-link';
        link.href = result.item.permalink;
        link.setAttribute('aria-label', result.item.title);

        li.appendChild(titleText);
        li.appendChild(svg);
        li.appendChild(link);
        fragment.appendChild(li);
    }

    /* 2026-08-12: 结果分批渲染 (每帧 25 条) — 搜「装置」202 条一次性 append
       会卡顿(大 DOM 操作), 分批后首屏秒出, 键盘导航的 first/last 随批次更新 */
    resList.innerHTML = '';
    firstResult = lastResult = currentElement = null;
    const items = Array.from(fragment.children);
    const BATCH = 25;
    let i = 0;
    const nextBatch = () => {
        const end = Math.min(i + BATCH, items.length);
        for (; i < end; i++) resList.appendChild(items[i]);
        if (!firstResult) firstResult = resList.firstElementChild;
        lastResult = resList.lastElementChild;
        if (i < items.length) {
            requestAnimationFrame(nextBatch);
        }
    };
    nextBatch();
};

const performSearch = () => {
    if (!fuse) {
        return;
    }

    const query = sInput.value.trim();
    if (!query) {
        renderResults([]);
        return;
    }

    const searchOptions = params.fuseOpts?.limit ? { limit: params.fuseOpts.limit } : undefined;
    const results = searchOptions ? fuse.search(query, searchOptions) : fuse.search(query);
    renderResults(results);
};

/* 2026-08-12: 搜索按钮确认制下, 索引(index.json 6.2MB)加载需要几秒 —
   就绪前点搜索不能无反应: 显示「索引加载中…」, 就绪后自动补搜。
   状态行插在结果列表前, inline style 不走 custom.css(避免中文注释坑)。 */
const statusEl = document.createElement('div');
statusEl.id = 'searchStatus';
statusEl.style.cssText = 'text-align:center;padding:16px 0;color:var(--secondary);font-size:14px;display:none;';
const showStatus = (msg) => {
    statusEl.textContent = msg;
    statusEl.style.display = 'block';
};
const hideStatus = () => {
    statusEl.style.display = 'none';
};

let pendingQuery = null;

const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('searchClear');

/* 2026-08-12: 自绘清除按钮 — 有输入显示, 空隐藏, 点击清空并复位结果 */
const updateClear = () => {
    if (clearBtn) clearBtn.hidden = !sInput.value;
};
if (clearBtn) {
    clearBtn.addEventListener('click', () => {
        reset();
        sInput.focus();
    });
}
sInput?.addEventListener('input', updateClear);
sInput?.addEventListener('search', updateClear); // 键盘/原生清除也同步

const doSearch = () => {
    const q = sInput.value.trim();
    if (!q) {
        return;
    }
    if (!fuse) {
        // 索引未就绪: 提示 + 记住关键词, 就绪后自动执行
        pendingQuery = q;
        showStatus('索引加载中… 完成后自动搜索');
        return;
    }
    performSearch();
};

const initSearch = async () => {
    if (!sInput || !resList) {
        return;
    }

    // 输入框/按钮立即可用(HTML 不再 disabled): 索引就绪前点搜索由
    // doSearch 显示「索引加载中…」+ 就绪自动补搜, 不再锁输入 (2026-08-12:
    // 之前锁到索引加载完, 手机 6.2MB 加载几秒~十几秒, 用户半天进不了输入框)
    resList.before(statusEl);
    sInput.focus();

    try {
        const response = await fetch('../index.json');
        if (!response.ok) {
            throw new Error(`Search index load failed: ${response.status}`);
        }

        const data = await response.json();
        if (data) {
            fuse = new Fuse(data, buildFuseOptions());
        }
    } catch (error) {
        console.error(error);
        showStatus('索引加载失败，请刷新重试');
        return;
    }

    hideStatus();
    if (pendingQuery) {
        // 就绪前按过搜索: 自动补搜
        sInput.value = pendingQuery;
        pendingQuery = null;
        performSearch();
    }
};

/* 2026-08-12: DOMContentLoaded 就拉索引(原来等 load, fetch 晚开始,
   首次搜索整体更慢); readyState 判断兼容 script 时序 */
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSearch);
} else {
    initSearch();
}

sInput?.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        event.preventDefault();
        doSearch();
    }
});

searchBtn?.addEventListener('click', doSearch);

sInput?.addEventListener('search', () => {
    if (!sInput.value) {
        reset();
    }
});

document.addEventListener('keydown', (event) => {
    const { key } = event;
    const active = document.activeElement;
    const isInSearchBox = searchBox?.contains(active);

    if (key === 'Escape') {
        reset();
        return;
    }

    if (!firstResult || !isInSearchBox) {
        return;
    }

    if (key === 'ArrowDown') {
        event.preventDefault();

        if (active === sInput) {
            setActiveResult(firstResult.querySelector('.entry-link'));
        } else if (active?.parentElement !== lastResult) {
            setActiveResult(active?.parentElement?.nextElementSibling?.querySelector('.entry-link'));
        }
    } else if (key === 'ArrowUp') {
        event.preventDefault();

        if (active?.parentElement === firstResult) {
            setActiveResult(sInput);
        } else if (active !== sInput) {
            setActiveResult(active?.parentElement?.previousElementSibling?.querySelector('.entry-link'));
        }
    } else if (key === 'ArrowRight') {
        if (active?.matches?.('.entry-link')) {
            active.click();
        }
    }
});
