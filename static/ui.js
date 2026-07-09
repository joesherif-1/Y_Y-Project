// Shared UI helpers: fades, page transitions, sounds, info popover, carousel.

const REDUCED_MOTION = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// ---------- Sounds (generated with the Web Audio API - no files needed) ----------
let audioCtx = null;
const SOUNDS = {
    step:   [[660, 0, 0.09]],                                // soft forward blip
    back:   [[440, 0, 0.09]],                                // lower back blip
    tick:   [[880, 0, 0.05]],                                // tiny checkbox tick
    done:   [[523, 0, 0.12], [784, 0.11, 0.18]],             // two-note success
    reveal: [[392, 0, 0.12], [523, 0.1, 0.12], [659, 0.2, 0.22]],  // rising chime
};

function playSound(kind) {
    try {
        const notes = SOUNDS[kind];
        if (!notes) return;
        audioCtx = audioCtx || new (window.AudioContext || window.webkitAudioContext)();
        if (audioCtx.state === 'suspended') audioCtx.resume();
        const t = audioCtx.currentTime;
        notes.forEach(([freq, delay, dur]) => {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.value = freq;
            gain.gain.setValueAtTime(0, t + delay);
            gain.gain.linearRampToValueAtTime(0.05, t + delay + 0.015);   // quiet!
            gain.gain.exponentialRampToValueAtTime(0.0001, t + delay + dur);
            osc.connect(gain).connect(audioCtx.destination);
            osc.start(t + delay);
            osc.stop(t + delay + dur + 0.05);
        });
    } catch (e) { /* sound is a nice-to-have, never an error */ }
}

// ---------- Fades ----------

// Fade one element out (~180ms), then fade the next in.
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
        void toEl.offsetWidth;
        toEl.classList.remove('is-fading');
        if (done) done();
    }, 180);
}

// Fade the whole white card out, run midFn (swap the content), fade back in.
function fadeThrough(midFn) {
    const card = document.querySelector('.container');
    if (REDUCED_MOTION || !card) { midFn(); return; }
    card.classList.add('card-fading');
    setTimeout(() => {
        midFn();
        void card.offsetWidth;
        card.classList.remove('card-fading');
    }, 190);
}

// Fade the card out, then navigate to a new page.
function navigateWithFade(url) {
    const card = document.querySelector('.container');
    if (REDUCED_MOTION || !card) { location.href = url; return; }
    card.classList.remove('ready');
    setTimeout(() => { location.href = url; }, 220);
}

// ---------- Info popover ----------
function setupInfoButton() {
    const btn = document.querySelector('.info-btn');
    const overlay = document.querySelector('.info-overlay');
    if (!btn || !overlay) return;
    btn.addEventListener('click', () => { playSound('tick'); overlay.hidden = false; });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay || e.target.classList.contains('info-close')) overlay.hidden = true;
    });
}

// ---------- Flash-card carousel ----------
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
        playSound('tick');
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

// ---------- Page enter/leave ----------
document.addEventListener('DOMContentLoaded', () => {
    setupInfoButton();
    const card = document.querySelector('.container');
    if (card) requestAnimationFrame(() => card.classList.add('ready'));
    // Links marked data-fade-nav leave the page with a card fade + sound.
    document.querySelectorAll('[data-fade-nav]').forEach(a => {
        a.addEventListener('click', (e) => {
            e.preventDefault();
            playSound('step');
            navigateWithFade(a.href);
        });
    });
});
