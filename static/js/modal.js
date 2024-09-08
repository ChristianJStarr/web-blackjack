document.addEventListener('DOMContentLoaded', function() {

    const modal_links = document.querySelectorAll('a[data-modal]');
    const modals = document.querySelectorAll('.modal');

    for (const modal of modals) {
        const close = modal.querySelector('.modal__close');
        if(close) {
            close.onclick = event => {
                modal.classList.remove('-show');
            }
        }
    }

    for (const modal_link of modal_links) {
        for (const modal of modals) {
            if (modal.dataset.modal === modal_link.dataset.modal) {
                modal_link.onclick = event => {
                    hideModals();
                    modal.classList.add('-show');
                }
            }
        }
    }

    function hideModals() {
        for (const modal of modals) {
            modal.classList.remove('-show');
        }
    }


});