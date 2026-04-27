// static/admin/js/color-picker.js
// Синхронизация цветовых пикеров

document.addEventListener('DOMContentLoaded', function() {
    initPickers();

    // Наблюдатель за динамическими элементами (например, inline formsets)
    const observer = new MutationObserver(mutations => {
        mutations.forEach(m => m.addedNodes.forEach(n => {
            if (n.nodeType === 1) initPickers(n);
        }));
    });
    observer.observe(document.body, { childList: true, subtree: true });
});

function initPickers(container = document) {
    container.querySelectorAll('.color-picker-widget').forEach(widget => {
        if (widget.dataset.initialized === 'true') return;
        widget.dataset.initialized = 'true';

        const colorInput = widget.querySelector('input[type="color"]');
        const hexInput = widget.querySelector('input.color-hex-input');
        const preview = widget.querySelector('.color-preview');

        function syncFromColor() {
            const val = colorInput.value.toLowerCase();
            hexInput.value = val;
            if (preview) preview.style.backgroundColor = val;
        }

        function syncFromHex() {
            let val = hexInput.value.trim().toLowerCase();
            if (!val.startsWith('#')) val = '#' + val;
            if (/^#([0-9a-f]{3}|[0-9a-f]{6})$/.test(val)) {
                if (val.length === 4) {
                    val = '#' + val[1]+val[1] + val[2]+val[2] + val[3]+val[3];
                }
                hexInput.value = val;
                colorInput.value = val;
                if (preview) preview.style.backgroundColor = val;
            }
        }

        colorInput.addEventListener('input', syncFromColor);
        hexInput.addEventListener('input', syncFromHex);
        hexInput.addEventListener('blur', syncFromHex);
        syncFromColor(); // начальное состояние
    });
}
