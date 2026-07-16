// API 请求封装
export const useApi = () => {
  const config = useRuntimeConfig()
  const { token } = useAuthStore()

  const baseURL = config.public.apiBase || 'http://127.0.0.1:8080'

  const request = async (url: string, options: any = {}) => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/x-www-form-urlencoded',
      ...options.headers,
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(`${baseURL}${url}`, {
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
