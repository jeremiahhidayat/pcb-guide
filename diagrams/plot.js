// Minimal canvas plotting helper shared by the diagrams (no dependencies).
// Usage: const p = new Plot(canvas, {xLog:true, yLog:false, xRange:[1,1e6], yRange:[-60,5], xLabel:'Hz', yLabel:'dB'});
//        p.clear(); p.axes(); p.line(xs, ys, color, width); p.hline(y, color, dash)
(function () {
  function css(name) {
    return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || '#888';
  }

  function fmt(v) {
    const a = Math.abs(v);
    if (a === 0) return '0';
    const units = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'], [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
    for (const [s, p] of units) if (a >= s * 0.999) return +(v / s).toPrecision(3) + p;
    return v.toExponential(1);
  }

  class Plot {
    constructor(canvas, opts) {
      this.c = canvas;
      this.o = Object.assign({ xLog: false, yLog: false, pad: { l: 58, r: 16, t: 14, b: 40 }, xLabel: '', yLabel: '' }, opts);
      this.resize();
      window.addEventListener('resize', () => { this.resize(); if (this.onResize) this.onResize(); });
    }
    resize() {
      const dpr = window.devicePixelRatio || 1;
      const w = this.c.clientWidth || 800;
      const h = Math.max(220, Math.round(w * (this.o.aspect || 0.45)));
      this.c.style.height = h + 'px';
      this.c.width = w * dpr; this.c.height = h * dpr;
      this.ctx = this.c.getContext('2d');
      this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      this.W = w; this.H = h;
    }
    tx(x) {
      const { l, r } = this.o.pad, [a, b] = this.o.xRange;
      const t = this.o.xLog ? (Math.log10(x) - Math.log10(a)) / (Math.log10(b) - Math.log10(a)) : (x - a) / (b - a);
      return l + t * (this.W - l - r);
    }
    ty(y) {
      const { t, b } = this.o.pad, [lo, hi] = this.o.yRange;
      const u = this.o.yLog ? (Math.log10(y) - Math.log10(lo)) / (Math.log10(hi) - Math.log10(lo)) : (y - lo) / (hi - lo);
      return this.H - b - u * (this.H - t - b);
    }
    clear() {
      this.ctx.fillStyle = css('--panel');
      this.ctx.fillRect(0, 0, this.W, this.H);
    }
    ticks(range, log) {
      const [a, b] = range, out = [];
      if (log) {
        for (let e = Math.floor(Math.log10(a)); e <= Math.ceil(Math.log10(b)); e++) {
          const v = Math.pow(10, e);
          if (v >= a * 0.999 && v <= b * 1.001) out.push(v);
        }
      } else {
        const span = b - a, raw = span / 6, mag = Math.pow(10, Math.floor(Math.log10(raw)));
        const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(s => span / s <= 7);
        for (let v = Math.ceil(a / step) * step; v <= b + 1e-9; v += step) out.push(+v.toPrecision(10));
      }
      return out;
    }
    axes() {
      const ctx = this.ctx, { l, r, t, b } = this.o.pad;
      ctx.lineWidth = 1; ctx.font = '12px system-ui, sans-serif';
      ctx.strokeStyle = css('--grid'); ctx.fillStyle = css('--muted');
      // minor log grid
      if (this.o.xLog) {
        const [a, bb] = this.o.xRange;
        for (let e = Math.floor(Math.log10(a)); e < Math.ceil(Math.log10(bb)); e++)
          for (let m = 2; m < 10; m++) {
            const v = m * Math.pow(10, e);
            if (v > a && v < bb) { ctx.globalAlpha = 0.5; this._v(this.tx(v)); ctx.globalAlpha = 1; }
          }
      }
      for (const v of this.ticks(this.o.xRange, this.o.xLog)) {
        const x = this.tx(v); this._v(x);
        ctx.textAlign = 'center'; ctx.fillText(fmt(v), x, this.H - b + 16);
      }
      for (const v of this.ticks(this.o.yRange, this.o.yLog)) {
        const y = this.ty(v); ctx.beginPath(); ctx.moveTo(l, y); ctx.lineTo(this.W - r, y); ctx.stroke();
        ctx.textAlign = 'right'; ctx.fillText(fmt(v), l - 6, y + 4);
      }
      ctx.strokeStyle = css('--line'); ctx.strokeRect(l, t, this.W - l - r, this.H - t - b);
      ctx.fillStyle = css('--muted'); ctx.textAlign = 'center';
      ctx.fillText(this.o.xLabel, l + (this.W - l - r) / 2, this.H - 6);
      ctx.save(); ctx.translate(14, t + (this.H - t - b) / 2); ctx.rotate(-Math.PI / 2);
      ctx.fillText(this.o.yLabel, 0, 0); ctx.restore();
    }
    _v(x) { const { t, b } = this.o.pad; this.ctx.beginPath(); this.ctx.moveTo(x, t); this.ctx.lineTo(x, this.H - b); this.ctx.stroke(); }
    clip(fn) {
      const { l, r, t, b } = this.o.pad, ctx = this.ctx;
      ctx.save(); ctx.beginPath(); ctx.rect(l, t, this.W - l - r, this.H - t - b); ctx.clip(); fn(); ctx.restore();
    }
    line(xs, ys, color, width = 2, dash = []) {
      const ctx = this.ctx;
      this.clip(() => {
        ctx.strokeStyle = color.startsWith('--') ? css(color) : color; ctx.lineWidth = width; ctx.setLineDash(dash);
        ctx.beginPath();
        let started = false;
        for (let i = 0; i < xs.length; i++) {
          if (!isFinite(ys[i]) || (this.o.yLog && ys[i] <= 0)) { started = false; continue; }
          const X = this.tx(xs[i]), Y = this.ty(ys[i]);
          if (!started) { ctx.moveTo(X, Y); started = true; } else ctx.lineTo(X, Y);
        }
        ctx.stroke(); ctx.setLineDash([]);
      });
    }
    hline(y, color, dash = [6, 4], label) {
      this.line([this.o.xRange[0], this.o.xRange[1]], [y, y], color, 1.5, dash);
      if (label) { const c = this.ctx; c.fillStyle = css(color); c.textAlign = 'right'; c.font = '12px system-ui'; c.fillText(label, this.W - this.o.pad.r - 4, this.ty(y) - 5); }
    }
    vline(x, color, dash = [6, 4], label) {
      const ctx = this.ctx, { t, b } = this.o.pad;
      this.clip(() => {
        ctx.strokeStyle = css(color); ctx.setLineDash(dash); ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(this.tx(x), t); ctx.lineTo(this.tx(x), this.H - b); ctx.stroke(); ctx.setLineDash([]);
      });
      if (label) { ctx.fillStyle = css(color); ctx.textAlign = 'left'; ctx.font = '12px system-ui'; ctx.fillText(label, this.tx(x) + 4, t + 14); }
    }
    dot(x, y, color, r = 4) {
      const ctx = this.ctx; ctx.fillStyle = css(color); ctx.beginPath(); ctx.arc(this.tx(x), this.ty(y), r, 0, 2 * Math.PI); ctx.fill();
    }
  }

  function logspace(a, b, n) {
    const la = Math.log10(a), lb = Math.log10(b), out = [];
    for (let i = 0; i < n; i++) out.push(Math.pow(10, la + (lb - la) * i / (n - 1)));
    return out;
  }
  function linspace(a, b, n) { const out = []; for (let i = 0; i < n; i++) out.push(a + (b - a) * i / (n - 1)); return out; }

  // Re-render every plot when the OS theme changes.
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  const listeners = [];
  (mq.addEventListener ? mq.addEventListener.bind(mq, 'change') : mq.addListener.bind(mq))(() => listeners.forEach(f => f()));

  window.PCB = { Plot, fmt, css, logspace, linspace, onTheme: f => listeners.push(f) };
})();
