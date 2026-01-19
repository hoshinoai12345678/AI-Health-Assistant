/**
 * 认证服务
 */
import { post, get } from '../utils/request'

interface LoginParams {
  code: string
  nickname?: string
  avatar_url?: string
  role?: string
}

interface UserInfo {
  id: number
  role: string
  nickname: string
  avatar_url: string
}

/**
 * 微信登录
 */
export async function wxLogin(params: LoginParams): Promise<any> {
  return await post('/auth/wx-login', params)
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser(token: string): Promise<UserInfo> {
  return await get(`/auth/me?token=${token}`)
}
