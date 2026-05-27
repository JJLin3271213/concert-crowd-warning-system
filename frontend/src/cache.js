const CACHE_PREFIX = 'concert_cache_'
const CACHE_TTL = 30000 // 30秒内存缓存

const memCache = {}

export async function cachedFetch(url, ttl = CACHE_TTL) {
  const key = CACHE_PREFIX + url
  const now = Date.now()

  // 1. 内存缓存
  if (memCache[key] && (now - memCache[key].time < ttl)) {
    return memCache[key].data
  }

  // 2. localStorage 兜底
  try {
    const stored = localStorage.getItem(key)
    if (stored) {
      const parsed = JSON.parse(stored)
      if (now - parsed.time < ttl * 2) {
        memCache[key] = parsed
        return parsed.data
      }
    }
  } catch (e) { /* ignore */ }

  // 3. 网络请求
  try {
    const response = await fetch(url)
    const data = await response.json()
    const cacheEntry = { data, time: now }
    memCache[key] = cacheEntry
    try { localStorage.setItem(key, JSON.stringify(cacheEntry)) } catch (e) { /* quota exceeded */ }
    return data
  } catch (networkError) {
    // 4. 网络失败，返回过期缓存
    const old = memCache[key] || (() => { try { const s = localStorage.getItem(key); return s ? JSON.parse(s) : null } catch (e) { return null } })()
    if (old) { console.warn('[Offline] 使用缓存数据:', url); return old.data }
    throw networkError
  }
}

export function clearCache() {
  Object.keys(localStorage).filter(k => k.startsWith(CACHE_PREFIX)).forEach(k => localStorage.removeItem(k))
}
