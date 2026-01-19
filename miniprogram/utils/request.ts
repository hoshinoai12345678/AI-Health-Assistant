/**
 * 网络请求工具
 */

// API基础地址
const BASE_URL = 'http://localhost:8000/api'

interface RequestOptions {
  url: string
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
}

interface ResponseData {
  code: number
  message: string
  data: any
}

/**
 * 发起网络请求
 */
export function request(options: RequestOptions): Promise<any> {
  return new Promise((resolve, reject) => {
    // 获取token
    const token = wx.getStorageSync('token')
    
    wx.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options.header
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // token过期，跳转登录
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          wx.showToast({
            title: '请先登录',
            icon: 'none'
          })
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/profile/profile'
            })
          }, 1500)
          reject(res)
        } else {
          wx.showToast({
            title: '请求失败',
            icon: 'none'
          })
          reject(res)
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * GET请求
 */
export function get(url: string, data?: any): Promise<any> {
  return request({ url, method: 'GET', data })
}

/**
 * POST请求
 */
export function post(url: string, data?: any): Promise<any> {
  return request({ url, method: 'POST', data })
}

/**
 * PUT请求
 */
export function put(url: string, data?: any): Promise<any> {
  return request({ url, method: 'PUT', data })
}

/**
 * DELETE请求
 */
export function del(url: string, data?: any): Promise<any> {
  return request({ url, method: 'DELETE', data })
}
