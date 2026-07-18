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

    // 获取响应文本
    const text = await response.text()

    // 尝试解析 JSON
    let data: any
    try {
      data = JSON.parse(text)
    } catch (e) {
      // 如果无法解析 JSON，可能是 HTML 错误页面
      throw new Error('服务器响应格式错误')
    }

    // 检查后端返回的错误
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
