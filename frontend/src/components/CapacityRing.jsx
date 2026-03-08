const STADIUM_CAPACITY = parseInt(import.meta.env.VITE_STADIUM_CAPACITY || '50000')
const STROKE = 10
const RADIUS = 56
const CIRCUMFERENCE = 2 * Math.PI * RADIUS

export default function CapacityRing({ peopleInside }) {
    const pct = Math.min(peopleInside / STADIUM_CAPACITY, 1)
    const offset = CIRCUMFERENCE * (1 - pct)

    // Color gradient based on fill level
    const color =
        pct < 0.7 ? '#024ddf'
            : pct < 0.9 ? '#f59e0b'
                : '#ef4444'

    return (
        <div className="capacity-ring-wrap">
            <svg width="140" height="140" viewBox="0 0 140 140">
                {/* Track */}
                <circle
                    cx="70" cy="70" r={RADIUS}
                    fill="none"
                    stroke="#e2e8f5"
                    strokeWidth={STROKE}
                />
                {/* Progress */}
                <circle
                    cx="70" cy="70" r={RADIUS}
                    fill="none"
                    stroke={color}
                    strokeWidth={STROKE}
                    strokeDasharray={CIRCUMFERENCE}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    style={{ transition: 'stroke-dashoffset 0.6s ease, stroke 0.3s ease' }}
                />
            </svg>
            <div className="capacity-pct-label">
                {Math.round(pct * 100)}%
                <span>capacity</span>
            </div>
        </div>
    )
}
