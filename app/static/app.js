document.addEventListener('DOMContentLoaded', function() {
    const clearFiltersBtn = document.getElementById('clear-filters-btn');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            // Redirect to the base URL of the page, removing all query parameters
            window.location.href = window.location.pathname;
        });
    }
});