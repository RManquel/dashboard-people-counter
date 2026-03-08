import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Legend,
} from 'recharts'

const PRIMARY = '#024ddf'
const GREEN = '#10b981'

function CustomTooltip({ active, payload, label }) {
    if (!active || !payload?.length) return null
    return (
        <div className="custom-tooltip">
            <p className="tt-label">{label}</p>
            {payload.map((entry) => (
                <p key={entry.dataKey} style={{ color: entry.color }}>
                    {entry.name}: <strong>{entry.value}</strong>
                </p>
            ))}
        </div>
    )
}

export default function OccupancyChart({ data }) {
    const formatted = data.map((d) => ({
        ...d,
        time: d.minute ? d.minute.slice(11, 16) : '', // HH:MM
    }))

    return (
        <ResponsiveContainer width="100%" height={280}>
            <LineChart
                data={formatted}
                margin={{ top: 4, right: 16, left: -8, bottom: 0 }}
            >
                <defs>
                    <linearGradient id="colorEntries" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={PRIMARY} stopOpacity={0.2} />
                        <stop offset="95%" stopColor={PRIMARY} stopOpacity={0} />
                    </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f5" vertical={false} />

                <XAxis
                    dataKey="time"
                    tick={{ fontSize: 11, fill: '#8a97b8', fontFamily: 'Inter' }}
                    tickLine={false}
                    axisLine={false}
                    interval="preserveStartEnd"
                />

                <YAxis
                    tick={{ fontSize: 11, fill: '#8a97b8', fontFamily: 'Inter' }}
                    tickLine={false}
                    axisLine={false}
                    allowDecimals={false}
                />

                <Tooltip content={<CustomTooltip />} />

                <Line
                    type="monotone"
                    dataKey="entries"
                    name="Entries"
                    stroke={PRIMARY}
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, fill: PRIMARY }}
                    isAnimationActive={false}
                />

                <Line
                    type="monotone"
                    dataKey="exits"
                    name="Exits"
                    stroke={GREEN}
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5, fill: GREEN }}
                    isAnimationActive={false}
                />
            </LineChart>
        </ResponsiveContainer>
    )
}
