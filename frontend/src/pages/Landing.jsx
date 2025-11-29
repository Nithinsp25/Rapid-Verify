import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

export default function Landing() {
  const [stats, setStats] = useState({ claims: 0, accuracy: 0, alerts: 0 })

  useEffect(() => {
    // Animate counters
    const targets = { claims: 12847, accuracy: 97, alerts: 8926 }
    const duration = 2000
    const start = Date.now()
    
    const animate = () => {
      const elapsed = Date.now() - start
      const progress = Math.min(elapsed / duration, 1)
      
      setStats({
        claims: Math.floor(targets.claims * progress),
        accuracy: Math.floor(targets.accuracy * progress),
        alerts: Math.floor(targets.alerts * progress),
      })
      
      if (progress < 1) requestAnimationFrame(animate)
    }
    
    animate()
  }, [])

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge glass-badge animate-slide-up">
            <span className="badge-dot"></span>
            <span>Mumbai Hacks '25 Project</span>
          </div>
          
          <h1 className="hero-title animate-slide-up delay-1">
            Stop <span className="gradient-text">Misinformation</span><br />
            Before It <span className="text-glow">Goes Viral</span>
          </h1>
          
          <p className="hero-subtitle animate-slide-up delay-2">
            AI-Powered Real-Time Verification Platform that protects communities 
            during emergencies, festivals, and public health crises.
          </p>
          
          <div className="hero-cta animate-slide-up delay-3">
            <Link to="/verify" className="neo-btn-primary">
              <i className="fas fa-search"></i>
              Verify Now
            </Link>
            <Link to="/dashboard" className="glass-btn">
              <i className="fas fa-chart-line"></i>
              Live Dashboard
            </Link>
          </div>
          
          <div className="hero-stats animate-slide-up delay-4">
            <div className="stat-item glass-card-mini">
              <span className="stat-number">{stats.claims.toLocaleString()}</span>
              <span className="stat-label">Claims Verified</span>
            </div>
            <div className="stat-item glass-card-mini">
              <span className="stat-number">{stats.accuracy}%</span>
              <span className="stat-label">Accuracy</span>
            </div>
            <div className="stat-item glass-card-mini">
              <span className="stat-number">{stats.alerts.toLocaleString()}</span>
              <span className="stat-label">Alerts Sent</span>
            </div>
          </div>
        </div>
        
        <div className="hero-visual animate-float">
          <div className="visual-card glass-panel-heavy">
            <div className="scan-animation">
              <div className="scan-line"></div>
              <div className="claim-preview">
                <div className="claim-header">
                  <span className="platform-badge telegram"><i className="fab fa-telegram"></i></span>
                  <span className="claim-source">Viral Forward</span>
                </div>
                <p className="claim-text">"Breaking: Free COVID vaccines cause magnetic effects..."</p>
                <div className="verification-result">
                  <span className="result-badge debunked">
                    <i className="fas fa-times-circle"></i> DEBUNKED
                  </span>
                  <div className="confidence-bar">
                    <div className="confidence-fill" style={{ width: '12%' }}></div>
                  </div>
                  <span className="confidence-score">12% Authentic</span>
                </div>
              </div>
            </div>
            <div className="visual-glow"></div>
          </div>
        </div>
      </section>

      {/* Trust Banner */}
      <section className="trust-banner">
        <div className="container">
          <p className="trust-label">Cross-verified with trusted sources</p>
          <div className="trust-logos">
            <div className="trust-logo glass-card-mini"><i className="fas fa-newspaper"></i> Reuters</div>
            <div className="trust-logo glass-card-mini"><i className="fas fa-landmark"></i> PIB India</div>
            <div className="trust-logo glass-card-mini"><i className="fas fa-heartbeat"></i> WHO</div>
            <div className="trust-logo glass-card-mini"><i className="fas fa-globe"></i> AFP</div>
            <div className="trust-logo glass-card-mini"><i className="fas fa-check-double"></i> FactCheck</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="container">
          <div className="section-header">
            <span className="section-badge glass-badge">
              <i className="fas fa-bolt"></i> Key Features
            </span>
            <h2 className="section-title">Powered by <span className="gradient-text">Agentic AI</span></h2>
            <p className="section-subtitle">Multi-agent system working 24/7 to protect you from misinformation</p>
          </div>
          
          <div className="features-grid">
            {features.map((feature, i) => (
              <div key={i} className={`feature-card neo-card animate-slide-up delay-${i + 1}`}>
                <div className="feature-icon-wrap">
                  <div className="feature-icon neo-icon">
                    <i className={feature.icon}></i>
                  </div>
                  <div className={`icon-glow ${feature.glow}`}></div>
                </div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-desc">{feature.desc}</p>
                {feature.extra}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works" id="how-it-works">
        <div className="container">
          <div className="section-header">
            <span className="section-badge glass-badge">
              <i className="fas fa-cog"></i> Process
            </span>
            <h2 className="section-title">How <span className="gradient-text">RapidVerify</span> Works</h2>
            <p className="section-subtitle">From viral claim to verified fact in seconds</p>
          </div>

          <div className="process-timeline">
            <div className="timeline-line"></div>
            
            {steps.map((step, i) => (
              <div key={i} className={`process-step animate-slide-up delay-${i + 1}`}>
                <div className="step-number glass-panel">0{i + 1}</div>
                <div className="step-content neo-card">
                  <div className="step-icon"><i className={step.icon}></i></div>
                  <h4>{step.title}</h4>
                  <p>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Platforms Section */}
      <section className="platforms-section" id="platforms">
        <div className="container">
          <div className="section-header">
            <span className="section-badge glass-badge">
              <i className="fas fa-globe"></i> Coverage
            </span>
            <h2 className="section-title">Platforms We <span className="gradient-text">Monitor</span></h2>
            <p className="section-subtitle">Comprehensive coverage across all major social platforms</p>
          </div>

          <div className="platforms-grid">
            {platforms.map((platform, i) => (
              <div key={i} className={`platform-card glass-panel animate-slide-up delay-${i + 1}`}>
                <div className={`platform-logo ${platform.class}`}>
                  <i className={platform.icon}></i>
                </div>
                <h4>{platform.name}</h4>
                <p className="platform-stats">{platform.claims} claims today</p>
                <span className="status-badge active">Active</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-card glass-panel-heavy">
            <div className="cta-content">
              <h2>Fight Misinformation <span className="gradient-text">Together</span></h2>
              <p>Join thousands of users protecting their communities from fake news and harmful rumors.</p>
              <div className="cta-buttons">
                <Link to="/verify" className="neo-btn-primary">
                  <i className="fas fa-rocket"></i> Get Started Free
                </Link>
                <a href="https://github.com" className="glass-btn" target="_blank" rel="noopener noreferrer">
                  <i className="fab fa-github"></i> View on GitHub
                </a>
              </div>
            </div>
            <div className="cta-visual">
              <div className="floating-icons">
                <i className="fas fa-shield-alt icon-1"></i>
                <i className="fas fa-check-circle icon-2"></i>
                <i className="fas fa-bell icon-3"></i>
                <i className="fas fa-robot icon-4"></i>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="logo">
                <div className="logo-icon">
                  <i className="fas fa-shield-halved"></i>
                </div>
                <span className="logo-text">Rapid<span className="accent">Verify</span></span>
              </div>
              <p>Fighting misinformation with AI-powered verification.</p>
            </div>
            <div className="footer-links">
              <div className="footer-col">
                <h5>Product</h5>
                <Link to="/dashboard">Dashboard</Link>
                <Link to="/verify">Verify</Link>
                <a href="#features">Features</a>
              </div>
              <div className="footer-col">
                <h5>Resources</h5>
                <a href="#">API Docs</a>
                <a href="#">GitHub</a>
                <a href="#">Blog</a>
              </div>
              <div className="footer-col">
                <h5>Connect</h5>
                <a href="#"><i className="fab fa-twitter"></i> Twitter</a>
                <a href="#"><i className="fab fa-discord"></i> Discord</a>
                <a href="#"><i className="fab fa-linkedin"></i> LinkedIn</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 RapidVerify. Built for Mumbai Hacks '25 with ❤️</p>
            <div className="footer-badges">
              <span className="badge">🏆 Hackathon Project</span>
              <span className="badge">🤖 Powered by AI</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

// Data
const features = [
  {
    icon: 'fas fa-radar',
    title: 'Continuous Social Scanning',
    desc: '24/7 monitoring of Twitter/X, Telegram, Facebook and news sites for viral claims and emerging misinformation.',
    glow: 'cyan',
    extra: (
      <div className="feature-platforms">
        <span className="platform-icon"><i className="fab fa-twitter"></i></span>
        <span className="platform-icon"><i className="fab fa-telegram"></i></span>
        <span className="platform-icon"><i className="fab fa-facebook"></i></span>
      </div>
    )
  },
  {
    icon: 'fas fa-brain',
    title: 'AI Claim Extraction',
    desc: 'Advanced NLP powered by Gemini AI extracts, clusters, and ranks claims by urgency and potential danger level.',
    glow: 'purple',
    extra: (
      <div className="feature-tech" style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        <span className="tech-badge">NLP</span>
        <span className="tech-badge">Gemini Pro</span>
        <span className="tech-badge">LangChain</span>
      </div>
    )
  },
  {
    icon: 'fas fa-check-double',
    title: 'Trusted Verification',
    desc: 'Cross-reference with government databases, health APIs, and verified news sources for instant fact-checking.',
    glow: 'green',
    extra: (
      <div className="verification-steps" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
        <span style={{ padding: '0.25rem 0.5rem', background: 'rgba(107, 203, 119, 0.1)', borderRadius: '4px', color: 'var(--success)' }}>Extract</span>
        <i className="fas fa-arrow-right" style={{ fontSize: '0.7rem' }}></i>
        <span style={{ padding: '0.25rem 0.5rem', background: 'rgba(107, 203, 119, 0.1)', borderRadius: '4px', color: 'var(--success)' }}>Search</span>
        <i className="fas fa-arrow-right" style={{ fontSize: '0.7rem' }}></i>
        <span style={{ padding: '0.25rem 0.5rem', background: 'rgba(107, 203, 119, 0.1)', borderRadius: '4px', color: 'var(--success)' }}>Verify</span>
      </div>
    )
  },
  {
    icon: 'fas fa-bell',
    title: 'Instant Notifications',
    desc: 'Push verified updates via dashboards, mobile apps, Telegram bot, and SMS alerts.',
    glow: 'orange',
    extra: (
      <div style={{ display: 'flex', gap: '1rem' }}>
        {[{ icon: 'fas fa-mobile-alt', label: 'App Push' }, { icon: 'fab fa-telegram', label: 'Telegram' }, { icon: 'fas fa-sms', label: 'SMS' }].map((n, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            <i className={n.icon} style={{ fontSize: '1.2rem', color: 'var(--primary)' }}></i>
            <span>{n.label}</span>
          </div>
        ))}
      </div>
    )
  },
  {
    icon: 'fas fa-link',
    title: 'Blockchain Anchoring',
    desc: 'High-impact advisories are timestamped on blockchain for tamper-proof authenticity and public traceability.',
    glow: 'yellow',
    extra: (
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
        <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: 'var(--text-muted)' }}><i className="fas fa-cube"></i></div>
        <div style={{ width: '20px', height: '2px', background: 'linear-gradient(90deg, var(--glass-border), var(--primary))' }}></div>
        <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: 'var(--text-muted)' }}><i className="fas fa-cube"></i></div>
        <div style={{ width: '20px', height: '2px', background: 'linear-gradient(90deg, var(--glass-border), var(--primary))' }}></div>
        <div style={{ width: '40px', height: '40px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--primary)', borderRadius: '8px', color: 'var(--bg-primary)' }} className="pulse-glow"><i className="fas fa-cube"></i></div>
      </div>
    )
  },
  {
    icon: 'fas fa-robot',
    title: 'Multi-Agent Architecture',
    desc: 'Orchestrator, Search, and Scorer agents work in harmony for comprehensive analysis and accurate scoring.',
    glow: 'red',
    extra: (
      <div style={{ display: 'flex', gap: '1rem' }}>
        {[{ icon: 'fas fa-sitemap', label: 'Orchestrator' }, { icon: 'fas fa-search', label: 'Search' }, { icon: 'fas fa-star-half-alt', label: 'Scorer' }].map((a, i) => (
          <div key={i} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.25rem', padding: '0.5rem', background: 'rgba(255,255,255,0.03)', borderRadius: '8px', fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            <i className={a.icon} style={{ fontSize: '1rem', color: 'var(--accent)' }}></i>
            <span>{a.label}</span>
          </div>
        ))}
      </div>
    )
  }
]

const steps = [
  { icon: 'fas fa-satellite-dish', title: 'Detect & Capture', desc: 'AI monitors social platforms 24/7, detecting viral claims and potential misinformation in real-time.' },
  { icon: 'fas fa-microscope', title: 'Extract & Analyze', desc: 'NLP extracts factual claims, identifies key entities, and assesses risk level and urgency.' },
  { icon: 'fas fa-balance-scale', title: 'Cross-Verify', desc: 'Claims are checked against government sources, verified news APIs, and historical fact-checks.' },
  { icon: 'fas fa-broadcast-tower', title: 'Alert & Inform', desc: 'Verified results pushed instantly via multiple channels to maximize reach and impact.' },
]

const platforms = [
  { name: 'Twitter / X', icon: 'fab fa-twitter', class: 'twitter', claims: '1,234' },
  { name: 'Telegram', icon: 'fab fa-telegram', class: 'telegram', claims: '567' },
  { name: 'Facebook', icon: 'fab fa-facebook', class: 'facebook', claims: '923' },
  { name: 'Instagram', icon: 'fab fa-instagram', class: 'instagram', claims: '445' },
  { name: 'News Sites', icon: 'fas fa-newspaper', class: 'news', claims: '678' },
]
