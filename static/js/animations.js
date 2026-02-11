// static/js/animations.js
// Modern animations for MyBiz website

document.addEventListener('alpine:init', () => {
    // Page transitions
    Alpine.data('pageTransitions', () => ({
        init() {
            this.$el.classList.add('opacity-0', 'translate-y-4');

            setTimeout(() => {
                this.$el.classList.add('transition-all', 'duration-500', 'ease-out');
                this.$el.classList.remove('opacity-0', 'translate-y-4');
            }, 100);
        }
    }));

    // Product card hover effects
    Alpine.data('productCard', () => ({
        hovering: false,
        init() {
            // Add subtle tilt effect on mouse move
            this.$el.addEventListener('mousemove', (e) => {
                if (!this.hovering) return;

                const card = this.$el;
                const cardRect = card.getBoundingClientRect();
                const centerX = cardRect.left + cardRect.width / 2;
                const centerY = cardRect.top + cardRect.height / 2;

                const mouseX = e.clientX - centerX;
                const mouseY = e.clientY - centerY;

                const rotateX = (mouseY / cardRect.height) * -10;
                const rotateY = (mouseX / cardRect.width) * 10;

                card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
            });

            this.$el.addEventListener('mouseenter', () => {
                this.hovering = true;
            });

            this.$el.addEventListener('mouseleave', () => {
                this.hovering = false;
                this.$el.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
            });
        }
    }));

    // Parallax scrolling effect
    Alpine.data('parallax', (speed = 0.5) => ({
        init() {
            window.addEventListener('scroll', () => {
                const scrolled = window.pageYOffset;
                const rate = scrolled * speed;
                this.$el.style.transform = `translateY(${rate}px)`;
            });
        }
    }));

    // Smooth scroll to anchor links
    Alpine.data('smoothScroll', (offset = 80) => ({
        init() {
            this.$el.addEventListener('click', (e) => {
                const href = this.$el.getAttribute('href');

                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    const targetId = href.substring(1);
                    const targetElement = document.getElementById(targetId);

                    if (targetElement) {
                        window.scrollTo({
                            top: targetElement.offsetTop - offset,
                            behavior: 'smooth'
                        });
                    }
                }
            });
        }
    }));

    // Sticky header on scroll
    Alpine.data('stickyHeader', (threshold = 100) => ({
        sticky: false,
        init() {
            window.addEventListener('scroll', () => {
                this.sticky = window.scrollY > threshold;

                if (this.sticky) {
                    this.$el.classList.add('sticky', 'shadow-lg');
                } else {
                    this.$el.classList.remove('sticky', 'shadow-lg');
                }
            });
        }
    }));

    // Modal/popup functionality
    Alpine.data('modal', () => ({
        open: false,
        toggle() {
            this.open = !this.open;

            if (this.open) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        },
        close() {
            this.open = false;
            document.body.style.overflow = '';
        }
    }));

    // Dropdown menu functionality
    Alpine.data('dropdown', () => ({
        open: false,
        toggle() {
            this.open = !this.open;
        },
        close() {
            this.open = false;
        }
    }));

    // Tab switching functionality
    Alpine.data('tabs', (defaultTab = 0) => ({
        activeTab: defaultTab,
        tabs: [],
        init() {
            // Get all tab elements
            this.tabs = Array.from(this.$el.querySelectorAll('[data-tab]'));

            // Show default tab
            this.showTab(this.activeTab);
        },
        showTab(index) {
            this.activeTab = index;

            // Hide all tabs
            this.tabs.forEach(tab => {
                tab.classList.add('hidden');
            });

            // Show active tab
            this.tabs[index].classList.remove('hidden');
        }
    }));

    // Accordion functionality
    Alpine.data('accordion', () => ({
        open: false,
        toggle() {
            this.open = !this.open;
        }
    }));

    // Form validation
    Alpine.data('formValidation', () => ({
        errors: {},
        submitting: false,

        validateField(field, value) {
            // Clear previous error
            delete this.errors[field];

            // Email validation
            if (field === 'email' && value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(value)) {
                    this.errors[field] = 'Введите корректный email';
                }
            }

            // Required field validation
            if (field === 'name' && !value) {
                this.errors[field] = 'Имя обязательно для заполнения';
            }
        },

        async submitForm() {
            this.submitting = true;

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1500));

            this.submitting = false;
            return true;
        }
    }));

    // Cart functionality (simplified for showcase)
    Alpine.data('cart', () => ({
        items: [],
        total: 0,

        init() {
            // Load cart from localStorage
            const savedCart = localStorage.getItem('mybiz_cart');
            if (savedCart) {
                const cartData = JSON.parse(savedCart);
                this.items = cartData.items || [];
                this.total = cartData.total || 0;
            }
        },

        addItem(product) {
            const existingItem = this.items.find(item => item.id === product.id);

            if (existingItem) {
                existingItem.quantity += 1;
            } else {
                this.items.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    image: product.image,
                    quantity: 1
                });
            }

            this.updateTotal();
            this.saveCart();
        },

        removeItem(productId) {
            this.items = this.items.filter(item => item.id !== productId);
            this.updateTotal();
            this.saveCart();
        },

        updateQuantity(productId, quantity) {
            const item = this.items.find(item => item.id === productId);
            if (item) {
                item.quantity = quantity;
                if (item.quantity <= 0) {
                    this.removeItem(productId);
                } else {
                    this.updateTotal();
                    this.saveCart();
                }
            }
        },

        updateTotal() {
            this.total = this.items.reduce((sum, item) => {
                return sum + (item.price * item.quantity);
            }, 0);
        },

        saveCart() {
            localStorage.setItem('mybiz_cart', JSON.stringify({
                items: this.items,
                total: this.total
            }));
        },

        clearCart() {
            this.items = [];
            this.total = 0;
            localStorage.removeItem('mybiz_cart');
        }
    }));

    // Search functionality
    Alpine.data('search', () => ({
        query: '',
        results: [],
        searching: false,

        async searchProducts() {
            if (!this.query.trim()) {
                this.results = [];
                return;
            }

            this.searching = true;

            try {
                // Simulate API call
                await new Promise(resolve => setTimeout(resolve, 500));

                // In a real app, this would be an actual API call
                // For now, we'll use a mock response
                this.results = [
                    { id: 1, name: 'Товар 1', price: 1000, url: '/products/tovar-1' },
                    { id: 2, name: 'Товар 2', price: 2000, url: '/products/tovar-2' },
                    { id: 3, name: 'Товар 3', price: 3000, url: '/products/tovar-3' }
                ];
            } catch (error) {
                console.error('Search error:', error);
                this.results = [];
            } finally {
                this.searching = false;
            }
        },

        clearSearch() {
            this.query = '';
            this.results = [];
        }
    }));

    // Image gallery with lightbox
    Alpine.data('gallery', () => ({
        images: [],
        currentIndex: 0,
        lightboxOpen: false,

        init() {
            // Get all gallery images
            this.images = Array.from(this.$el.querySelectorAll('[data-gallery-image]'));

            // Add click handlers
            this.images.forEach((img, index) => {
                img.addEventListener('click', () => {
                    this.openLightbox(index);
                });
            });
        },

        openLightbox(index) {
            this.currentIndex = index;
            this.lightboxOpen = true;
            document.body.style.overflow = 'hidden';
        },

        closeLightbox() {
            this.lightboxOpen = false;
            document.body.style.overflow = '';
        },

        nextImage() {
            this.currentIndex = (this.currentIndex + 1) % this.images.length;
        },

        prevImage() {
            this.currentIndex = (this.currentIndex - 1 + this.images.length) % this.images.length;
        },

        goToImage(index) {
            this.currentIndex = index;
        }
    }));

    // Product quick view
    Alpine.data('quickView', (product) => ({
        open: false,
        product: product,

        toggle() {
            this.open = !this.open;

            if (this.open) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        }
    }));

    // Wishlist functionality
    Alpine.data('wishlist', () => ({
        items: [],

        init() {
            // Load wishlist from localStorage
            const savedWishlist = localStorage.getItem('mybiz_wishlist');
            if (savedWishlist) {
                this.items = JSON.parse(savedWishlist);
            }
        },

        toggleItem(product) {
            const index = this.items.findIndex(item => item.id === product.id);

            if (index === -1) {
                this.items.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    image: product.image
                });
            } else {
                this.items.splice(index, 1);
            }

            this.saveWishlist();
        },

        isInWishlist(productId) {
            return this.items.some(item => item.id === productId);
        },

        saveWishlist() {
            localStorage.setItem('mybiz_wishlist', JSON.stringify(this.items));
        },

        clearWishlist() {
            this.items = [];
            localStorage.removeItem('mybiz_wishlist');
        }
    }));

    // Notification system
    Alpine.data('notifications', () => ({
        messages: [],
        timeout: 5000,

        add(message, type = 'info') {
            const id = Date.now();
            const notification = {
                id,
                message,
                type,
                visible: true
            };

            this.messages.push(notification);

            // Auto remove after timeout
            setTimeout(() => {
                this.remove(id);
            }, this.timeout);
        },

        remove(id) {
            const index = this.messages.findIndex(msg => msg.id === id);
            if (index !== -1) {
                this.messages.splice(index, 1);
            }
        },

        success(message) {
            this.add(message, 'success');
        },

        error(message) {
            this.add(message, 'error');
        },

        warning(message) {
            this.add(message, 'warning');
        },

        info(message) {
            this.add(message, 'info');
        }
    }));

    // Currency formatting
    Alpine.data('currency', () => ({
        format(amount, currency = 'RUB') {
            return new Intl.NumberFormat('ru-RU', {
                style: 'currency',
                currency: currency,
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(amount);
        }
    }));

    // Date formatting
    Alpine.data('dateFormat', () => ({
        format(date, format = 'dd.MM.yyyy') {
            const d = new Date(date);

            const day = d.getDate().toString().padStart(2, '0');
            const month = (d.getMonth() + 1).toString().padStart(2, '0');
            const year = d.getFullYear();

            return format
                .replace('dd', day)
                .replace('MM', month)
                .replace('yyyy', year);
        }
    }));

    // ==============================================
    // Кастомная директива x-observe вместо x-intersect
    // ==============================================

    // Создаем кастомную директиву x-observe
    Alpine.directive('observe', (el, { value, expression, modifiers }, { evaluate, evaluateLater, cleanup }) => {
        // Парсим опции из модификаторов
        const options = {
            threshold: modifiers.includes('half') ? 0.5 : 0.1,
            rootMargin: modifiers.includes('margin') ? '50px' : '0px'
        };

        // Если есть параметр в value, например x-observe="0.3"
        if (value) {
            try {
                const threshold = parseFloat(value);
                if (!isNaN(threshold)) {
                    options.threshold = threshold;
                }
            } catch (e) {
                console.warn('Invalid threshold value for x-observe:', value);
            }
        }

        // Компилируем выражение для многократного использования
        const evaluateExpression = evaluateLater(expression);

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Выполняем выражение Alpine
                    evaluateExpression();

                    // Останавливаем наблюдение, если нужно
                    if (modifiers.includes('once')) {
                        observer.unobserve(el);
                    }

                    // Также можно выполнить действие при выходе из viewport
                    if (modifiers.includes('leave')) {
                        entry.target._wasIntersected = true;
                    }
                } else if (modifiers.includes('leave') && entry.target._wasIntersected) {
                    // Выполняем действие при выходе из viewport
                    const leaveExpression = expression.replace('=', ' = false');
                    try {
                        evaluate(leaveExpression);
                    } catch (e) {
                        console.warn('Could not evaluate leave expression:', leaveExpression);
                    }
                }
            });
        }, options);

        observer.observe(el);

        // Очистка при удалении элемента
        cleanup(() => {
            observer.disconnect();
        });
    });

    // Также добавляем упрощенную версию для счетчиков
    Alpine.data('counterAnimation', (initialValue = 0, targetValue = 100, duration = 2000) => ({
        value: initialValue,
        init() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.animateCounter(targetValue, duration);
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.5 });

            observer.observe(this.$el);
        },
        animateCounter(target, duration) {
            const startTime = Date.now();
            const startValue = this.value;
            const difference = target - startValue;

            const updateCounter = () => {
                const elapsed = Date.now() - startTime;
                const progress = Math.min(elapsed / duration, 1);

                // Easing function for smooth animation
                const easeOutQuart = 1 - Math.pow(1 - progress, 4);
                this.value = Math.floor(easeOutQuart * difference + startValue);

                if (progress < 1) {
                    requestAnimationFrame(updateCounter);
                }
            };

            updateCounter();
        }
    }));
});

// Дополнительные глобальные анимации и эффекты
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем все анимации при загрузке страницы

    // Добавляем анимацию загрузки для всех карточек с задержкой
    const cards = document.querySelectorAll('.card-modern');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Инициализируем всплывающие подсказки
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltipElement = document.createElement('div');
            tooltipElement.className = 'fixed z-50 px-3 py-2 text-sm bg-gray-900 text-white rounded-lg shadow-lg';
            tooltipElement.textContent = tooltipText;
            document.body.appendChild(tooltipElement);

            const rect = this.getBoundingClientRect();
            tooltipElement.style.left = `${rect.left + rect.width / 2}px`;
            tooltipElement.style.top = `${rect.top - tooltipElement.offsetHeight - 10}px`;
            tooltipElement.style.transform = 'translateX(-50%)';

            this._tooltipElement = tooltipElement;
        });

        tooltip.addEventListener('mouseleave', function() {
            if (this._tooltipElement) {
                this._tooltipElement.remove();
                delete this._tooltipElement;
            }
        });
    });

    // Добавляем эффект ряби на кнопки
    const buttons = document.querySelectorAll('.btn-modern');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;

            ripple.style.width = ripple.style.height = `${size}px`;
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            ripple.className = 'ripple-effect';

            this.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Добавляем CSS для эффекта ряби
    const style = document.createElement('style');
    style.textContent = `
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.6);
            transform: scale(0);
            animation: ripple-animation 0.6s linear;
        }

        @keyframes ripple-animation {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Ленивая загрузка изображений с Intersection Observer
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const src = img.getAttribute('data-src');

                if (src) {
                    img.src = src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            }
        });
    }, { rootMargin: '50px' });

    lazyImages.forEach(img => imageObserver.observe(img));

    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            if (href === '#') return;

            const targetElement = document.querySelector(href);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Добавляем индикатор прогресса прокрутки
    const progressBar = document.createElement('div');
    progressBar.className = 'fixed top-0 left-0 z-50 h-1 bg-gradient-to-r from-primary to-secondary transform origin-left';
    progressBar.style.width = '0%';
    document.body.appendChild(progressBar);

    window.addEventListener('scroll', () => {
        const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
        const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const scrolled = (winScroll / height) * 100;
        progressBar.style.width = scrolled + '%';
    });

    // Добавляем сочетания клавиш
    document.addEventListener('keydown', (e) => {
        // Фокусировка на поисковом поле по Ctrl+K или Cmd+K
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="search"], input[name="q"]');
            if (searchInput) {
                searchInput.focus();
            }
        }

        // Клавиша Escape закрывает модальные окна
        if (e.key === 'Escape') {
            const openModals = document.querySelectorAll('[x-data*="modal"][x-show="open"]');
            openModals.forEach(modal => {
                const alpineComponent = Alpine.$data(modal);
                if (alpineComponent && alpineComponent.close) {
                    alpineComponent.close();
                }
            });
        }
    });

    // Мониторинг производительности
    if (window.performance) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perf = performance.getEntriesByType('navigation')[0];
                const loadTime = perf.loadEventEnd - perf.startTime;

                console.log(`Page loaded in ${loadTime.toFixed(2)}ms`);

                // Отправляем в аналитику, если нужно
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'timing_complete', {
                        name: 'page_load',
                        value: Math.round(loadTime),
                        event_category: 'Performance'
                    });
                }
            }, 0);
        });
    }

    // Добавляем viewport units для мобильных браузеров
    function setViewportHeight() {
        const vh = window.innerHeight * 0.01;
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    setViewportHeight();
    window.addEventListener('resize', setViewportHeight);
});

// Экспорт для использования в модулях, если нужно
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        animations: Alpine
    };

}
