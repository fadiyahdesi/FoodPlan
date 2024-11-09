document.addEventListener('DOMContentLoaded', function() {
    // Show all items initially
    const items = document.querySelectorAll('.gallery-item');
    items.forEach(item => item.classList.add('show'));

    // Filter functionality
    const filterButtons = document.querySelectorAll('.filter-btn');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');

            const category = this.getAttribute('data-category');
            
            items.forEach(item => {
                if (category === 'all' || item.getAttribute('data-category') === category) {
                    item.classList.add('show');
                } else {
                    item.classList.remove('show');
                }
            });
        });
    });

    // More button functionality (expand all)
    const moreButton = document.querySelector('.more-btn');
    let isShowingAll = true;

    moreButton.addEventListener('click', function() {
        if (isShowingAll) {
            items.forEach(item => item.classList.add('show'));
            moreButton.textContent = "Sembunyikan Beberapa";
        } else {
            items.forEach(item => item.classList.remove('show'));
            filterButtons[0].click();  // Reset to default category
            moreButton.textContent = "Lihat Semua";
        }
        isShowingAll = !isShowingAll;
    });
});