// static/admin/js/header_font_choice.js
document.addEventListener('DOMContentLoaded', function() {
    const fontChoiceSelect = document.querySelector('#id_header_font_choice');
    const customFontRow = document.querySelector('#id_header_font_family').closest('.form-row');

    if (!fontChoiceSelect || !customFontRow) return;

    function toggleCustomFont() {
        if (fontChoiceSelect.value === 'custom') {
            customFontRow.style.display = '';
        } else {
            customFontRow.style.display = 'none';
        }
    }

    fontChoiceSelect.addEventListener('change', toggleCustomFont);
    toggleCustomFont(); // вызов при загрузке
});
