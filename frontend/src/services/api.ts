/**
 * API服务配置和请求函数
 */
import axios from 'axios';
import { notification } from '../components/common';

// 创建axios实例
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data;
  },
  (error) => {
    // 处理错误
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response;
      
      if (status === 404) {
        notification.error({
          message: '资源未找到',
          description: data.error || '请求的资源不存在',
        });
      } else if (status === 500) {
        notification.error({
          message: '服务器错误',
          description: '服务器内部错误，请稍后重试',
        });
      } else if (status === 400) {
        notification.error({
          message: '请求错误',
          description: data.error || '请求参数有误',
        });
      } else {
        notification.error({
          message: '请求失败',
          description: data.error || '请求失败，请重试',
        });
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      notification.error({
        message: '网络错误',
        description: '无法连接到服务器，请检查网络连接',
      });
    } else {
      // 其他错误
      notification.error({
        message: '请求错误',
        description: error.message || '请求配置错误',
      });
    }
    
    return Promise.reject(error);
  }
);

export default api;
