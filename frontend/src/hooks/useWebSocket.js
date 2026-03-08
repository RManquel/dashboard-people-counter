import { useState, useEffect, useRef, useCallback } from 'react'

const WS_URL = import.meta.env.VITE_WS_URL || `ws://${window.location.host}/ws`
const RECONNECT_DELAY = 3000

export function useWebSocket(onMessage) {
    const [connected, setConnected] = useState(false)
    const wsRef = useRef(null)
    const timerRef = useRef(null)
    const mountedRef = useRef(true)

    const connect = useCallback(() => {
        if (!mountedRef.current) return

        try {
            const ws = new WebSocket(WS_URL)
            wsRef.current = ws

            ws.onopen = () => {
                if (!mountedRef.current) return
                setConnected(true)
                clearTimeout(timerRef.current)
            }

            ws.onmessage = (event) => {
                if (!mountedRef.current) return
                try {
                    const msg = JSON.parse(event.data)
                    onMessage(msg)
                } catch (e) {
                    console.warn('WS parse error:', e)
                }
            }

            ws.onclose = () => {
                if (!mountedRef.current) return
                setConnected(false)
                timerRef.current = setTimeout(connect, RECONNECT_DELAY)
            }

            ws.onerror = () => {
                ws.close()
            }
        } catch (e) {
            console.error('WS connect error:', e)
            timerRef.current = setTimeout(connect, RECONNECT_DELAY)
        }
    }, [onMessage])

    useEffect(() => {
        mountedRef.current = true
        connect()
        return () => {
            mountedRef.current = false
            clearTimeout(timerRef.current)
            wsRef.current?.close()
        }
    }, [connect])

    return { connected }
}
