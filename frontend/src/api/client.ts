import type { ApiResponse } from '@/api/types'

const API_BASE = '/api'

class ApiClient {
  private getToken(): string {
    return localStorage.getItem('token') || ''
  }

  async request<T>(url: string, options: RequestInit = {}): Promise<ApiResponse<T>> {
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    }

    const token = this.getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const response = await fetch(`${API_BASE}${url}`, {
      ...options,
      headers,
    })

    const text = await response.text()
    let data: ApiResponse<T>
    try {
      data = JSON.parse(text)
    } catch {
      throw new Error('服务器响应格式错误')
    }

    // 统一错误处理
    if (response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 触发自定义事件，通知 store 清除状态
      window.dispatchEvent(new CustomEvent('auth:expired'))
      throw new Error('登录已过期，请重新登录')
    }

    if (data.code !== 0) {
      throw new Error(data.message || '请求失败')
    }

    return data
  }

  async get<T>(url: string): Promise<ApiResponse<T>> {
    return this.request<T>(url, { method: 'GET' })
  }

  async post<T>(url: string, body?: any): Promise<ApiResponse<T>> {
    if (body instanceof FormData) {
      return this.request<T>(url, {
        method: 'POST',
        body,
      })
    }
    return this.request<T>(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async put<T>(url: string, body?: any): Promise<ApiResponse<T>> {
    return this.request<T>(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async delete<T>(url: string): Promise<ApiResponse<T>> {
    return this.request<T>(url, { method: 'DELETE' })
  }
}

export const api = new ApiClient()
