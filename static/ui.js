// Shared UI helpers: fade transitions, info popover, flash-card carousel.

const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Fade one element out (~180ms), then fade the next in. Fast and clean.
function fadeSwap(fromEl, toEl, done) {
    if (REDUCED_MOTION || !fromEl) {
        if (fromEl) fromEl.hidden = true;
        toEl.hidden = false;
        if (done) done();
        return;
    }
    fromEl.classList.add('is-fading');
    setTimeout(() => {
        fromEl.hidden = true;
        fromEl.classList.remove('is-fading');
        toEl.classList.add('is-fading');
        toEl.hidden = false;
        void toEl.offsetWidth;   // force reflow so the fade-in animates
        toEl.classList.remove('is-fading');
        if (done) done();
    }, 180);
}

// Info popover: the (i) button toggles the overlay; clicking outside or x closes it.
function setupInfoButton() {
    const btn = document.querySelector('.info-btn');
    const overlay = document.querySelector('.info-overlay');
    if (!btn || !overlay) return;
    btn.addEventListener('click', () => { overlay.hidden = false; });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay || e.target.classList.contains('info-close')) overlay.hidden = true;
    });
}

// Flash-card carousel: scroll-snap track + dots + prev/next arrows.
function setupCarousel(container) {
    const track = container.querySelector('.cards-track');
    const cards = [...track.children];
    const dotsBox = container.querySelector('.cards-dots');
    cards.forEach((_, i) => {
        const d = document.createElement('button');
        d.className = 'dot' + (i === 0 ? ' active' : '');
        d.setAttribute('aria-label', 'Card ' + (i + 1));
        d.addEventListener('click', () => scrollToCard(i));
        dotsBox.appendChild(d);
    });
    const dots = [...dotsBox.children];

    function scrollToCard(i) {
        track.scrollTo({ left: cards[i].offsetLeft, behavior: REDUCED_MOTION ? 'auto' : 'smooth' });
    }
    function currentCard() {
        const center = track.scrollLeft + track.clientWidth / 2;
        let best = 0;
        cards.forEach((c, i) => {
            const cCenter = c.offsetLeft + c.clientWidth / 2;
            const bCenter = cards[best].offsetLeft + cards[best].clientWidth / 2;
            if (Math.abs(cCenter - center) < Math.abs(bCenter - center)) best = i;
        });
        return best;
    }
    track.addEventListener('scroll', () => {
        const i = currentCard();
        dots.forEach((d, j) => d.classList.toggle('active', j === i));
    }, { passive: true });
    container.querySelector('.cards-prev').addEventListener('click',
        () => scrollToCard(Math.max(0, currentCard() - 1)));
    container.querySelector('.cards-next').addEventListener('click',
        () => scrollToCard(Math.min(cards.length - 1, currentCard() + 1)));
}

document.addEventListener('DOMContentLoaded', setupInfoButton);
