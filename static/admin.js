// script.js
// document.addEventListener('DOMContentLoaded', function () {
//     $('#deleteModal').on('show.bs.modal', function (event) {
//         var button = $(event.relatedTarget); // Button that triggered the modal
//         var productId = button.data('id'); // Extract info from data-* attributes
//         var actionUrl = "{{ url_for('hapus_produk', id='') }}" + productId; // Construct action URL

//         var modal = $(this);
//         modal.find('#deleteForm').attr('action', actionUrl); // Set form action
//     });
// });

    $(document).ready(function() {
        $('#example2').DataTable({
            "paging": true,
            "lengthChange": false,
            "searching": false,
            "ordering": true,
            "info": true,
            "autoWidth": false,
            "responsive": true
        });
    });


async function fetchData() {
    const response = await fetch('/count'); // Mengambil data dari endpoint
    const data = await response.json(); // Mengonversi respons ke JSON

    const months = [];
    const categories = {};

    // Mengelompokkan data berdasarkan bulan dan kategori
    data.forEach(item => {
        if (!months.includes(item.month)) {
            months.push(item.month);
        }
        if (!categories[item.product_category]) {
            categories[item.product_category] = new Array(months.length).fill(0);
        }
        const monthIndex = months.indexOf(item.month);
        categories[item.product_category][monthIndex] = item.count;
    });

    return { months, categories };
}

async function createChart() {
    const { months, categories } = await fetchData();

    const ctx = document.getElementById('productChart').getContext('2d'); // Ganti ID di sini

    // Menyiapkan dataset untuk Chart.js
    const datasets = Object.keys(categories).map(category => ({
        label: category,
        data: categories[category],
        borderColor: getRandomColor(), // Menghasilkan warna acak untuk setiap kategori
        fill: false
    }));

    // Membuat chart
    const productChart = new Chart(ctx, { // Ganti variabel di sini jika diperlukan
        type: 'line', // Jenis chart, bisa diganti dengan 'bar', 'pie', dll
        data: {
            labels: months, // Label sumbu X (bulan)
            datasets: datasets // Data untuk chart
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Fungsi untuk menghasilkan warna acak
function getRandomColor() {
    const letters = '0123456789ABCDEF';
    let color = '#';
    for (let i = 0; i < 6; i++) {
        color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
}

// Memanggil fungsi untuk membuat chart saat halaman dimuat
createChart();

// Contoh JavaScript sederhana
document.addEventListener("DOMContentLoaded", function () {
    console.log("Login page loaded");
    // Tambahkan skrip tambahan di sini
});


