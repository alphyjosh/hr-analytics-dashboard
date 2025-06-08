// Smooth scrolling for navigation links with offset for fixed header
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            const headerOffset = 80; // Height of your fixed header
            const elementPosition = targetElement.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });

            // Update URL without page jump
            history.pushState(null, null, targetId);
        }
    });
});

// Highlight active navigation link while scrolling
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');

function highlightNavigation() {
    let current = '';
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        const sectionHeight = section.offsetHeight;
        
        if (pageYOffset >= sectionTop && pageYOffset < sectionTop + sectionHeight) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
}

// Run on scroll and on load
window.addEventListener('scroll', highlightNavigation);
window.addEventListener('load', highlightNavigation);

// Mobile menu toggle
const menuToggle = document.createElement('button');
menuToggle.className = 'menu-toggle';
menuToggle.setAttribute('aria-label', 'Toggle navigation');
menuToggle.innerHTML = '<span></span><span></span><span></span>';

document.querySelector('nav .container').prepend(menuToggle);

menuToggle.addEventListener('click', () => {
    document.body.classList.toggle('nav-open');
    menuToggle.setAttribute('aria-expanded', 
        menuToggle.getAttribute('aria-expanded') === 'true' ? 'false' : 'true'
    );
});

// Close mobile menu when clicking a link
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
        document.body.classList.remove('nav-open');
        menuToggle.setAttribute('aria-expanded', 'false');
    });
});

// Set current year in footer
document.getElementById('currentYear').textContent = new Date().getFullYear();

// Add animation on scroll
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    elements.forEach(element => {
        const elementPosition = element.getBoundingClientRect().top;
        const screenPosition = window.innerHeight / 1.2;
        
        if (elementPosition < screenPosition) {
            element.classList.add('animate');
        }
    });
};

// Run on scroll and on load
window.addEventListener('scroll', animateOnScroll);
window.addEventListener('load', animateOnScroll);
