(function() {
    const overlay = document.createElement('div');
    overlay.id = '_e2e_sync';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;'
        + 'background:#00FF00;display:flex;flex-direction:column;align-items:center;justify-content:center;'
        + 'z-index:999999;';
    const img = document.createElement('img');
    img.src = '{{dataUrl}}';
    img.style.cssText = 'width:400px;height:400px;image-rendering:pixelated;';
    overlay.appendChild(img);
    const label = '{{label}}';
    if (label) {
        const lbl = document.createElement('div');
        lbl.textContent = label;
        lbl.style.cssText = 'margin-top:12px;font-family:monospace;font-size:18px;color:#000;'
            + 'background:rgba(255,255,255,0.85);padding:6px 16px;border-radius:6px;'
            + 'max-width:80vw;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;';
        overlay.appendChild(lbl);
    }
    document.body.appendChild(overlay);
})()
