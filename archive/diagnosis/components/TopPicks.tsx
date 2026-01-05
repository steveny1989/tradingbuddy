import React, { useEffect, useState } from 'react';
import './TopPicks.css';

interface TopPick {
  code: string;
  name: string;
  overall_score: number;
  reason: string;
  strategy_name: string;
  price: number;
}

export const TopPicks: React.FC = () => {
  const [picks, setPicks] = useState<TopPick[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopPicks();
  }, []);

  const loadTopPicks = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/diagnosis/top-picks');
      const result = await response.json();
      
      if (result.success && result.data) {
        setPicks(result.data);
      }
    } catch (error) {
      console.error('加载 Top 10 失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePickClick = (code: string) => {
    // 触发搜索并诊断
    window.location.href = `/diagnosis?code=${code}`;
  };

  const getScoreColor = (score: number) => {
    if (score >= 70) return '#fbbf24'; // 金色
    if (score >= 60) return '#60a5fa'; // 蓝色
    return '#94a3b8'; // 灰色
  };

  const getScoreLabel = (score: number) => {
    if (score >= 70) return '强烈推荐';
    if (score >= 60) return '值得关注';
    return '谨慎观察';
  };

  if (loading) {
    return (
      <div className="top-picks-loading">
        <div className="loading-spinner"></div>
        <p>正在加载今日推荐...</p>
      </div>
    );
  }

  if (picks.length === 0) {
    return (
      <div className="top-picks-empty">
        <p>暂无推荐股票，请点击右上角同步按钮获取最新数据</p>
      </div>
    );
  }

  return (
    <div className="top-picks-container">
      <div className="top-picks-header">
        <h2 className="top-picks-title">
          <span className="title-icon">🏆</span>
          今日推荐 Top 10
        </h2>
        <p className="top-picks-subtitle">
          基于 AI 多维度分析，为你精选最具潜力的股票
        </p>
      </div>

      <div className="top-picks-grid">
        {picks.map((pick, index) => (
          <div
            key={pick.code}
            className="pick-card"
            onClick={() => handlePickClick(pick.code)}
          >
            <div className="pick-rank">
              <span className={`rank-number ${index < 3 ? 'top-three' : ''}`}>
                {index + 1}
              </span>
            </div>

            <div className="pick-content">
              <div className="pick-header">
                <h3 className="pick-name">{pick.name}</h3>
                <span className="pick-code">{pick.code.split('.')[1] || pick.code}</span>
              </div>

              <div className="pick-score">
                <div 
                  className="score-badge"
                  style={{ backgroundColor: getScoreColor(pick.overall_score) }}
                >
                  <span className="score-value">{Math.round(pick.overall_score)}</span>
                  <span className="score-label">分</span>
                </div>
                <span className="score-text" style={{ color: getScoreColor(pick.overall_score) }}>
                  {getScoreLabel(pick.overall_score)}
                </span>
              </div>

              <div className="pick-strategy">
                <span className="strategy-tag">{pick.strategy_name}</span>
              </div>

              <div className="pick-reason">
                {pick.reason}
              </div>
            </div>

            <div className="pick-arrow">→</div>
          </div>
        ))}
      </div>

      <div className="top-picks-footer">
        <p className="footer-note">
          💡 点击任意股票查看详细诊断报告
        </p>
      </div>
    </div>
  );
};
