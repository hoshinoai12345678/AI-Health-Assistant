// pages/index/index.ts
Page({
  data: {},

  onLoad() {
    console.log('首页加载')
  },

  /**
   * 跳转到AI对话页面
   */
  goToChat() {
    wx.switchTab({
      url: '/pages/chat/chat'
    })
  }
})
