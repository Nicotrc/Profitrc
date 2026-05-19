import { useState, useEffect, useCallback } from 'react'

export function useApi<T>(url: string, autoFetch = true, refreshMs = 0) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetch_ = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(url)
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const json = await res.json()
      setData(json)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [url])

  useEffect(() => {
    if (autoFetch) fetch_()
  }, [fetch_, autoFetch])

  useEffect(() => {
    if (!refreshMs) return
    const id = setInterval(fetch_, refreshMs)
    return () => clearInterval(id)
  }, [fetch_, refreshMs])

  return { data, loading, error, refetch: fetch_ }
}

export async function post<T>(url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    const txt = await res.text()
    throw new Error(`HTTP ${res.status}: ${txt}`)
  }
  return res.json()
}

export async function patch<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return res.json()
}

export async function del(url: string): Promise<void> {
  await fetch(url, { method: 'DELETE' })
}
