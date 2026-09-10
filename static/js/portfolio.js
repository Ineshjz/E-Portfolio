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
         SUPPRESSION DU PORTFOLIO (propriétaire uniquement)
      ────────────────────────────────────────────────────────── */
    function initDeletePortfolio() {
        const btn = document.getElementById('deletePortfolioBtn');
        if (!btn) return;

        btn.addEventListener('click', async () => {
            const slug = btn.dataset.slug;
            if (!confirm('Supprimer définitivement ce portfolio ? Cette action est irréversible.')) {
                return;
            }

            btn.disabled = true;
            try {
                const res = await fetch(`/api/portfolio/${slug}`, { method: 'DELETE' });
                if (!res.ok) throw new Error();
                window.location.href = '/dashboard';
            } catch (_) {
                btn.disabled = false;
                alert('Impossible de supprimer le portfolio. Réessayez.');
            }
        });
    }

    /* ──────────────────────────────────────────────────────────
         VISIBILITÉ DU PORTFOLIO (Public / Privé) — propriétaire uniquement
      ────────────────────────────────────────────────────────── */
    function initVisibilityToggle() {
        const toggle = document.getElementById('visibilityToggle');
        if (!toggle) return;

        const label = document.getElementById('visibilityLabel');
        const shareBox = document.getElementById('shareLinkBox');

        toggle.addEventListener('change', async () => {
            const slug = toggle.dataset.slug;
            const isPublic = toggle.checked;
            toggle.disabled = true;

            try {
                const body = new URLSearchParams({ is_public: isPublic });
                const res = await fetch(`/api/portfolio/${slug}/visibility`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                    body,
                });
                if (!res.ok) throw new Error();

                if (label) {
                    label.textContent = isPublic
                        ? 'Public — visible avec le lien du portfolio'
                        : 'Privé — visible uniquement via un lien de partage';
                }
                if (shareBox) shareBox.hidden = isPublic;
            } catch (_) {
                toggle.checked = !isPublic; // revert on failure
                alert('Impossible de changer la visibilité. Réessayez.');
            } finally {
                toggle.disabled = false;
            }
        });
    }

    /* ──────────────────────────────────────────────────────────
         LIEN DE PARTAGE — copier / régénérer (propriétaire uniquement)
      ────────────────────────────────────────────────────────── */
    function initShareLink() {
        const copyBtn = document.getElementById('copyShareLinkBtn');
        const regenBtn = document.getElementById('regenerateTokenBtn');
        const input = document.getElementById('shareLinkInput');

        if (copyBtn && input) {
            copyBtn.addEventListener('click', async () => {
                try {
                    await navigator.clipboard.writeText(input.value);
                } catch (_) {
                    input.select();
                    document.execCommand('copy');
                }
                const original = copyBtn.textContent;
                copyBtn.textContent = 'Copié !';
                setTimeout(() => { copyBtn.textContent = original; }, 1500);
            });
        }

        if (regenBtn && input) {
            regenBtn.addEventListener('click', async () => {
                if (!confirm('Régénérer le lien de partage ? Tous les liens déjà distribués cesseront de fonctionner.')) {
                    return;
                }

                const slug = regenBtn.dataset.slug;
                regenBtn.disabled = true;
                try {
                    const res = await fetch(`/api/portfolio/${slug}/share-token`, { method: 'POST' });
                    if (!res.ok) throw new Error();
                    const data = await res.json();
                    input.value = data.share_url;
                } catch (_) {
                    alert('Impossible de régénérer le lien. Réessayez.');
                } finally {
                    regenBtn.disabled = false;
                }
            });
        }
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
        initDeletePortfolio();
        initVisibilityToggle();
        initShareLink();
    });

})();