// ============== NAVİGASYON ==============
document.addEventListener('DOMContentLoaded', function() {
    // Hamburger menü
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger) {
        hamburger.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
    
    // Aktif sayfa işaretleme
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-links a').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Scroll efekti
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(26, 26, 46, 0.98)';
        } else {
            navbar.style.background = 'rgba(26, 26, 46, 0.9)';
        }
    });
});

// ============== QR CODE GENERATOR ==============
async function generateQR() {
    const data = document.getElementById('qr-data').value;
    const resultDiv = document.getElementById('qr-result');
    
    if (!data) {
        resultDiv.innerHTML = '<p style="color: #f5576c;">Lütfen bir metin veya URL girin!</p>';
        return;
    }
    
    try {
        const response = await fetch('/api/generate-qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ data: data }),
        });
        
        const result = await response.json();
        
        if (result.error) {
            resultDiv.innerHTML = `<p style="color: #f5576c;">${result.error}</p>`;
        } else {
            resultDiv.innerHTML = `
                <img src="${result.image}" alt="QR Code">
                <br><br>
                <a href="${result.image}" download="qrcode.png" class="btn btn-primary">
                    📥 İndir
                </a>
            `;
        }
    } catch (error) {
        resultDiv.innerHTML = '<p style="color: #f5576c;">Bir hata oluştu!</p>';
    }
}

// ============== ŞİFRE OLUŞTURUCU ==============
async function generatePassword() {
    const length = document.getElementById('password-length').value;
    const uppercase = document.getElementById('uppercase').checked;
    const lowercase = document.getElementById('lowercase').checked;
    const numbers = document.getElementById('numbers').checked;
    const symbols = document.getElementById('symbols').checked;
    
    const resultDiv = document.getElementById('password-result');
    
    if (!uppercase && !lowercase && !numbers && !symbols) {
        resultDiv.textContent = 'En az bir seçenek seçin!';
        resultDiv.style.color = '#f5576c';
        return;
    }
    
    try {
        const response = await fetch('/api/generate-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                length: parseInt(length),
                uppercase: uppercase,
                lowercase: lowercase,
                numbers: numbers,
                symbols: symbols,
            }),
        });
        
        const result = await response.json();
        
        if (result.error) {
            resultDiv.textContent = result.error;
            resultDiv.style.color = '#f5576c';
        } else {
            resultDiv.textContent = result.password;
            resultDiv.style.color = '#43e97b';
        }
    } catch (error) {
        resultDiv.textContent = 'Bir hata oluştu!';
        resultDiv.style.color = '#f5576c';
    }
}

function updateLengthValue(value) {
    document.getElementById('length-value').textContent = value;
}

function copyPassword() {
    const password = document.getElementById('password-result').textContent;
    navigator.clipboard.writeText(password).then(() => {
        const btn = document.querySelector('.copy-btn');
        const originalText = btn.textContent;
        btn.textContent = '✓ Kopyalandı!';
        btn.style.background = 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
        }, 2000);
    });
}

// ============== ANİMASYONLAR ==============
// Scroll ile görünür olan elementlere animasyon
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('animate-in');
        }
    });
}, observerOptions);

document.querySelectorAll('.card, .about-card, .timeline-item').forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'all 0.6s ease';
    observer.observe(el);
});

// Animasyon class'ı
document.head.insertAdjacentHTML('beforeend', `
    <style>
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
    </style>
`);
