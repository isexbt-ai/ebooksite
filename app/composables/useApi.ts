// API 请求封装 - Nuxt auto-imported composable
export const useApi = () => {
  const { token } = useAuthStore()

  const request = async (url: string, options: any = {}) => {
    const headers: Record<string, string> = {
      ...options.headers,
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(url, {
      ...options,
      headers,
      credentials: 'include',
    })

    const data = await response.json()

    if (data.err && data.err !== 'ok') {
      throw new Error(data.msg || data.err)
    }

    return data
  }

  const post = async (url: string, body: any = {}) => {
    // 根据 body 类型决定发送格式
    // 如果 body 是 FormData，不设置 Content-Type，让浏览器自动设置
    if (body instanceof FormData) {
      return request(url, {
        method: 'POST',
        body,
      })
    }

    // 默认发送 JSON
    return request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
  }

  const get = async (url: string) => {
    return request(url, {
      method: 'GET',
    })
  }

  return { request, post, get }
}
