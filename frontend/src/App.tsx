/**
 * 主应用组件 - 配置路由
 */
import { Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout';
import Dashboard from './pages/Dashboard';
import StockList from './pages/StockList';

// 临时占位组件
const StockDetailPage = () => <div>股票详情页面 - 待实现</div>;
const StrategiesPage = () => <div>策略管理页面 - 待实现</div>;
const BacktestPage = () => <div>回测结果页面 - 待实现</div>;
const PaperTradingPage = () => <div>模拟盘页面 - 待实现</div>;
const DataPage = () => <div>数据管理页面 - 待实现</div>;

function App() {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="stocks" element={<StockList />} />
        <Route path="stocks/:code" element={<StockDetailPage />} />
        <Route path="strategies" element={<StrategiesPage />} />
        <Route path="backtest" element={<BacktestPage />} />
        <Route path="paper-trading" element={<PaperTradingPage />} />
        <Route path="data" element={<DataPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

export default App;


