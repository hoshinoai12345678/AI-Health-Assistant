// pages/history/history.ts
import { request } from '../../utils/request'

Page({
  data: {
    conversations: [] as any[],
    loading: false
  },

  onLoad() {
    this.loadHistory()
  },

  onShow() {
    this.loadHistory()
  },

  /**
   * 加载历史记录
   */
  async loadHistory() {
    const token = wx.getStorageSync('token')
    if (!token) {
      return
    }

    this.setData({ loading: true })
    
    try {
      const res = await request({
        url: `/conversation/list?token=${token}`,
        method: 'GET'
      })
      
      this.setData({
        conversations: res,
        loading: false
      })
    } catch (error) {
      console.error('加载历史失败:', error)
      this.setData({ loading: false })
    }
  },

  /**
   * 打开对话
   */
  openConversation(e: any) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/chat/chat?id=${id}`
    })
  },

  /**
   * 删除对话
   */
  async deleteConversation(e: any) {
    const id = e.currentTarget.dataset.id
    const token = wx.getStorageSync('token')
    
    const res = await wx.showModal({
      title: '提示',
      content: '确定要删除这条对话记录吗？'
    })
    
    if (res.confirm) {
      try {
        await request({
          url: `/conversation/${id}?token=${token}`,
          method: 'DELETE'
        })
        
        wx.showToast({
          title: '删除成功',
          icon: 'success'
        })
        
        // 重新加载列表
        this.loadHistory()
      } catch (error) {
        wx.showToast({
          title: '删除失败',
          icon: 'none'
        })
      }
    }
  },

  /**
   * 跳转到对话页
   */
  goToChat() {
    wx.switchTab({
      url: '/pages/chat/chat'
    })
  }
})
