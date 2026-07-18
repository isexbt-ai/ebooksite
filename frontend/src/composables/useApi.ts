// API 请求封装
const API_BASE = import.meta.env.VITE_API_BASE || '/api'

export const useApi = () => {
  const getToken = () => {
    return localStorage.getItem('token') || ''
  }

  const request = async (url: string, options: any = {}) => {
    const headers: Record<string, string> = {
      ...options.headers,
    }

    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
      credentials: 'include',
    })

    // 检查响应是否为 JSON
    const contentType = response.headers.get('content-type')
    const isJson = contentType && contentType.includes('application/json')

    if (!isJson) {
      const text = await response.text()
      throw new Error('服务器响应格式错误')
    }

    const data = await response.json()

    if (data.err && data.err !== 'ok') {
      throw new Error(data.msg || data.err)
    }

    return data
  }

  const post = async (url: string, body: any = {}) => {
    if (body instanceof FormData) {
      return request(url, {
        method: 'POST',
        body,
      })
    }

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
