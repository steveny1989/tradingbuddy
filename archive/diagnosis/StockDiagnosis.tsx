import React, { useState } from 'react';
import AIDecisionCard from '../components/diagnosis/AIDecisionCard';
import RadarChart from '../components/diagnosis/RadarChart';
import MetricGauge from '../components/diagnosis/MetricGauge';
import ReasonBubbles from '../components/diagnosis/ReasonBubbles';
import { ConfidenceGauge } from '../components/diagnosis/ConfidenceGauge';
import { ValueIndicator } from '../components/diagnosis/ValueIndicator';
import { TopPicks } from '../components/diagnosis/TopPicks';
import { formatStockCode } from '../utils/stockCode';
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
        <h1>📋 决策简报</h1>
        <p>AI 驱动的智能选股情报站 - 3秒看懂一只股票</p>
      </div>

      {/* 搜索框 */}
      <div className="search-section">
        <div className="search-box">
          <input
            type="text"
            placeholder="输入股票代码或名称（如：600519 或 贵州茅台）"
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

      {/* 今日推荐 Top 10 */}
      {!report && !isLoading && !error && (
        <TopPicks />
      )}

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
          {/* 信心指数仪表盘 - 第一眼直觉 */}
          <ConfidenceGauge
            score={report.overall_score}
            conclusion={report.diagnosis_text.split('\n\n')[0]}
            level={report.overall_score >= 70 ? 'high' : report.overall_score >= 40 ? 'medium' : 'low'}
          />

          {/* AI 决策总结卡片 - 金字招牌 */}
          <AIDecisionCard
            overallScore={report.overall_score}
            signalLight={report.signal_light}
            diagnosisText={report.diagnosis_text}
            stockName={report.name}
          />

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
                <span className="info-value">{formatStockCode(report.code)}</span>
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

          {/* 多维可视化情报站 */}
          <div className="report-section dimensions">
            <h2>🎯 多维战力分析</h2>
            
            {/* 五维雷达图 + 核心指标仪表 */}
            <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 24, marginBottom: 24 }}>
              {/* 左侧：五维雷达图 */}
              <RadarChart
                technicalScore={report.technical_score.value}
                liquidityScore={report.liquidity_score.value}
                marketScore={report.market_score.value}
              />

              {/* 右侧：核心指标仪表盘 */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                <MetricGauge
                  title="技术面"
                  value={report.technical_score.value}
                  unit="分"
                  min={0}
                  max={100}
                  icon="📈"
                  comparison={report.technical_score.value >= 70 ? '技术形态优秀' : report.technical_score.value >= 40 ? '技术形态一般' : '技术形态较弱'}
                />
                <MetricGauge
                  title="流动性"
                  value={report.liquidity_score.value}
                  unit="分"
                  min={0}
                  max={100}
                  icon="💰"
                  comparison={report.liquidity_score.value >= 70 ? '交易活跃' : report.liquidity_score.value >= 40 ? '流动性一般' : '流动性较差'}
                />
                <MetricGauge
                  title="市场情绪"
                  value={report.market_score.value}
                  unit="分"
                  min={0}
                  max={100}
                  icon="🌍"
                  comparison={report.market_score.value >= 70 ? '市场环境良好' : report.market_score.value >= 40 ? '市场环境中性' : '市场环境较差'}
                />
              </div>
            </div>
            
            {/* 行业水位线指标 */}
            <div style={{ marginBottom: 24 }}>
              <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', color: 'rgba(255,255,255,0.9)' }}>📊 行业对比分析</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
                <ValueIndicator
                  title="估值水平"
                  value={report.current_price.toFixed(2)}
                  status={report.current_price < 10 ? 'excellent' : report.current_price < 20 ? 'good' : report.current_price < 50 ? 'normal' : 'poor'}
                  statusText={report.current_price < 10 ? '低价股' : report.current_price < 20 ? '中价股' : report.current_price < 50 ? '高价股' : '超高价股'}
                  position={Math.min(100, (report.current_price / 100) * 100)}
                  unit="元"
                />
                <ValueIndicator
                  title="风险等级"
                  value={(report.risk_info.volatility * 100).toFixed(1)}
                  status={report.risk_info.volatility < 0.15 ? 'excellent' : report.risk_info.volatility < 0.25 ? 'good' : report.risk_info.volatility < 0.35 ? 'normal' : 'poor'}
                  statusText={report.risk_info.risk_level}
                  position={Math.min(100, (report.risk_info.volatility / 0.5) * 100)}
                  unit="%"
                />
              </div>
            </div>
            
            {/* 核心看点 - 逻辑卡片 */}
            <div style={{ marginTop: 24 }}>
              <h3 style={{ fontSize: '1.125rem', marginBottom: '1rem', color: 'rgba(255,255,255,0.9)' }}>💡 核心看点</h3>
              <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.6)', marginBottom: '1rem' }}>AI 为你解读这只股票的关键逻辑</p>
              
              {/* 技术面 */}
              <div className="dimension-card">
                <div className="dimension-header">
                  <h3>📈 技术面看点</h3>
                  <span className="dimension-score">{report.technical_score.value.toFixed(1)} 分</span>
                </div>
                <ReasonBubbles reasons={report.technical_score.reasons} type="technical" />
              </div>

              {/* 流动性 */}
              <div className="dimension-card">
                <div className="dimension-header">
                  <h3>💰 流动性看点</h3>
                  <span className="dimension-score">{report.liquidity_score.value.toFixed(1)} 分</span>
                </div>
                <ReasonBubbles reasons={report.liquidity_score.reasons} type="liquidity" />
              </div>

              {/* 市场环境 */}
              <div className="dimension-card">
                <div className="dimension-header">
                  <h3>🌍 市场环境看点</h3>
                  <span className="dimension-score">{report.market_score.value.toFixed(1)} 分</span>
                </div>
                <ReasonBubbles reasons={report.market_score.reasons} type="market" />
              </div>
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
