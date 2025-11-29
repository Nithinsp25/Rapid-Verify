/**
 * RapidVerify - Main Application JavaScript
 * Mumbai Hacks '25 Edition
 */

// ==========================================================================
// Global State & Configuration
// ==========================================================================

const API_BASE_URL = '/api';

const state = {
    isLoading: false,
    currentPlatformFilter: 'all',
    trendingClaims: [],
    statistics: {}
};

// ==========================================================================
// Utility Functions
// ==========================================================================

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

/**
 * Animate counter from 0 to target value
 */
function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function for smooth animation
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(easeOutQuart * target);
        
        element.textContent = formatNumber(current);
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = formatNumber(target);
        }
    }
    
    requestAnimationFrame(update);
}

/**
 * Create particle elements for background
 */
function createParticles() {
    const container = document.getElementById('particles');
    if (!container) return;
    
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.left = `${Math.random() * 100}%`;
        particle.style.animationDelay = `${Math.random() * 20}s`;
        particle.style.animationDuration = `${15 + Math.random() * 15}s`;
        particle.style.opacity = Math.random() * 0.3 + 0.1;
        container.appendChild(particle);
    }
}

/**
 * Get platform icon class
 */
function getPlatformIcon(platform) {
    const icons = {
        twitter: 'fab fa-twitter',
        whatsapp: 'fab fa-whatsapp',
        telegram: 'fab fa-telegram',
        facebook: 'fab fa-facebook',
        instagram: 'fab fa-instagram',
        web: 'fas fa-globe'
    };
    return icons[platform] || 'fas fa-globe';
}

/**
 * Get status color class
 */
function getStatusClass(status) {
    switch (status) {
        case 'debunked': return 'debunked';
        case 'verified': return 'verified';
        case 'investigating': return 'investigating';
        default: return 'investigating';
    }
}

/**
 * Get risk level class
 */
function getRiskClass(level) {
    switch (level) {
        case 'critical': return 'critical';
        case 'high': return 'high';
        case 'medium': return 'medium';
        case 'low': return 'low';
        default: return 'medium';
    }
}

// ==========================================================================
// Animation on Scroll
// ==========================================================================

function initScrollAnimations() {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.animate-on-scroll').forEach(el => {
        observer.observe(el);
    });
}

// ==========================================================================
// Navigation
// ==========================================================================

function initNavigation() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.querySelector('.nav-links');
    
    if (mobileMenuBtn && navLinks) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });
    }
    
    // Close mobile menu on link click
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            navLinks?.classList.remove('active');
            mobileMenuBtn?.classList.remove('active');
        });
    });
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    window.addEventListener('scroll', debounce(() => {
        if (window.scrollY > 50) {
            navbar?.classList.add('scrolled');
        } else {
            navbar?.classList.remove('scrolled');
        }
    }, 10));
}

// ==========================================================================
// Counter Animation
// ==========================================================================

function initCounters() {
    const counters = document.querySelectorAll('.counter');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.dataset.target);
                animateCounter(entry.target, target);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => observer.observe(counter));
}

// ==========================================================================
// Verification Functionality
// ==========================================================================

async function verifyClaim(claimText, source = 'User Submission') {
    try {
        const response = await fetch(`${API_BASE_URL}/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                claim: claimText,
                source: source
            })
        });
        
        if (!response.ok) {
            throw new Error('Verification failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Verification error:', error);
        throw error;
    }
}

function renderVerificationResult(result) {
    const score = result.verification_score || 0;
    const scoreClass = score < 0.4 ? 'low' : score < 0.7 ? 'medium' : 'high';
    const status = result.status || 'investigating';
    const statusText = status === 'debunked' ? 'Likely Fake' : status === 'verified' ? 'Likely Authentic' : 'Under Investigation';
    
    return `
        <div class="verification-display">
            <div class="result-header">
                <div class="result-status">
                    <div class="status-icon ${status}">
                        <i class="fas ${status === 'verified' ? 'fa-check-circle' : status === 'debunked' ? 'fa-times-circle' : 'fa-question-circle'}"></i>
                    </div>
                    <div class="status-text">
                        <h4>${statusText}</h4>
                        <span>${result.category || 'Analysis Complete'}</span>
                    </div>
                </div>
                <div class="score-display">
                    <span class="score-value ${scoreClass}">${Math.round(score * 100)}%</span>
                    <span class="score-label">Authenticity Score</span>
                </div>
            </div>
            
            <div class="result-details">
                ${Object.entries(result.detailed_scores || {}).map(([key, value]) => `
                    <div class="detail-row">
                        <span class="detail-label">${key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                        <span class="detail-value">${Math.round((value.score || value) * 100)}%</span>
                    </div>
                `).join('')}
            </div>
            
            ${result.report ? `
                <div class="result-report">
                    <p>${result.report}</p>
                </div>
            ` : ''}
            
            ${result.blockchain_hash ? `
                <div class="blockchain-info glass-card-mini" style="margin-top: var(--space-md);">
                    <p style="font-size: 0.8rem; color: var(--text-muted);">
                        <i class="fas fa-link" style="color: var(--primary); margin-right: 8px;"></i>
                        Blockchain Hash: <code style="color: var(--primary);">${result.blockchain_hash}</code>
                    </p>
                </div>
            ` : ''}
        </div>
    `;
}

function initVerification() {
    const verifyBtn = document.getElementById('verifyBtn');
    const claimInput = document.getElementById('claimInput');
    const resultSection = document.getElementById('resultSection');
    
    if (!verifyBtn || !claimInput) return;
    
    verifyBtn.addEventListener('click', async () => {
        const claimText = claimInput.value.trim();
        
        if (!claimText) {
            alert('Please enter a claim to verify');
            return;
        }
        
        // Show loading state
        verifyBtn.classList.add('loading');
        verifyBtn.disabled = true;
        
        try {
            const result = await verifyClaim(claimText);
            
            if (resultSection) {
                resultSection.innerHTML = renderVerificationResult(result);
            }
        } catch (error) {
            if (resultSection) {
                resultSection.innerHTML = `
                    <div class="result-placeholder" style="color: var(--danger);">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Verification failed. Please try again.</p>
                    </div>
                `;
            }
        } finally {
            verifyBtn.classList.remove('loading');
            verifyBtn.disabled = false;
        }
    });
    
    // Clear button functionality
    const clearBtn = document.getElementById('clearBtn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            claimInput.value = '';
            if (resultSection) {
                resultSection.innerHTML = `
                    <div class="result-placeholder">
                        <i class="fas fa-search"></i>
                        <p>Enter a claim above to see verification results</p>
                    </div>
                `;
            }
        });
    }
}

// ==========================================================================
// Dashboard Functionality
// ==========================================================================

async function fetchTrendingClaims(platform = 'all') {
    try {
        const response = await fetch(`${API_BASE_URL}/trending?platform=${platform}`);
        if (!response.ok) throw new Error('Failed to fetch trending claims');
        const data = await response.json();
        return data.claims || [];
    } catch (error) {
        console.error('Error fetching trending claims:', error);
        return [];
    }
}

async function fetchStatistics() {
    try {
        const response = await fetch(`${API_BASE_URL}/statistics`);
        if (!response.ok) throw new Error('Failed to fetch statistics');
        const data = await response.json();
        return data.statistics || {};
    } catch (error) {
        console.error('Error fetching statistics:', error);
        return {};
    }
}

function renderClaimItem(claim) {
    return `
        <div class="claim-item ${claim.risk_level}" data-id="${claim.id}">
            <div class="claim-item-header">
                <div class="claim-platform ${claim.platform}">
                    <i class="${getPlatformIcon(claim.platform)}"></i>
                    <span>${claim.source}</span>
                </div>
                <span class="claim-urgency ${claim.risk_level}">
                    ${claim.urgency}% Urgency
                </span>
            </div>
            <div class="claim-item-content">
                <p>${claim.claim}</p>
            </div>
            <div class="claim-item-footer">
                <span class="claim-status ${claim.status}">
                    <i class="fas ${claim.status === 'verified' ? 'fa-check-circle' : claim.status === 'debunked' ? 'fa-times-circle' : 'fa-clock'}"></i>
                    ${claim.status.charAt(0).toUpperCase() + claim.status.slice(1)}
                    (${Math.round(claim.verification_score * 100)}%)
                </span>
                <span class="claim-time">${claim.timestamp}</span>
            </div>
        </div>
    `;
}

function initDashboard() {
    const claimsList = document.getElementById('claimsList');
    const filterTabs = document.querySelectorAll('.filter-tab');
    
    if (!claimsList) return;
    
    // Load initial data
    loadDashboardData();
    
    // Filter tabs functionality
    filterTabs.forEach(tab => {
        tab.addEventListener('click', async () => {
            filterTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const platform = tab.dataset.platform;
            state.currentPlatformFilter = platform;
            
            claimsList.innerHTML = '<div class="loading-spinner">Loading...</div>';
            const claims = await fetchTrendingClaims(platform);
            renderClaims(claims);
        });
    });
    
    // Auto-refresh every 30 seconds
    setInterval(loadDashboardData, 30000);
}

async function loadDashboardData() {
    const claimsList = document.getElementById('claimsList');
    
    // Fetch claims and statistics in parallel
    const [claims, stats] = await Promise.all([
        fetchTrendingClaims(state.currentPlatformFilter),
        fetchStatistics()
    ]);
    
    state.trendingClaims = claims;
    state.statistics = stats;
    
    // Update statistics
    updateStatistics(stats);
    
    // Render claims
    if (claimsList) {
        renderClaims(claims);
    }
}

function updateStatistics(stats) {
    const statElements = {
        'claims-verified': stats.claims_verified,
        'fake-detected': stats.fake_detected,
        'alerts-sent': stats.alerts_sent,
        'accuracy-rate': stats.accuracy_rate
    };
    
    Object.entries(statElements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element && value !== undefined) {
            element.textContent = formatNumber(value);
        }
    });
}

function renderClaims(claims) {
    const claimsList = document.getElementById('claimsList');
    if (!claimsList) return;
    
    if (claims.length === 0) {
        claimsList.innerHTML = `
            <div class="no-claims">
                <i class="fas fa-inbox"></i>
                <p>No claims found for this filter</p>
            </div>
        `;
        return;
    }
    
    claimsList.innerHTML = claims.map(renderClaimItem).join('');
    
    // Add click handlers for claim items
    claimsList.querySelectorAll('.claim-item').forEach(item => {
        item.addEventListener('click', () => {
            const claimId = item.dataset.id;
            showClaimDetails(claimId);
        });
    });
}

function showClaimDetails(claimId) {
    const claim = state.trendingClaims.find(c => c.id.toString() === claimId);
    if (!claim) return;
    
    // For now, just redirect to verify page with the claim
    window.location.href = `/verify?claim=${encodeURIComponent(claim.claim)}`;
}

// ==========================================================================
// Verify Page
// ==========================================================================

function initVerifyPage() {
    const claimInput = document.getElementById('claimInputFull');
    const sourceSelect = document.getElementById('sourceSelect');
    const verifyBtn = document.getElementById('verifyBtnFull');
    const clearBtn = document.getElementById('clearBtnFull');
    const resultContainer = document.getElementById('resultContainer');
    
    if (!verifyBtn) return;
    
    // Check for URL parameters (claim from dashboard)
    const urlParams = new URLSearchParams(window.location.search);
    const claimParam = urlParams.get('claim');
    if (claimParam && claimInput) {
        claimInput.value = claimParam;
    }
    
    verifyBtn.addEventListener('click', async () => {
        const claimText = claimInput?.value.trim();
        const source = sourceSelect?.value || 'User Submission';
        
        if (!claimText) {
            alert('Please enter a claim to verify');
            return;
        }
        
        // Show loading state
        verifyBtn.classList.add('loading');
        verifyBtn.disabled = true;
        
        try {
            const result = await verifyClaim(claimText, source);
            
            if (resultContainer) {
                resultContainer.classList.remove('hidden');
                resultContainer.innerHTML = renderVerificationResult(result);
            }
        } catch (error) {
            if (resultContainer) {
                resultContainer.classList.remove('hidden');
                resultContainer.innerHTML = `
                    <div class="result-placeholder" style="color: var(--danger);">
                        <i class="fas fa-exclamation-triangle"></i>
                        <p>Verification failed. Please try again.</p>
                    </div>
                `;
            }
        } finally {
            verifyBtn.classList.remove('loading');
            verifyBtn.disabled = false;
        }
    });
    
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (claimInput) claimInput.value = '';
            if (resultContainer) {
                resultContainer.classList.add('hidden');
                resultContainer.innerHTML = '';
            }
        });
    }
}

// ==========================================================================
// Alert Subscription
// ==========================================================================

async function subscribeToAlerts(channel, contact, topics) {
    try {
        const response = await fetch(`${API_BASE_URL}/alerts/subscribe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ channel, contact, topics })
        });
        
        if (!response.ok) throw new Error('Subscription failed');
        return await response.json();
    } catch (error) {
        console.error('Subscription error:', error);
        throw error;
    }
}

// ==========================================================================
// Smooth Scroll
// ==========================================================================

function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ==========================================================================
// Typing Effect
// ==========================================================================

function typeWriter(element, text, speed = 50) {
    let i = 0;
    element.textContent = '';
    
    function type() {
        if (i < text.length) {
            element.textContent += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

// ==========================================================================
// Initialize Everything
// ==========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Common initializations
    createParticles();
    initNavigation();
    initScrollAnimations();
    initSmoothScroll();
    
    // Page-specific initializations
    const body = document.body;
    
    if (body.classList.contains('landing-page')) {
        initCounters();
        initVerification();
    }
    
    if (body.classList.contains('dashboard-page')) {
        initDashboard();
    }
    
    if (body.classList.contains('verify-page')) {
        initVerifyPage();
    }
    
    console.log('🛡️ RapidVerify initialized - Fighting misinformation with AI!');
});

// Export functions for global access
window.RapidVerify = {
    verifyClaim,
    subscribeToAlerts,
    fetchTrendingClaims,
    fetchStatistics
};

