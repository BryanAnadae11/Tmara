/* ============================================
   BCA FINTECH DASHBOARD - NAVIGATION
   Sidebar, mobile menu, and routing
   ============================================ */

   class Navigation {
    constructor() {
      this.sidebar = document.querySelector('.sidebar');
      this.mobileNav = document.querySelector('.mobile-nav');
      this.mobileOverlay = document.querySelector('.mobile-nav-overlay');
      this.hamburger = document.querySelector('.hamburger');
      this.closeBtn = document.querySelector('.mobile-nav__close');
      this.navItems = document.querySelectorAll('.nav-item');
      
      this.init();
    }
  
    init() {
      this.hamburger?.addEventListener('click', () => this.openMobileNav());
      this.closeBtn?.addEventListener('click', () => this.closeMobileNav());
      this.mobileOverlay?.addEventListener('click', () => this.closeMobileNav());
      
      this.navItems.forEach(item => {
        item.addEventListener('click', (e) => this.handleNavClick(e, item));
      });
  
      // Close on escape
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') this.closeMobileNav();
      });
  
      // Handle resize
      let resizeTimer;
      window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
          if (window.innerWidth > 767) {
            this.closeMobileNav();
          }
        }, 150);
      });
    }
  
    openMobileNav() {
      this.mobileNav?.classList.add('mobile-nav--open');
      this.mobileOverlay?.classList.add('mobile-nav-overlay--open');
      this.hamburger?.classList.add('hamburger--active');
      document.body.style.overflow = 'hidden';
    }
  
    closeMobileNav() {
      this.mobileNav?.classList.remove('mobile-nav--open');
      this.mobileOverlay?.classList.remove('mobile-nav-overlay--open');
      this.hamburger?.classList.remove('hamburger--active');
      document.body.style.overflow = '';
    }
  
    handleNavClick(e, item) {
      // Remove active from all
      this.navItems.forEach(n => n.classList.remove('nav-item--active'));
    
      // Add active to clicked
      item.classList.add('nav-item--active');
    
      // Close mobile nav if open (only matters on mobile)
      this.closeMobileNav();
    
      // no e.preventDefault(), no fade animation — let the <a> navigate normally
    }
  }
  
  // Initialize
  document.addEventListener('DOMContentLoaded', () => {
    window.navigation = new Navigation();
  });