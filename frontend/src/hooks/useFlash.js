import { useEffect, useRef, useState } from 'react'

export function useFlash(value) {
    const [flashing, setFlashing] = useState(false)
    const prevRef = useRef(value)

    useEffect(() => {
        if (prevRef.current !== value) {
            prevRef.current = value
            setFlashing(true)
            const t = setTimeout(() => setFlashing(false), 600)
            return () => clearTimeout(t)
        }
    }, [value])

    return flashing
}
