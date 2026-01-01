/**
 * 确认对话框组件
 */
import { Modal } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

const { confirm } = Modal;

export interface ConfirmOptions {
  title: string;
  content: string;
  onConfirm: () => void | Promise<void>;
  onCancel?: () => void;
  okText?: string;
  cancelText?: string;
  okType?: 'primary' | 'danger' | 'default';
}

/**
 * 显示确认对话框
 */
export const showConfirm = ({
  title,
  content,
  onConfirm,
  onCancel,
  okText = '确定',
  cancelText = '取消',
  okType = 'primary',
}: ConfirmOptions) => {
  confirm({
    title,
    icon: <ExclamationCircleOutlined />,
    content,
    okText,
    cancelText,
    okType,
    onOk: async () => {
      await onConfirm();
    },
    onCancel: () => {
      onCancel?.();
    },
  });
};

/**
 * 显示危险操作确认对话框
 */
export const showDangerConfirm = ({
  title,
  content,
  onConfirm,
  onCancel,
  okText = '确定',
  cancelText = '取消',
}: Omit<ConfirmOptions, 'okType'>) => {
  showConfirm({
    title,
    content,
    onConfirm,
    onCancel,
    okText,
    cancelText,
    okType: 'danger',
  });
};

export default {
  showConfirm,
  showDangerConfirm,
};
