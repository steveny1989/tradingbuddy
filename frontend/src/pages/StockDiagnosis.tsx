import React, { useState } from 'react';
import './StockDiagnosis.css';

interface Stock {
  code: string;
  name: string;
  market: string;
}

interface DiagnosisReport {
  code: string;
  name: string;
  current_price: number;
  change_pct: number;
  overall_score: number;
  technical_score: {
    value: number;
    reasons: string[];
  };
  liquidity_score: {
    value: number;
    reasons: string[];
  };
  market_score: {
    value: number;
    reasons: string[];
  };
  signal_light: {
    color: string;
    label: string;
    confidence: number;
    reason: string;
  };
  risk_info: {
    current_price: number;
    stop_loss_price: number;
    stop_loss_pct: number;
    take_profit_price: number;
    take_profit_pct: number;
    risk_reward_ratio: number;
    volatility: number;
    risk_level: string;
    warnings: string[];
  };
  diagnosis_text: string;
  disclaimer: string;
  data_source: string;
  data_coverage: string;
  data_update_time: string | null;
}

const StockDiagnosis: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Stock[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [report, setReport] = useState<DiagnosisReport | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 搜索股票
  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const response = await fetch(`http://localhost:5001/api/diagnosis/search?q=${encodeURIComponent(query)}`);
      const data = await response.json();
      setSearchResults(data.stocks || []);
    } catch (err) {
      console.error('搜索失败:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // 诊断股票
  const handleDiagnose = async (code: string) => {
    setIsLoading(true);
    setError(null);
    setSearchResults([]);
    setSearchQuery('');

    try {
      const response = await fetch(`http://localhost:5001/api/diagnosis/${code}`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || '诊断失败');
      }

      const data = await response.json();
      setReport(data);
    } catch (err: any) {
      setError(err.message || '诊断失败，请稍后重试');
      setReport(null);
    } finally {
      setIsLoading(false);
    }
  };

  // 获取信号灯颜色
  const getSignalColor = (color: string) => {
    switch (color) {
      case 'GREEN': return '#10b981';
      case 'YELLOW': return '#f59e0b';
      case 'RED': return '#ef4444';
      default: return '#6b7280';
    }
  };

  // 获取信号灯 emoji
  const getSignalEmoji = (color: string) => {
    switch (color) {
      case 'GREEN': return '🟢';
      case 'YELLOW': return '🟡';
      case 'RED': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <div className="diagnosis-container">
      <div className="diagnosis-header">
        <h1>🏥 个股诊断</h1>
        <p>输入股票代码或名称，获取客观的诊断分析</p>
      </div>

      {/* 搜索框 */}
      <div className="search-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="输入股票代码或名称（如：000060 或 中金岭南）"
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="search-input"
          />
          {isSearching && <div className="search-loading">搜索中...</div>}
        </div>

        {/* 搜索结果 */}
        {searchResults.length > 0 && (
          <div className="search-results">
            {searchResults.map((stock) => (
              <div
                key={stock.code}
                className="search-result-item"
                onClick={() => handleDiagnose(stock.code)}
              >
                <span className="stock-code">{stock.code}</span>
                <span className="stock-name">{stock.name}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 加载状态 */}
      {isLoading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>正在诊断中...</p>
        </div>
      )}

      {/* 错误信息 */}
      {error && (
        <div className="error-container">
          <p>❌ {error}</p>
        </div>
      )}

      {/* 诊断报告 */}
      {report && !isLoading && (
        <div className="report-container">
          {/* 基本信息 */}
          <div className="report-section basic-info">
            <h2>📊 基本信息</h2>
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">股票名称</span>
                <span className="info-value">{report.name}</span>
              </div>
              <div className="info-item">
                <span className="info-label">股票代码</span>
                <span className="info-value">{report.code}</span>
              </div>
              <div className="info-item">
                <span className="info-label">当前价格</span>
                <span className="info-value price">{report.current_price.toFixed(2)} 元</span>
              </div>
              <div className="info-item">
                <span className="info-label">涨跌幅</span>
                <span className={`info-value ${report.change_pct >= 0 ? 'positive' : 'negative'}`}>
                  {report.change_pct >= 0 ? '+' : ''}{report.change_pct.toFixed(2)}%
                </span>
              </div>
            </div>
          </div>

          {/* 综合评分 */}
          <div className="report-section overall-score">
            <h2>⭐ 综合评分</h2>
            <div className="score-display">
              <div className="score-number">{report.overall_score.toFixed(1)}</div>
              <div className="score-label">分</div>
            </div>
          </div>

          {/* 各维度评分 */}
          <div className="report-section dimensions">
            <h2>📈 各维度评分</h2>
            
            {/* 技术面 */}
            <div className="dimension-card">
              <div className="dimension-header">
                <h3>📈 技术面评分</h3>
                <span className="dimension-score">{report.technical_score.value.toFixed(1)} 分</span>
              </div>
              <ul className="dimension-reasons">
                {report.technical_score.reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>

            {/* 流动性 */}
            <div className="dimension-card">
              <div className="dimension-header">
                <h3>💰 流动性评分</h3>
                <span className="dimension-score">{report.liquidity_score.value.toFixed(1)} 分</span>
              </div>
              <ul className="dimension-reasons">
                {report.liquidity_score.reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>

            {/* 市场环境 */}
            <div className="dimension-card">
              <div className="dimension-header">
                <h3>🌍 市场环境评分</h3>
                <span className="dimension-score">{report.market_score.value.toFixed(1)} 分</span>
              </div>
              <ul className="dimension-reasons">
                {report.market_score.reasons.map((reason, idx) => (
                  <li key={idx}>{reason}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* 信号灯 */}
          <div className="report-section signal-light">
            <h2>🚦 信号灯评价</h2>
            <div className="signal-display" style={{ borderColor: getSignalColor(report.signal_light.color) }}>
              <div className="signal-icon">{getSignalEmoji(report.signal_light.color)}</div>
              <div className="signal-info">
                <div className="signal-label" style={{ color: getSignalColor(report.signal_light.color) }}>
                  {report.signal_light.label}
                </div>
                <div className="signal-confidence">信号强度: {report.signal_light.confidence.toFixed(1)}</div>
                <div className="signal-reason">{report.signal_light.reason}</div>
              </div>
            </div>
          </div>

          {/* 风险管理 */}
          <div className="report-section risk-management">
            <h2>⚠️ 风险管理指南</h2>
            <div className="risk-grid">
              <div className="risk-item">
                <span className="risk-label">当前价格</span>
                <span className="risk-value">{report.risk_info.current_price.toFixed(2)} 元</span>
              </div>
              <div className="risk-item">
                <span className="risk-label">建议止损</span>
                <span className="risk-value stop-loss">
                  {report.risk_info.stop_loss_price.toFixed(2)} 元 
                  ({(report.risk_info.stop_loss_pct * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="risk-item">
                <span className="risk-label">建议止盈</span>
                <span className="risk-value take-profit">
                  {report.risk_info.take_profit_price.toFixed(2)} 元 
                  ({(report.risk_info.take_profit_pct * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="risk-item">
                <span className="risk-label">盈亏比</span>
                <span className="risk-value">{report.risk_info.risk_reward_ratio.toFixed(2)}:1</span>
              </div>
              <div className="risk-item">
                <span className="risk-label">风险等级</span>
                <span className={`risk-value risk-level-${report.risk_info.risk_level.toLowerCase()}`}>
                  {report.risk_info.risk_level}
                </span>
              </div>
              <div className="risk-item">
                <span className="risk-label">波动率</span>
                <span className="risk-value">{(report.risk_info.volatility * 100).toFixed(1)}%</span>
              </div>
            </div>

            {report.risk_info.warnings.length > 0 && (
              <div className="risk-warnings">
                <h4>⚠️ 风险警告</h4>
                <ul>
                  {report.risk_info.warnings.map((warning, idx) => (
                    <li key={idx}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* 诊断意见 */}
          <div className="report-section diagnosis-opinion">
            <h2>💬 诊断意见（大白话）</h2>
            <div className="diagnosis-text">
              {report.diagnosis_text.split('\n\n').map((paragraph, idx) => (
                <p key={idx}>{paragraph}</p>
              ))}
            </div>
          </div>

          {/* 免责声明 */}
          <div className="report-section disclaimer">
            <h2>📋 免责声明</h2>
            <p>{report.disclaimer}</p>
            <div className="data-info">
              <p><strong>数据来源:</strong> {report.data_source}</p>
              <p><strong>数据覆盖:</strong> {report.data_coverage}</p>
              {report.data_update_time && (
                <p><strong>数据更新时间:</strong> {report.data_update_time}</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default StockDiagnosis;
