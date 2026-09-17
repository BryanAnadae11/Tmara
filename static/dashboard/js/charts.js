/* ============================================
   BCA FINTECH DASHBOARD - CHARTS
   Handcrafted SVG statistics visualization
   ============================================ */

   class SpendingChart {
    constructor(containerId, data) {
      this.container = document.getElementById(containerId);
      this.data = data || [
        { day: 'Thu 27', value: 820, label: 'Spent', amount: '$820.50' },
        { day: 'Tue 25', value: 650, label: 'Spent', amount: '$650.20' },
        { day: 'Wed 26', value: 1200.43, label: 'Spent', amount: '$1,200.43' },
        { day: 'Fri 28', value: 580, label: 'Spent', amount: '$580.00' },
        { day: 'Sat 29', value: 920, label: 'Spent', amount: '$920.75' }
      ];
      this.activeIndex = 2; // Wed 26 (highest point)
      this.init();
    }
  
    init() {
      this.render();
      this.animate();
    }
  
    getPathPoints() {
      const width = 400;
      const height = 140;
      const padding = 20;
      const chartWidth = width - padding * 2;
      const chartHeight = height - padding * 2;
      
      const max = Math.max(...this.data.map(d => d.value));
      const min = Math.min(...this.data.map(d => d.value));
      const range = max - min || 1;
      
      return this.data.map((point, i) => ({
        x: padding + (i / (this.data.length - 1)) * chartWidth,
        y: padding + chartHeight - ((point.value - min) / range) * chartHeight,
        ...point
      }));
    }
  
    generateSmoothPath(points) {
      if (points.length < 2) return '';
      
      let path = `M ${points[0].x},${points[0].y}`;
      
      for (let i = 0; i < points.length - 1; i++) {
        const p0 = points[i === 0 ? 0 : i - 1];
        const p1 = points[i];
        const p2 = points[i + 1];
        const p3 = points[i + 2] || p2;
        
        const tension = 0.3;
        
        const cp1x = p1.x + (p2.x - p0.x) * tension;
        const cp1y = p1.y + (p2.y - p0.y) * tension;
        const cp2x = p2.x - (p3.x - p1.x) * tension;
        const cp2y = p2.y - (p3.y - p1.y) * tension;
        
        path += ` C ${cp1x},${cp1y} ${cp2x},${cp2y} ${p2.x},${p2.y}`;
      }
      
      return path;
    }
  
    render() {
      const points = this.getPathPoints();
      const pathD = this.generateSmoothPath(points);
      const activePoint = points[this.activeIndex];
      
      // Create area path by closing the bottom
      const areaD = `${pathD} L ${points[points.length - 1].x},180 L ${points[0].x},180 Z`;
      
      this.container.innerHTML = `
        <svg viewBox="0 0 400 180" preserveAspectRatio="none" class="chart-svg">
          <defs>
            <linearGradient id="chartAreaGrad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#8c735d" stop-opacity="0.18"/>
              <stop offset="50%" stop-color="#8c735d" stop-opacity="0.06"/>
              <stop offset="100%" stop-color="#8c735d" stop-opacity="0"/>
            </linearGradient>
            <filter id="chartGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur"/>
              <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <!-- Grid lines -->
          ${[0, 1, 2, 3, 4].map(i => {
            const y = 30 + i * 30;
            return `<line x1="20" y1="${y}" x2="380" y2="${y}" stroke="rgba(0,0,0,0.04)" stroke-width="1" stroke-dasharray="4,6"/>`;
          }).join('')}
          
          <!-- Vertical guides -->
          ${points.map((p, i) => 
            `<line x1="${p.x}" y1="20" x2="${p.x}" y2="160" 
              stroke="${i === this.activeIndex ? 'rgba(0,0,0,0.08)' : 'transparent'}" 
              stroke-width="1" stroke-dasharray="4,4" class="guide-line" data-index="${i}"/>`
          ).join('')}
          
          <!-- Area fill -->
          <path d="${areaD}" fill="url(#chartAreaGrad)" class="chart-area"/>
          
          <!-- Main line -->
          <path d="${pathD}" fill="none" stroke="#8c735d" stroke-width="2.5" 
            stroke-linecap="round" stroke-linejoin="round" class="chart-line" filter="url(#chartGlow)"/>
          
          <!-- Data points -->
          ${points.map((p, i) => `
            <circle cx="${p.x}" cy="${p.y}" r="${i === this.activeIndex ? 5 : 3}" 
              fill="${i === this.activeIndex ? '#1a1a1a' : '#8c735d'}" 
              stroke="${i === this.activeIndex ? '#fff' : 'transparent'}" 
              stroke-width="${i === this.activeIndex ? 3 : 0}"
              class="chart-point ${i === this.activeIndex ? 'chart-point--active' : ''}" 
              data-index="${i}" style="cursor: pointer;"/>
          `).join('')}
          
          <!-- Active point glow -->
          ${activePoint ? `
            <circle cx="${activePoint.x}" cy="${activePoint.y}" r="12" 
              fill="rgba(140,115,93,0.15)" class="chart-point-glow"/>
          ` : ''}
        </svg>
        
        <div class="chart-tooltip chart-tooltip--visible chart-tooltip--animated" 
          style="left: ${activePoint.x / 4}%; top: ${activePoint.y / 180 * 100 - 45}%;">
          <div class="chart-tooltip__label">${activePoint.label}</div>
          <div class="chart-tooltip__value">${activePoint.amount}</div>
        </div>
      `;
      
      this.attachEvents(points);
    }
  
    attachEvents(points) {
      const svgPoints = this.container.querySelectorAll('.chart-point');
      svgPoints.forEach((point, i) => {
        point.addEventListener('mouseenter', () => this.setActivePoint(i));
        point.addEventListener('click', () => this.setActivePoint(i));
      });
    }
  
    setActivePoint(index) {
      if (index === this.activeIndex) return;
      this.activeIndex = index;
      this.render();
      this.updateXAxis();
    }
  
    updateXAxis() {
      const labels = document.querySelectorAll('.statistics-section__x-label');
      labels.forEach((label, i) => {
        label.classList.toggle('statistics-section__x-label--active', i === this.activeIndex);
      });
    }
  
    animate() {
      const line = this.container.querySelector('.chart-line');
      if (line) {
        const length = line.getTotalLength();
        line.style.strokeDasharray = length;
        line.style.strokeDashoffset = length;
        line.style.animation = 'drawLine 2s cubic-bezier(0.25, 0.1, 0.25, 1) 0.5s forwards';
      }
    }
  }
  
  // Initialize chart on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    const chartContainer = document.getElementById('spendingChart');
    if (chartContainer) {
      window.spendingChart = new SpendingChart('spendingChart');
    }
  });