/**
 * 主应用组件 - 配置路由和主题
 */
import { ConfigProvider } from 'antd';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout';
import SimplePicker from './pages/SimplePicker.premium'; // 使用 Premium 版本
import SimpleStockDetail from './pages/SimpleStockDetail.premium'; // 使用 Premium 版本
import Dashboard from './pages/Dashboard';
import StockList from './pages/StockList';
import StockDetail from './pages/StockDetail';
import { tradingTheme } from './theme/tradingTheme';
import './styles/premium.css'; // 导入 Premium 样式

// 临时占位组件
const StrategiesPage = () => <div>策略管理页面 - 待实现</div>;
const BacktestPage = () => <div>回测结果页面 - 待实现</div>;
const PaperTradingPage = () => <div>模拟盘页面 - 待实现</div>;
const DataPage = () => <div>数据管理页面 - 待实现</div>;

function App() {
  return (
    <ConfigProvider theme={tradingTheme}>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          {/* 极简选股助手作为首页 */}
          <Route index element={<SimplePicker />} />
          {/* 极简股票详情页 */}
          <Route path="picker/stocks/:code" element={<SimpleStockDetail />} />
          {/* 原有的仪表板页面保留，可通过 /dashboard 访问 */}
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="stocks" element={<StockList />} />
          <Route path="stocks/:code" element={<StockDetail />} />
          <Route path="strategies" element={<StrategiesPage />} />
          <Route path="backtest" element={<BacktestPage />} />
          <Route path="paper-trading" element={<PaperTradingPage />} />
          <Route path="data" element={<DataPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </ConfigProvider>
  );
}

export default App;


