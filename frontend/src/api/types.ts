// API 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  data: T
  message: string
}

// 分页响应
export interface PaginatedData<T> {
  total: number
  items: T[]
  page: number
  size: number
}

// 用户
export interface User {
  id: number
  username: string
  name: string | null
  email: string | null
  avatar: string | null
  admin: boolean
  active: boolean
  expiry_date: string | null
  created_at?: string
}

// 书籍
export interface Book {
  id: number
  title: string
  author: string | null
  category: string | null
  tags: string | null
  description: string | null
  cover_url: string | null
  r2_key: string | null
  r2_url: string | null
  file_size: number | null
  file_format: string | null
  mime_type: string | null
  upload_status: string
  file_hash: string | null
  search_count: number
  created_at: string
  updated_at: string
}

// 卡密
export interface Card {
  id: number
  code: string
  type: string
  duration_days: number
  used: boolean
  used_by: number | null
  used_at: string | null
  expires_at: string | null
  created_at: string
}

// 反馈
export interface Feedback {
  id: number
  user_id: number | null
  content: string
  contact: string | null
  status: string
  created_at: string
}

// 下载记录
export interface Download {
  id: number
  user_id: number
  book_id: number
  book?: Pick<Book, 'id' | 'title' | 'author' | 'file_format' | 'file_size'>
  created_at: string
}

// 仪表盘数据
export interface DashboardData {
  total_users: number
  active_users: number
  expired_users: number
  total_books: number
  total_cards: number
  used_cards: number
  total_downloads: number
  today_downloads: number
  pending_feedbacks: number
}

// 系统设置
export type Settings = Record<string, string>

// 登录响应
export interface LoginData {
  user_id: number
  username: string
  name: string
  admin: boolean
  expiry_date: string | null
  token: string
}

// 注册响应
export interface RegisterData {
  user_id: number
  username: string
  expiry_date: string
}
