// static/admin/js/image-preview.js
document.addEventListener('DOMContentLoaded', function() {
    const wrappers = document.querySelectorAll('.image-preview-wrapper');
    wrappers.forEach(function(wrapper) {
        const fileInput = wrapper.querySelector('input[type="file"]');
        const previewContainer = wrapper.querySelector('.image-preview-container');
        const previewImg = previewContainer ? previewContainer.querySelector('.image-preview') : null;

        if (fileInput && previewContainer && previewImg) {
            fileInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        previewImg.src = e.target.result;
                        previewContainer.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                } else {
                    previewContainer.style.display = 'none';
                }
            });
        }
    });
});
