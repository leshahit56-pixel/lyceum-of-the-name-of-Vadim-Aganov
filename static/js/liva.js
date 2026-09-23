// Общие скрипты оформления ЛиВА: тема, дата в шапке, рисунки на полях, след курсора.
(function () {
    const body = document.body;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // ---------- Тема: «бумага» / «доска» ----------
    function applyTheme(theme) {
        body.classList.toggle('dark', theme === 'dark');
        try {
            localStorage.setItem('theme', theme);
        } catch (e) {}
    }

    // оставлено глобальным: старые шаблоны вызывают setTheme('dark')
    window.setTheme = function (theme) {
        if (document.startViewTransition && !reduceMotion) {
            document.startViewTransition(() => applyTheme(theme));
        } else {
            applyTheme(theme);
        }
    };

    const switcher = document.getElementById('themeSwitch');
    if (switcher) {
        switcher.addEventListener('click', () => {
            window.setTheme(body.classList.contains('dark') ? 'light' : 'dark');
        });
    }

    // ---------- Дата, как в школьной тетради ----------
    const dateEl = document.querySelector('[data-date]');
    if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' });
    }

    // ---------- Клик по подписи варианта ответа выбирает его ----------
    document.addEventListener('click', (e) => {
        const label = e.target.closest('.form-check label');
        if (!label || label.htmlFor) return;
        const input = label.parentElement.querySelector('.form-check-input');
        if (input) input.click();
    });

    // ---------- Рисунки на полях слегка следуют за мышью ----------
    const doodles = document.querySelector('.doodles');
    if (doodles && !reduceMotion) {
        window.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth - 0.5) * -14;
            const y = (e.clientY / window.innerHeight - 0.5) * -10;
            doodles.style.setProperty('--px', x.toFixed(1) + 'px');
            doodles.style.setProperty('--py', y.toFixed(1) + 'px');
        }, { passive: true });
    }

    // ---------- След курсора: карандаш на бумаге, мел на доске ----------
    const canvas = document.getElementById('trail');
    const finePointer = window.matchMedia('(pointer: fine)').matches;
    if (!canvas || reduceMotion || !finePointer) return;

    const ctx = canvas.getContext('2d');
    const points = [];
    const LIFE = 650;
    let dpr = 1;
    let running = false;

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = window.innerWidth * dpr;
        canvas.height = window.innerHeight * dpr;
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    resize();
    window.addEventListener('resize', resize);

    window.addEventListener('mousemove', (e) => {
        points.push({ x: e.clientX, y: e.clientY, t: performance.now() });
        if (!running) {
            running = true;
            requestAnimationFrame(frame);
        }
    }, { passive: true });

    function frame(now) {
        ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        while (points.length && now - points[0].t > LIFE) points.shift();

        const chalk = body.classList.contains('dark');
        for (let i = 1; i < points.length; i++) {
            const a = points[i - 1];
            const b = points[i];
            const life = 1 - (now - b.t) / LIFE;
            if (chalk) {
                // мел: неровная, крошащаяся линия
                ctx.strokeStyle = `rgba(236, 232, 219, ${0.22 * life})`;
                ctx.lineWidth = 3.2 * life + 0.6;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
                if (Math.random() < 0.35) {
                    ctx.fillStyle = `rgba(236, 232, 219, ${0.3 * life})`;
                    ctx.fillRect(b.x + (Math.random() - 0.5) * 8, b.y + (Math.random() - 0.5) * 8, 1.4, 1.4);
                }
            } else {
                // карандаш: тонкий графитовый штрих
                ctx.strokeStyle = `rgba(52, 60, 78, ${0.32 * life})`;
                ctx.lineWidth = 1.3;
                ctx.lineCap = 'round';
                ctx.beginPath();
                ctx.moveTo(a.x, a.y);
                ctx.lineTo(b.x, b.y);
                ctx.stroke();
            }
        }

        if (points.length) {
            requestAnimationFrame(frame);
        } else {
            running = false;
            ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
        }
    }
})();
