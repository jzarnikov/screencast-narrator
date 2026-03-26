(el) => {
    const rect = el.getBoundingClientRect();
    const pad = {{padding}};
    const viewportArea = window.innerWidth * window.innerHeight;
    const elArea = rect.width * rect.height;
    const areaPct = (elArea / viewportArea) * 100;
    const threshold = {{underlineThresholdPct}};
    const isLarge = areaPct > threshold;

    let targetRect = rect;
    if (isLarge) {
        const sources = el._e2eSourceElements || [el];
        let found = null;
        for (const src of sources) {
            const tag = src.tagName.toLowerCase();
            if (tag === 'tr') {
                found = src.querySelector('th, td');
            } else if (tag === 'table' || tag === 'tbody') {
                found = src.querySelector('thead tr, tr');
            }
            if (!found) {
                found = src.querySelector('h1, h2, h3, h4, h5, h6, [role="heading"], legend, caption, summary');
            }
            if (!found) {
                const walker = document.createTreeWalker(src, NodeFilter.SHOW_TEXT, {
                    acceptNode: (n) => n.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
                });
                const firstText = walker.nextNode();
                if (firstText && firstText.parentElement) {
                    found = firstText.parentElement;
                }
            }
            if (found) break;
        }
        if (found) {
            targetRect = found.getBoundingClientRect();
        }
    }

    const canvas = document.createElement('canvas');
    canvas.id = '_e2e_highlight';
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.cssText = 'position:fixed;top:0;left:0;pointer-events:none;z-index:99999;';
    document.body.appendChild(canvas);

    const ctx = canvas.getContext('2d');
    const minW = {{lineWidthMin}}, maxW = {{lineWidthMax}}, opacity = {{opacity}};
    const segments = {{segments}}, coverage = {{coverage}};

    const points = [];
    if (isLarge) {
        const y = targetRect.bottom + pad * 0.5;
        const x0 = targetRect.left - pad * 0.3;
        const x1 = targetRect.right + pad * 0.3;
        const tickHeight = 10;
        const tickSegs = Math.floor(segments * 0.08);
        for (let i = 0; i <= tickSegs; i++) {
            const t = i / tickSegs;
            points.push({ x: x0, y: y - tickHeight + tickHeight * t, widthT: t < 0.5 ? t * 2 : 1.0 });
        }
        const remaining = segments - tickSegs;
        for (let i = 0; i <= remaining; i++) {
            const t = i / remaining;
            const x = x0 + (x1 - x0) * t * coverage;
            const wobble = Math.sin(t * Math.PI * 6) * 0.6;
            points.push({ x, y: y + wobble, widthT: 1.0 });
        }
    } else {
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const rx = rect.width / 2 + pad;
        const ry = rect.height / 2 + pad * 0.78;
        const startAngle = -Math.PI / 2;
        for (let i = 0; i <= segments; i++) {
            const t = i / segments;
            const angle = startAngle - t * coverage * Math.PI * 2;
            const x = cx + rx * Math.cos(angle);
            const y = cy + ry * Math.sin(angle);
            const widthT = t < 0.2 ? t / 0.2 : 1.0;
            points.push({ x, y, widthT });
        }
    }

    const speed = {{animationSpeedMs}};
    const start = performance.now();
    function draw(now) {
        const progress = Math.min((now - start) / speed, 1.0);
        const n = Math.floor(progress * (points.length - 1));
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.globalAlpha = opacity;
        ctx.strokeStyle = '{{color}}';
        if (n > 0) {
            ctx.beginPath();
            ctx.moveTo(points[0].x, points[0].y);
            for (let i = 1; i <= n; i++) {
                ctx.lineWidth = minW + (maxW - minW) * points[i].widthT;
                ctx.lineTo(points[i].x, points[i].y);
            }
            ctx.stroke();
        }
        if (progress < 1.0) requestAnimationFrame(draw);
    }
    requestAnimationFrame(draw);
}
