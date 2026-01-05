/**
 * 信号灯组件
 * 
 * 用红绿灯表示买卖建议
 */
import React from 'react';
import { Space, Typography, Badge } from 'antd';
import { getSignalTypeColor, getSignalLabel } from '../../utils/picker';
import type { SignalType } from '../../utils/picker';
import './SignalLight.css';

const { Text } = Typography;

/**
 * SignalLight 组件属性
 */
export interface SignalLightProps {
  signal: SignalType;
  showLabel?: boolean;  // 是否显示文字标签
  size?: 'small' | 'default' | 'large';
}

/**
 * 信号灯组件
 * 
 * 功能：
 * - 用红绿灯表示买卖建议
 * - 绿灯 = 买入建议
 * - 红灯 = 卖出建议
 * - 黄灯 = 观望
 * - 可选显示文字标签
 */
const SignalLight: React.FC<SignalLightProps> = ({ 
  signal, 
  showLabel = true,
  size = 'default'
}) => {
  const color = getSignalTypeColor(signal);
  const label = getSignalLabel(signal);
  
  // 根据信号类型设置样式
  const getSignalClass = () => {
    return `signal-light signal-${signal} signal-${size}`;
  };

  // 根据信号类型设置图标
  const renderLight = () => {
    const dotSize = size === 'small' ? 8 : size === 'large' ? 16 : 12;
    
    return (
      <div className={getSignalClass()}>
        <Badge 
          color={color}
          dot
          style={{ 
            width: dotSize, 
            height: dotSize,
          }}
        />
      </div>
    );
  };

  if (!showLabel) {
    return renderLight();
  }

  return (
    <Space size="small" className="signal-light-container">
      {renderLight()}
      <Text 
        strong 
        style={{ 
          color,
          fontSize: size === 'small' ? 12 : size === 'large' ? 16 : 14
        }}
      >
        {label}
      </Text>
    </Space>
  );
};

export default SignalLight;
