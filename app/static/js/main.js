// FitStart Global JavaScript
document.addEventListener('DOMContentLoaded', function () {
    // Mobile navigation toggle
    const mobileToggle = document.querySelector('.nav-mobile-toggle');
    const navMenu = document.querySelector('.nav-menu');
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function () {
            navMenu.classList.toggle('active');
        });
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });
});
