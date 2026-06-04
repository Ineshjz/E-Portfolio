/**
 * PORTFOLIO.JS
 * Animations et interactions de la page ePortfolio générée.
 *
 * Fonctionnalités :
 *  - Fade-up au scroll via IntersectionObserver
 *  - Count-up animé sur les stats du hero (Skills / Projects / Keywords)
 *  - Effet cascade (stagger) sur les skill chips
 *  - Effet cascade (stagger) sur les lignes de projets
 *  - Clic sur toute la ligne d'un projet pour ouvrir l'URL
 */

(function () {
    'use strict';

    /* ── FADE-UP OBSERVER ── */
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.08 }
    );

    function observeAll() {
        document.querySelectorAll('.fade-up:not(.visible)').forEach((el) => {
            observer.observe(el);
        });
    }

    document.addEventListener('DOMContentLoaded', observeAll);
    document.body.addEventListener('htmx:afterSwap', observeAll);

    /* ── COUNT-UP STATS ── */
    function countUp(el, target, duration) {
        if (!el || target === 0) return;
        const step = duration / target;
        let current = 0;
        const timer = setInterval(() => {
            current += 1;
            el.textContent = current;
            if (current >= target) clearInterval(timer);
        }, step);
    }

    function initStatsCountUp() {
        const statNumbers = document.querySelectorAll('.stat-n');
        if (!statNumbers.length) return;
        const targets = Array.from(statNumbers).map((el) => parseInt(el.textContent, 10) || 0);
        statNumbers.forEach((el) => (el.textContent = '0'));
        const heroRight = document.querySelector('.hero-right');
        if (!heroRight) return;
        const obs = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        statNumbers.forEach((el, i) => {
                            setTimeout(() => countUp(el, targets[i], 600), i * 80);
                        });
                        obs.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.3 }
        );
        obs.observe(heroRight);
    }

    /* ── STAGGER SKILLS ── */
    function initSkillsStagger() {
        const chips = document.querySelectorAll('.skill-chip');
        chips.forEach((chip, i) => {
            chip.style.transitionDelay = `${i * 0.04}s`;
        });
    }

    /* ── STAGGER PROJECTS ── */
    function initProjectsStagger() {
        const items = document.querySelectorAll('.proj-item');
        items.forEach((item, i) => {
            item.style.transitionDelay = `${i * 0.07}s`;
        });
    }

    /* ──────────────────────────────────────────────────────────
         CLIC SUR LES LIGNES DE PROJET
      ────────────────────────────────────────────────────────── */
    function initProjectLinks() {
        document.querySelectorAll('.proj-item[data-url]').forEach((item) => {
            item.addEventListener('click', () => {
                const url = item.dataset.url;
                if (url) window.open(url, '_blank', 'noopener');
            });
        });
    }

    /* ──────────────────────────────────────────────────────────
          INITIALISATION
          Lance toutes les fonctions après le chargement du DOM.
       ────────────────────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', () => {
        initStatsCountUp();
        initSkillsStagger();
        initProjectsStagger();
        initProjectLinks();
    });

})();