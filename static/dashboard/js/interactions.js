/* ============================================
   BCA FINTECH DASHBOARD - INTERACTIONS
   Premium micro-interactions and effects
   ============================================ */

   class Interactions {
    constructor() {
      this.initRipples();
      this.initCounters();
      this.initLazyLoad();
      this.initTooltips();
      this.initCardEffects();
    }
  
    // Ripple effect on buttons
    initRipples() {
      document.querySelectorAll('.btn, .transaction-card, .limit-card').forEach(el => {
        el.addEventListener('click', (e) => {
          const rect = el.getBoundingClientRect();
          const x = ((e.clientX - rect.left) / rect.width) * 100;
          const y = ((e.clientY - rect.top) / rect.height) * 100;
          el.style.setProperty('--ripple-x', `${x}%`);
          el.style.setProperty('--ripple-y', `${y}%`);
        });
      });
    }
  
    // Animated counters
    initCounters() {
      const counters = document.querySelectorAll('[data-counter]');
      
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            this.animateCounter(entry.target);
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.5 });
  
      counters.forEach(counter => observer.observe(counter));
    }
  
    animateCounter(element) {
      const target = parseFloat(element.dataset.counter);
      const prefix = element.dataset.prefix || '';
      const suffix = element.dataset.suffix || '';
      const duration = parseInt(element.dataset.duration) || 1500;
      const decimals = parseInt(element.dataset.decimals) || 2;
      
      const startTime = performance.now();
      
      const update = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        
        const current = target * eased;
        element.textContent = prefix + current.toFixed(decimals) + suffix;
        
        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          element.textContent = prefix + target.toFixed(decimals) + suffix;
        }
      };
      
      requestAnimationFrame(update);
    }
  
    // Lazy loading for images
    initLazyLoad() {
      const lazyElements = document.querySelectorAll('[data-lazy]');
      
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const el = entry.target;
            el.src = el.dataset.lazy;
            el.removeAttribute('data-lazy');
            el.classList.add('loaded');
            imageObserver.unobserve(el);
          }
        });
      });
  
      lazyElements.forEach(el => imageObserver.observe(el));
    }
  
    // Custom tooltips
    initTooltips() {
      document.querySelectorAll('[data-tooltip]').forEach(el => {
        el.addEventListener('mouseenter', (e) => this.showTooltip(e, el));
        el.addEventListener('mouseleave', () => this.hideTooltip());
      });
    }
  
    showTooltip(e, element) {
      const text = element.dataset.tooltip;
      const tooltip = document.createElement('div');
      tooltip.className = 'custom-tooltip';
      tooltip.textContent = text;
      tooltip.style.cssText = `
        position: fixed;
        background: #1a1a1a;
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 11px;
        pointer-events: none;
        z-index: 1000;
        opacity: 0;
        transform: translateY(4px);
        transition: all 0.2s ease;
      `;
      
      document.body.appendChild(tooltip);
      
      const rect = element.getBoundingClientRect();
      tooltip.style.left = `${rect.left + rect.width / 2 - tooltip.offsetWidth / 2}px`;
      tooltip.style.top = `${rect.top - tooltip.offsetHeight - 8}px`;
      
      requestAnimationFrame(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
      });
      
      element._tooltip = tooltip;
    }
  
    hideTooltip() {
      document.querySelectorAll('.custom-tooltip').forEach(t => t.remove());
    }
  
    // 3D card tilt effect
    initCardEffects() {
      document.querySelectorAll('.credit-card').forEach(card => {
        card.addEventListener('mousemove', (e) => {
          const rect = card.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          
          const rotateX = (y - centerY) / 20;
          const rotateY = (centerX - x) / 20;
          
          card.style.transform = `perspective(500px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', () => {
          card.style.transform = '';
        });
      });
    }
  }
  
  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    window.interactions = new Interactions();
  });