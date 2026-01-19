// pages/profile/profile.ts
import { wxLogin } from '../../services/auth'

Page({
  data: {
    hasLogin: false,
    userInfo: null as any,
    roleText: ''
  },

  onLoad() {
    this.checkLogin()
  },

  onShow() {
    this.checkLogin()
  },

  /**
   * 检查登录状态
   */
  checkLogin() {
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.setData({
        hasLogin: true,
        userInfo,
        roleText: this.getRoleText(userInfo.role)
      })
    }
  },

  /**
   * 获取角色文本
   */
  getRoleText(role: string): string {
    const roleMap: any = {
      'teacher': '教师',
      'student': '学生',
      'parent': '家长',
      'admin': '管理员'
    }
    return roleMap[role] || '用户'
  },

  /**
   * 微信登录
   */
  async login() {
    try {
      // 1. 获取微信登录code
      const loginRes = await wx.login()
      
      // 2. 获取用户信息
      const userInfoRes = await wx.getUserProfile({
        desc: '用于完善用户资料'
      })
      
      // 3. 调用后端登录接口
      const res = await wxLogin({
        code: loginRes.code,
        nickname: userInfoRes.userInfo.nickName,
        avatar_url: userInfoRes.userInfo.avatarUrl,
        role: 'student'
      })
      
      // 4. 保存token和用户信息
      wx.setStorageSync('token', res.token)
      wx.setStorageSync('userInfo', res.user)
      
      this.setData({
        hasLogin: true,
        userInfo: res.user,
        roleText: this.getRoleText(res.user.role)
      })
      
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      })
    } catch (error) {
      console.error('登录失败:', error)
      wx.showToast({
        title: '登录失败',
        icon: 'none'
      })
    }
  },

  /**
   * 退出登录
   */
  logout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          wx.removeStorageSync('token')
          wx.removeStorageSync('userInfo')
          
          this.setData({
            hasLogin: false,
            userInfo: null
          })
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          })
        }
      }
    })
  },

  /**
   * 跳转到历史记录
   */
  goToHistory() {
    wx.switchTab({
      url: '/pages/history/history'
    })
  }
})
