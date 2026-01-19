// pages/chat/chat.ts
import { request } from '../../utils/request'

Page({
  data: {
    messages: [] as any[],
    inputText: '',
    loading: false,
    scrollToView: '',
    conversationId: null as number | null
  },

  onLoad() {
    // 添加欢迎消息
    this.addMessage({
      id: Date.now(),
      role: 'assistant',
      content: '您好！我是AI大健康助手，很高兴为您服务。您可以问我关于运动、营养、心理健康等方面的问题。',
      source: null
    })
  },

  /**
   * 输入框内容变化
   */
  onInput(e: any) {
    this.setData({
      inputText: e.detail.value
    })
  },

  /**
   * 发送消息
   */
  async sendMessage() {
    const { inputText, loading, conversationId } = this.data
    
    if (!inputText.trim() || loading) {
      return
    }

    // 检查登录状态
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/profile/profile'
        })
      }, 1500)
      return
    }

    // 添加用户消息
    this.addMessage({
      id: Date.now(),
      role: 'user',
      content: inputText
    })

    // 清空输入框
    this.setData({
      inputText: '',
      loading: true
    })

    try {
      // 调用后端API
      const res = await request({
        url: '/chat/send',
        method: 'POST',
        data: {
          message: inputText,
          conversation_id: conversationId
        },
        header: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      // 保存会话ID
      if (res.conversation_id && !conversationId) {
        this.setData({
          conversationId: res.conversation_id
        })
      }
      
      // 添加AI回复
      this.addMessage({
        id: Date.now(),
        role: 'assistant',
        content: res.message,
        source: res.source
      })
      
      // 如果有风险提示，显示
      if (res.has_risk && res.risk_warning) {
        wx.showModal({
          title: '重要提示',
          content: res.risk_warning,
          showCancel: false
        })
      }
      
    } catch (error) {
      console.error('发送消息失败:', error)
      wx.showToast({
        title: '发送失败，请重试',
        icon: 'none'
      })
    } finally {
      this.setData({
        loading: false
      })
    }
  },

  /**
   * 添加消息
   */
  addMessage(message: any) {
    const messages = this.data.messages
    messages.push(message)
    
    this.setData({
      messages,
      scrollToView: `msg-${message.id}`
    })
  }
})
