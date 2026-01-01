/**
 * 通知工具函数
 */
import { notification as antNotification } from 'antd';
import type { NotificationPlacement } from 'antd/es/notification/interface';

// 配置默认设置
antNotification.config({
  placement: 'topRight' as NotificationPlacement,
  duration: 3,
  maxCount: 3,
});

export interface NotificationOptions {
  message: string;
  description?: string;
  duration?: number;
  placement?: NotificationPlacement;
}

/**
 * 成功通知
 */
export const success = ({ message, description, duration = 3 }: NotificationOptions) => {
  antNotification.success({
    message,
    description,
    duration,
  });
};

/**
 * 错误通知
 */
export const error = ({ message, description, duration = 4 }: NotificationOptions) => {
  antNotification.error({
    message,
    description,
    duration,
  });
};

/**
 * 警告通知
 */
export const warning = ({ message, description, duration = 3 }: NotificationOptions) => {
  antNotification.warning({
    message,
    description,
    duration,
  });
};

/**
 * 信息通知
 */
export const info = ({ message, description, duration = 3 }: NotificationOptions) => {
  antNotification.info({
    message,
    description,
    duration,
  });
};

export default {
  success,
  error,
  warning,
  info,
};
