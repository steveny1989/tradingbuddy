/**
 * 数据流颗粒背景组件
 * Data Flow Particles Background
 */
import React from 'react';

const DataParticles: React.FC = () => {
  return (
    <div className="data-particles">
      {[...Array(10)].map((_, index) => (
        <div key={index} className="particle" />
      ))}
    </div>
  );
};

export default DataParticles;
