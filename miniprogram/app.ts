// app.ts
App({
  globalData: {
    userInfo: null,
    token: null
  },

  onLaunch() {
    console.log('AI大健康助手启动')
    
    // 检查登录状态
    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    
    if (token && userInfo) {
      this.globalData.token = token
      this.globalData.userInfo = userInfo
    }
  }
})
