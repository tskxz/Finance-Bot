document.addEventListener('DOMContentLoaded', function () {
    const flashMessages = document.querySelectorAll('.flash-messages li');
    if (flashMessages.length > 0) {
        flashMessages.forEach(function (message) {
            Swal.fire({
                title: 'Error!',
                text: message.textContent,
                icon: 'error',
                confirmButtonText: 'OK'
            });
        });
    }
});
