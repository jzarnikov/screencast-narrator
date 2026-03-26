(elements) => {
    let left = Infinity, top = Infinity, right = -Infinity, bottom = -Infinity;
    for (const el of elements) {
        const r = el.getBoundingClientRect();
        left = Math.min(left, r.left);
        top = Math.min(top, r.top);
        right = Math.max(right, r.right);
        bottom = Math.max(bottom, r.bottom);
    }
    const w = document.createElement('div');
    w.id = '_e2e_multi_highlight';
    w.style.cssText = `position:fixed;left:${left}px;top:${top}px;width:${right-left}px;height:${bottom-top}px;pointer-events:none;z-index:-1;`;
    w._e2eSourceElements = elements;
    document.body.appendChild(w);
}
