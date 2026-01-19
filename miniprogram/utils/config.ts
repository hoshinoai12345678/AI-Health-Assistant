/**
 * API配置
 */
export const API_CONFIG = {
  // 开发环境
  DEV_BASE_URL: 'http://localhost:8000',
  
  // 生产环境（替换为你的实际域名）
  PROD_BASE_URL: 'https://your-api-domain.com',
  
  // 当前使用的环境
  BASE_URL: 'http://localhost:8000',
  
  // 请求超时时间
  TIMEOUT: 30000
};

/**
 * 微信小程序配置
 */
export const WECHAT_CONFIG = {
  // 小程序AppID（替换为你的实际AppID）
  APP_ID: 'your_appid_here',
  
  // 小程序名称
  APP_NAME: 'AI健康助手'
};

/**
 * 获取当前环境的API地址
 */
export function getApiBaseUrl(): string {
  // 可以根据环境变量或其他条件判断
  return API_CONFIG.BASE_URL;
}
