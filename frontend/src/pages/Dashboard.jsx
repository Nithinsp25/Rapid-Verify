import { useState, useEffect } from 'react'

export default function Dashboard() {
  const [stats, setStats] = useState({ claims: 0, false: 0, alerts: 0, accuracy: 0 })
  const [activity, setActivity] = useState([])
  const [alerts, setAlerts] = useState([])

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch Stats
        const statsRes = await fetch('http://localhost:5000/api/dashboard/stats')
        const statsData = await statsRes.json()
        if (statsData.success) {
          setStats(statsData.stats)
        }

        // Fetch Activity
        const recordsRes = await fetch('http://localhost:5000/api/blockchain/records?limit=10')
        const recordsData = await recordsRes.json()
        if (recordsData.success) {
          const newActivity = recordsData.records.map(record => ({
            platform: 'web',
            text: record.claim_snippet || 'Verified content',
            status: record.status,
            time: getRelativeTime(record.timestamp)
          }))
          setActivity(newActivity)

          // Generate alerts from debunked/high-risk records
          const newAlerts = recordsData.records
            .filter(r => r.status === 'debunked' || (r.verification_score || 0) < 0.4)
            .slice(0, 5)
            .map((r, i) => ({
              id: i,
              text: `High Risk: ${r.claim_snippet || 'Suspicious content detected'}`,
              time: getRelativeTime(r.timestamp)
            }))
          setAlerts(newAlerts)
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
      }
    }

    // Initial fetch
    fetchData()

    // Poll every 5 seconds
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  const getRelativeTime = (timestamp) => {
    if (!timestamp) return 'Just now'
    const now = Math.floor(Date.now() / 1000)
    const diff = now - timestamp

    if (diff < 60) return 'Just now'
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    return `${Math.floor(diff / 86400)}d ago`
  }

  const platformIcons = {
    whatsapp: 'fab fa-whatsapp',
    twitter: 'fab fa-twitter',
    telegram: 'fab fa-telegram',
    facebook: 'fab fa-facebook'
  }

  const platformColors = {
    whatsapp: '#25d366',
    twitter: '#1da1f2',
    telegram: '#0088cc',
    facebook: '#1877f2'
  }

  return (
    <div className="dashboard-page" style={{ paddingTop: '100px' }}>
      {/* Header */}
      <div className="dashboard-header" style={{ padding: 'var(--space-xl)', maxWidth: '1400px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
          <h1 style={{ fontSize: '2rem', fontWeight: 700 }}>
            Live <span className="gradient-text">Dashboard</span>
          </h1>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 'var(--space-sm)',
            padding: 'var(--space-sm) var(--space-md)',
            background: 'rgba(107, 203, 119, 0.1)',
            border: '1px solid rgba(107, 203, 119, 0.3)',
            borderRadius: 'var(--radius-full)',
            fontSize: '0.85rem',
            color: 'var(--success)'
          }}>
            <div className="pulse-glow" style={{
              width: '8px',
              height: '8px',
              background: 'var(--success)',
              borderRadius: '50%'
            }}></div>
            <span>Live Monitoring</span>
          </div>
        </div>

        {/* Stats Row */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: 'var(--space-md)'
        }}>
          {[
            { icon: 'fas fa-check-circle', label: 'Claims Verified', value: stats.claims.toLocaleString(), color: 'var(--primary)', bg: 'rgba(0, 245, 212, 0.15)' },
            { icon: 'fas fa-times-circle', label: 'False Claims', value: stats.false.toLocaleString(), color: 'var(--danger)', bg: 'rgba(255, 107, 107, 0.15)' },
            { icon: 'fas fa-bell', label: 'Alerts Sent', value: stats.alerts.toLocaleString(), color: 'var(--warning)', bg: 'rgba(255, 217, 61, 0.15)' },
            { icon: 'fas fa-chart-line', label: 'Accuracy', value: `${stats.accuracy}%`, color: 'var(--success)', bg: 'rgba(107, 203, 119, 0.15)' },
          ].map((stat, i) => (
            <div key={i} className="glass-panel" style={{ padding: 'var(--space-lg)', display: 'flex', alignItems: 'center', gap: 'var(--space-md)' }}>
              <div style={{
                width: '50px',
                height: '50px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: 'var(--radius-md)',
                fontSize: '1.3rem',
                background: stat.bg,
                color: stat.color
              }}>
                <i className={stat.icon}></i>
              </div>
              <div>
                <h3 style={{ fontSize: '1.8rem', fontWeight: 700, fontFamily: 'var(--font-mono)', lineHeight: 1, marginBottom: '4px' }}>
                  {stat.value}
                </h3>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{stat.label}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <div style={{
        padding: '0 var(--space-xl) var(--space-xl)',
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'grid',
        gridTemplateColumns: '2fr 1fr',
        gap: 'var(--space-xl)'
      }}>
        {/* Live Activity */}
        <div className="glass-panel-heavy" style={{ padding: 'var(--space-lg)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600 }}>
              <i className="fas fa-stream" style={{ color: 'var(--primary)', marginRight: 'var(--space-sm)' }}></i>
              Live Verification Feed
            </h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Auto-updating</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)' }}>
            {activity.map((item, i) => (
              <div key={i} style={{
                padding: 'var(--space-md)',
                background: 'rgba(0, 0, 0, 0.2)',
                borderRadius: 'var(--radius-md)',
                borderLeft: `3px solid ${item.status === 'debunked' ? 'var(--danger)' : item.status === 'verified' ? 'var(--success)' : 'var(--warning)'}`,
                animation: i === 0 ? 'slideUp 0.3s ease' : 'none'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-sm)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <i className={platformIcons[item.platform]} style={{ fontSize: '1.2rem', color: platformColors[item.platform] }}></i>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{item.platform}</span>
                  </div>
                  <span style={{
                    padding: 'var(--space-xs) var(--space-sm)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    fontFamily: 'var(--font-mono)',
                    background: item.status === 'debunked' ? 'rgba(255, 107, 107, 0.2)' :
                      item.status === 'verified' ? 'rgba(107, 203, 119, 0.2)' : 'rgba(255, 217, 61, 0.2)',
                    color: item.status === 'debunked' ? 'var(--danger)' :
                      item.status === 'verified' ? 'var(--success)' : 'var(--warning)',
                    textTransform: 'uppercase'
                  }}>{item.status}</span>
                </div>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-primary)', marginBottom: 'var(--space-sm)' }}>
                  "{item.text}"
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sidebar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {/* Recent Alerts */}
          <div className="glass-panel" style={{ padding: 'var(--space-lg)' }}>
            <h4 style={{ fontSize: '1rem', marginBottom: 'var(--space-md)', display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
              <i className="fas fa-exclamation-triangle" style={{ color: 'var(--danger)' }}></i>
              Recent Alerts
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {alerts.map((alert) => (
                <div key={alert.id} style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-sm)',
                  padding: 'var(--space-sm)',
                  background: 'rgba(255, 107, 107, 0.1)',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.85rem'
                }}>
                  <i className="fas fa-bell" style={{ color: 'var(--danger)' }}></i>
                  <div style={{ flex: 1 }}>
                    <p style={{ marginBottom: '2px' }}>{alert.text}</p>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{alert.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Platform Status */}
          <div className="glass-panel" style={{ padding: 'var(--space-lg)' }}>
            <h4 style={{ fontSize: '1rem', marginBottom: 'var(--space-md)', display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
              <i className="fas fa-server" style={{ color: 'var(--primary)' }}></i>
              Platform Status
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
              {[
                { name: 'Twitter/X', claims: '234', icon: 'fab fa-twitter', color: '#1da1f2' },
                { name: 'Telegram', claims: '156', icon: 'fab fa-telegram', color: '#0088cc' },
                { name: 'Facebook', claims: '145', icon: 'fab fa-facebook', color: '#1877f2' },
                { name: 'News Sites', claims: '123', icon: 'fas fa-newspaper', color: 'var(--primary)' },
              ].map((platform, i) => (
                <div key={i} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: 'var(--space-sm)',
                  background: 'rgba(0, 0, 0, 0.2)',
                  borderRadius: 'var(--radius-sm)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', fontSize: '0.9rem' }}>
                    <i className={platform.icon} style={{ color: platform.color }}></i>
                    <span>{platform.name}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                      {platform.claims}
                    </span>
                    <div style={{ width: '8px', height: '8px', background: 'var(--success)', borderRadius: '50%' }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* API Status */}
          <div className="glass-panel" style={{ padding: 'var(--space-lg)' }}>
            <h4 style={{ fontSize: '1rem', marginBottom: 'var(--space-md)', display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
              <i className="fas fa-cogs" style={{ color: 'var(--secondary)' }}></i>
              System Status
            </h4>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-sm)' }}>
              {['API Server', 'AI Verifier', 'Scraper', 'Gemini AI', 'Telegram Bot', 'Blockchain'].map((service, i) => {
                // Get blockchain status from stats
                const isBlockchain = service === 'Blockchain'
                const blockchainStatus = stats?.services?.blockchain || 'demo mode'
                const isActive = isBlockchain
                  ? (blockchainStatus.includes('active') || blockchainStatus.includes('live'))
                  : true
                const isDemo = isBlockchain && blockchainStatus.includes('demo')

                return (
                  <div key={i} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 'var(--space-xs)',
                    padding: 'var(--space-xs) var(--space-sm)',
                    background: 'rgba(0, 0, 0, 0.2)',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.8rem',
                    ...(isBlockchain && isDemo && {
                      background: 'rgba(255, 170, 0, 0.15)',
                      border: '1px solid rgba(255, 170, 0, 0.3)'
                    })
                  }}>
                    <div style={{
                      width: '6px',
                      height: '6px',
                      background: isActive ? (isDemo ? 'var(--warning)' : 'var(--success)') : 'var(--danger)',
                      borderRadius: '50%'
                    }}></div>
                    <span>{service}</span>
                    {isBlockchain && isDemo && (
                      <span style={{
                        fontSize: '0.65rem',
                        color: 'var(--warning)',
                        marginLeft: '4px'
                      }}>(demo)</span>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer" style={{ marginTop: 'var(--space-3xl)' }}>
        <div className="container">
          <div className="footer-bottom" style={{ borderTop: 'none', paddingTop: 0 }}>
            <p>&copy; 2025 RapidVerify. Mumbai Hacks '25</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
