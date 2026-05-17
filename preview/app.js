(function () {
    'use strict';

    /* ---------- Navbar scrolled state ---------- */
    const navbar = document.querySelector('[data-navbar]');
    if (navbar) {
        const onScroll = () => {
            navbar.classList.toggle('is-scrolled', window.scrollY > 24);
        };
        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });
    }

    /* ---------- Mobile nav ---------- */
    const navToggle = document.querySelector('[data-nav-toggle]');
    const nav = document.querySelector('[data-nav]');
    if (navToggle && nav) {
        navToggle.addEventListener('click', () => {
            const open = nav.classList.toggle('is-open');
            navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            document.body.style.overflow = open ? 'hidden' : '';
        });
        nav.querySelectorAll('a').forEach((link) => {
            link.addEventListener('click', () => {
                nav.classList.remove('is-open');
                navToggle.setAttribute('aria-expanded', 'false');
                document.body.style.overflow = '';
            });
        });
    }

    /* ---------- Reveal on scroll ---------- */
    const revealEls = document.querySelectorAll('[data-reveal]');
    if (revealEls.length && 'IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
        revealEls.forEach((el) => io.observe(el));
    } else {
        revealEls.forEach((el) => el.classList.add('is-visible'));
    }

    /* ---------- Before/After slider ---------- */
    const compare = document.querySelector('[data-compare]');
    if (compare) {
        const after = compare.querySelector('[data-compare-after]');
        const handle = compare.querySelector('[data-compare-handle]');
        const knob = compare.querySelector('[data-compare-knob]');

        let dragging = false;

        const setPosition = (clientX) => {
            const rect = compare.getBoundingClientRect();
            let pct = ((clientX - rect.left) / rect.width) * 100;
            pct = Math.max(0, Math.min(100, pct));
            after.style.clipPath = `inset(0 ${100 - pct}% 0 0)`;
            handle.style.left = `${pct}%`;
            if (knob) knob.style.left = `${pct}%`;
            compare.setAttribute('aria-valuenow', String(Math.round(pct)));
        };

        const onStart = (e) => {
            dragging = true;
            compare.classList.add('is-dragging');
            const x = e.touches ? e.touches[0].clientX : e.clientX;
            setPosition(x);
        };
        const onMove = (e) => {
            if (!dragging) return;
            const x = e.touches ? e.touches[0].clientX : e.clientX;
            setPosition(x);
        };
        const onEnd = () => {
            dragging = false;
            compare.classList.remove('is-dragging');
        };

        compare.addEventListener('mousedown', onStart);
        compare.addEventListener('touchstart', onStart, { passive: true });
        window.addEventListener('mousemove', onMove);
        window.addEventListener('touchmove', onMove, { passive: true });
        window.addEventListener('mouseup', onEnd);
        window.addEventListener('touchend', onEnd);

        compare.setAttribute('tabindex', '0');
        compare.setAttribute('role', 'slider');
        compare.setAttribute('aria-label', 'Comparar antes e depois');
        compare.setAttribute('aria-valuemin', '0');
        compare.setAttribute('aria-valuemax', '100');
        compare.setAttribute('aria-valuenow', '50');

        compare.addEventListener('keydown', (e) => {
            const rect = compare.getBoundingClientRect();
            const current = parseFloat(handle.style.left) || 50;
            let next = current;
            if (e.key === 'ArrowLeft')  next = Math.max(0, current - 5);
            if (e.key === 'ArrowRight') next = Math.min(100, current + 5);
            if (e.key === 'Home')       next = 0;
            if (e.key === 'End')        next = 100;
            if (next !== current) {
                e.preventDefault();
                setPosition(rect.left + (rect.width * next / 100));
            }
        });
    }
})();
