import { useFlash } from '../hooks/useFlash'

function formatNumber(n) {
    return n.toLocaleString('en-US')
}

export default function StatCard({ label, value, icon: Icon, iconClass = 'icon-blue', footer, trendValue, trendUp }) {
    const flashing = useFlash(value)

    return (
        <div className="stat-card fade-in-up">
            <div className="stat-card-header">
                <span className="stat-card-label">{label}</span>
                {Icon && (
                    <div className={`stat-card-icon ${iconClass}`}>
                        <Icon size={18} />
                    </div>
                )}
            </div>

            <div className={`stat-card-value${flashing ? ' flash' : ''}`}>
                {formatNumber(value)}
            </div>

            {trendValue != null && (
                <div className={`stat-card-trend ${trendUp ? 'trend-up' : 'trend-down'}`}>
                    {trendUp ? '▲' : '▼'} {formatNumber(Math.abs(trendValue))} from last hour
                </div>
            )}

            {footer && <div className="stat-card-footer">{footer}</div>}
        </div>
    )
}
