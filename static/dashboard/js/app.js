/* ============================================
   BCA FINTECH DASHBOARD - APP
   Main application controller
   ============================================ */

   class BCADashboard {
    constructor() {
      this.state = {
        currentView: 'overview',
        currency: 'USD',
        notifications: 2,
        chartPeriod: 'week'
      };
      
      this.init();
    }
  
    init() {
      this.initSkeletonLoading();
      this.initTabSwitching();
      this.initCurrencyDropdown();
      this.initNotificationBadge();
      this.initScrollEffects();
    }
  
    // Skeleton loading simulation
    initSkeletonLoading() {
      const skeletonContainers = document.querySelectorAll('[data-skeleton]');
      
      skeletonContainers.forEach(container => {
        container.classList.add('skeleton-loading');
        
        // Simulate data load
        setTimeout(() => {
          container.classList.remove('skeleton-loading');
          container.classList.add('content-loaded');
        }, 800 + Math.random() * 600);
      });
    }
  
    // Tab switching for statistics
    initTabSwitching() {
      const tabs = document.querySelectorAll('.tab');
      
      tabs.forEach(tab => {
        tab.addEventListener('click', () => {
          tabs.forEach(t => t.classList.remove('tab--active'));
          tab.classList.add('tab--active');
          
          const period = tab.dataset.period;
          this.state.chartPeriod = period;
          
          // Animate chart refresh
          const chart = document.querySelector('.statistics-section__chart-wrapper');
          if (chart) {
            chart.style.opacity = '0';
            chart.style.transform = 'scale(0.98)';
            
            setTimeout(() => {
              chart.style.transition = 'all 0.4s cubic-bezier(0.25, 0.1, 0.25, 1)';
              chart.style.opacity = '1';
              chart.style.transform = 'scale(1)';
              
              // Regenerate chart data
              if (window.spendingChart) {
                window.spendingChart.data = this.generateChartData(period);
                window.spendingChart.render();
                window.spendingChart.animate();
              }
            }, 200);
          }
        });
      });
    }
  
    generateChartData(period) {
      const baseValues = {
        day: [1200, 800, 1500, 600, 900],
        week: [820, 650, 1200.43, 580, 920],
        month: [3200, 2800, 4100, 2600, 3500],
        year: [45000, 38000, 52000, 41000, 48000]
      };
      
      const labels = {
        day: ['6 AM', '10 AM', '2 PM', '6 PM', '10 PM'],
        week: ['Thu 27', 'Tue 25', 'Wed 26', 'Fri 28', 'Sat 29'],
        month: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'],
        year: ['Q1', 'Q2', 'Q3', 'Q4', 'Total']
      };
      
      const values = baseValues[period] || baseValues.week;
      const dayLabels = labels[period] || labels.week;
      
      return values.map((v, i) => ({
        day: dayLabels[i],
        value: v,
        label: 'Spent',
        amount: `$${v.toLocaleString('en-US', { minimumFractionDigits: 2 })}`
      }));
    }
  
    // Currency dropdown
    initCurrencyDropdown() {
      const currencyBtn = document.querySelector('.main-header__currency');
      if (!currencyBtn) return;
      
      currencyBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        
        // Remove existing dropdown
        document.querySelectorAll('.currency-dropdown').forEach(d => d.remove());
        
        const dropdown = document.createElement('div');
        dropdown.className = 'currency-dropdown dropdown-animate';
        dropdown.style.cssText = `
          position: absolute;
          top: 100%;
          right: 0;
          margin-top: 8px;
          background: white;
          border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.12);
          padding: 8px;
          min-width: 140px;
          z-index: 100;
        `;
        
        const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'IDR'];
        dropdown.innerHTML = currencies.map(c => `
          <div class="currency-option" style="
            padding: 8px 12px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            transition: background 0.15s;
            ${c === this.state.currency ? 'font-weight: 600; background: #f5f5f5;' : ''}
          ">${c}</div>
        `).join('');
        
        dropdown.querySelectorAll('.currency-option').forEach(opt => {
          opt.addEventListener('click', () => {
            this.state.currency = opt.textContent;
            currencyBtn.querySelector('span').textContent = `${opt.textContent} `;
            dropdown.remove();
          });
          opt.addEventListener('mouseenter', () => {
            if (opt.textContent !== this.state.currency) {
              opt.style.background = '#f5f5f5';
            }
          });
          opt.addEventListener('mouseleave', () => {
            if (opt.textContent !== this.state.currency) {
              opt.style.background = 'transparent';
            }
          });
        });
        
        currencyBtn.style.position = 'relative';
        currencyBtn.appendChild(dropdown);
      });
      
      document.addEventListener('click', () => {
        document.querySelectorAll('.currency-dropdown').forEach(d => d.remove());
      });
    }
  
    // Notification badge animation
    initNotificationBadge() {
      const badge = document.querySelector('.panel-header__action-badge');
      if (badge && this.state.notifications > 0) {
        setInterval(() => {
          badge.classList.add('badge-bounce');
          setTimeout(() => badge.classList.remove('badge-bounce'), 300);
        }, 5000);
      }
    }
  
    // Scroll-based effects
    initScrollEffects() {
      const main = document.querySelector('.main');
      if (!main) return;
      
      let lastScroll = 0;
      
      main.addEventListener('scroll', () => {
        const currentScroll = main.scrollTop;
        const direction = currentScroll > lastScroll ? 'down' : 'up';
        
        // Parallax effect on chart
        const chart = document.querySelector('.statistics-section__chart-wrapper');
        if (chart && currentScroll < 300) {
          chart.style.transform = `translateY(${currentScroll * 0.02}px)`;
        }
        
        lastScroll = currentScroll;
      });
    }
  }
  
  // Initialize app
  document.addEventListener('DOMContentLoaded', () => {
    window.bcaApp = new BCADashboard();
  });