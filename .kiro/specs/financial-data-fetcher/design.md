# Design Document - Financial Data Fetcher System

## Overview

财务数据采集系统是TradingBuddy的核心数据模块之一，负责从新浪财经API获取上市公司的财务报表数据。系统采用Python实现，使用akshare库作为数据源接口，SQLite作为本地存储。

**核心目标：**
- 准确区分成功和失败的数据获取操作
- 提供详细的错误分类和诊断信息
- 实现健壮的重试机制处理临时性错误
- 计算财务指标弥补API数据缺失
- 支持高效的批量下载和增量更新

**技术栈：**
- Python 3.8+
- akshare (数据源)
- pandas (数据处理)
- SQLite (数据存储)
- logging (日志记录)
- tqdm (进度显示)

## Architecture

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Financial Data Fetcher                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐      ┌──────────────────┐            │
│  │  Fetcher Layer   │      │  Calculator      │            │
│  │                  │      │  Layer           │            │
│  │ - fetch_*()      │      │                  │            │
│  │ - retry logic    │      │ - calculate_*()  │            │
│  │ - error classify │      │ - validate()     │            │
│  └────────┬─────────┘      └────────┬─────────┘            │
│           │                         │                       │
│           v                         v                       │
│  ┌──────────────────────────────────────────┐              │
│  │         Result Aggregator                │              │
│  │  - success/failure determination         │              │
│  │  - error type classification             │              │
│  │  - statistics collection                 │              │
│  └────────────────┬─────────────────────────┘              │
│                   │                                         │
└───────────────────┼─────────────────────────────────────────┘
                    │
                    v
         ┌──────────────────────┐
         │   StockDatabase      │
         │                      │
         │ - balance_sheet      │
         │ - income_statement   │
         │ - cash_flow          │
         │ - financial_indicators│
         └──────────────────────┘
                    ^
                    │
         ┌──────────┴──────────┐
         │   Sina Finance API  │
         │   (via akshare)     │
         └─────────────────────┘
```

### 数据流

1. **单股票获取流程：**
   ```
   fetch_all_financial_data(code)
   ├─> fetch_balance_sheet(code) ──> [retry if needed] ──> save_balance_sheet()
   ├─> fetch_income_statement(code) ──> [retry if needed] ──> save_income_statement()
   ├─> fetch_cash_flow(code) ──> [retry if needed] ──> save_cash_flow()
   ├─> calculate_financial_indicators() ──> save_financial_indicators()
   └─> determine_success_status() ──> return result
   ```

2. **批量下载流程：**
   ```
   batch_fetch_financial_data(codes)
   ├─> for each code:
   │   ├─> check_if_needs_update()
   │   ├─> fetch_all_financial_data(code)
   │   └─> collect_statistics()
   ├─> generate_report()
   └─> save_failed_list()
   ```

## Components and Interfaces

### 1. FinancialDataFetcher (主类)

**职责：** 协调所有财务数据获取操作

**主要方法：**

```python
class FinancialDataFetcher:
    def __init__(self, db: StockDatabase):
        """初始化采集器"""
        
    def fetch_all_financial_data(
        self, 
        code: str, 
        save_to_db: bool = True,
        force_update: bool = False
    ) -> FetchResult:
        """获取单只股票的所有财务数据"""
        
    def batch_fetch_financial_data(
        self,
        codes: List[str] = None,
        max_stocks: int = None,
        force_update: bool = False,
        resume_from: str = None
    ) -> BatchResult:
        """批量获取财务数据"""
        
    def retry_failed_stocks(
        self,
        failed_list_file: str
    ) -> BatchResult:
        """重新下载失败的股票"""
```

### 2. StatementFetcher (报表获取器)

**职责：** 获取三大财务报表

**主要方法：**

```python
class StatementFetcher:
    def fetch_balance_sheet(
        self, 
        code: str,
        max_retries: int = 3
    ) -> FetchResult:
        """获取资产负债表（带重试）"""
        
    def fetch_income_statement(
        self, 
        code: str,
        max_retries: int = 3
    ) -> FetchResult:
        """获取利润表（带重试）"""
        
    def fetch_cash_flow(
        self, 
        code: str,
        max_retries: int = 3
    ) -> FetchResult:
        """获取现金流量表（带重试）"""
        
    def _retry_with_backoff(
        self,
        func: Callable,
        max_retries: int,
        backoff_factor: float = 2.0
    ) -> FetchResult:
        """带指数退避的重试机制"""
```

### 3. FinancialCalculator (财务指标计算器)

**职责：** 从三大报表计算财务指标

**主要方法：**

```python
class FinancialCalculator:
    @staticmethod
    def calculate_indicators(
        balance_sheet: pd.DataFrame,
        income_statement: pd.DataFrame,
        cash_flow: pd.DataFrame
    ) -> pd.DataFrame:
        """计算所有财务指标"""
        
    @staticmethod
    def calculate_roe(
        net_profit: float,
        shareholders_equity: float
    ) -> Optional[float]:
        """计算ROE（净资产收益率）"""
        
    @staticmethod
    def calculate_roa(
        net_profit: float,
        total_assets: float
    ) -> Optional[float]:
        """计算ROA（总资产收益率）"""
        
    @staticmethod
    def calculate_gross_margin(
        revenue: float,
        cost: float
    ) -> Optional[float]:
        """计算毛利率"""
        
    @staticmethod
    def calculate_current_ratio(
        current_assets: float,
        current_liabilities: float
    ) -> Optional[float]:
        """计算流动比率"""
        
    @staticmethod
    def calculate_quick_ratio(
        current_assets: float,
        inventory: float,
        current_liabilities: float
    ) -> Optional[float]:
        """计算速动比率"""
```

### 4. ErrorClassifier (错误分类器)

**职责：** 分类和记录错误信息

**错误类型枚举：**

```python
class ErrorType(Enum):
    API_ERROR = "API_ERROR"           # JSON解析错误等API问题
    NETWORK_ERROR = "NETWORK_ERROR"   # 网络连接失败
    EMPTY_DATA = "EMPTY_DATA"         # API返回空数据
    VALIDATION_ERROR = "VALIDATION_ERROR"  # 数据验证失败
    DATABASE_ERROR = "DATABASE_ERROR"  # 数据库操作失败
    UNKNOWN_ERROR = "UNKNOWN_ERROR"    # 未知错误
```

**主要方法：**

```python
class ErrorClassifier:
    @staticmethod
    def classify_error(exception: Exception) -> ErrorType:
        """根据异常类型分类错误"""
        
    @staticmethod
    def should_retry(error_type: ErrorType) -> bool:
        """判断是否应该重试"""
        
    @staticmethod
    def get_retry_count(error_type: ErrorType) -> int:
        """获取建议的重试次数"""
```

### 5. DataValidator (数据验证器)

**职责：** 验证数据完整性和有效性

**主要方法：**

```python
class DataValidator:
    @staticmethod
    def validate_report_date(date_str: str) -> bool:
        """验证报告日期格式"""
        
    @staticmethod
    def validate_numeric_field(value: Any) -> bool:
        """验证数值字段"""
        
    @staticmethod
    def validate_dataframe(
        df: pd.DataFrame,
        required_columns: List[str]
    ) -> ValidationResult:
        """验证DataFrame完整性"""
        
    @staticmethod
    def has_valid_data(df: pd.DataFrame) -> bool:
        """检查DataFrame是否有有效数据（非全None）"""
```

### 6. ProgressTracker (进度跟踪器)

**职责：** 跟踪和显示下载进度

**主要方法：**

```python
class ProgressTracker:
    def __init__(self, total: int):
        """初始化进度跟踪器"""
        
    def update(
        self,
        success: bool,
        error_type: Optional[ErrorType] = None
    ):
        """更新进度"""
        
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        
    def save_report(self, filepath: str):
        """保存下载报告"""
        
    def save_failed_list(self, filepath: str):
        """保存失败股票列表"""
```

## Data Models

### FetchResult (获取结果)

```python
@dataclass
class FetchResult:
    """单次数据获取结果"""
    code: str
    success: bool
    has_data: bool  # 是否有任何数据被保存
    error_type: Optional[ErrorType] = None
    error_details: Optional[str] = None
    retry_count: int = 0
    data: Optional[Dict[str, pd.DataFrame]] = None
    
    # 各报表的获取状态
    balance_sheet_status: FetchStatus = FetchStatus.NOT_STARTED
    income_statement_status: FetchStatus = FetchStatus.NOT_STARTED
    cash_flow_status: FetchStatus = FetchStatus.NOT_STARTED
    indicators_status: FetchStatus = FetchStatus.NOT_STARTED
```

### BatchResult (批量获取结果)

```python
@dataclass
class BatchResult:
    """批量获取结果"""
    total: int
    success: int
    failed: int
    
    # 按错误类型分类的失败统计
    error_stats: Dict[ErrorType, int]
    
    # 失败股票列表（按错误类型分组）
    failed_stocks: Dict[ErrorType, List[str]]
    
    # 性能统计
    start_time: datetime
    end_time: datetime
    avg_speed: float  # 股票/秒
    
    # 报告文件路径
    report_file: Optional[str] = None
    failed_list_file: Optional[str] = None
```

### FetchStatus (获取状态)

```python
class FetchStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
```

### ValidationResult (验证结果)

```python
@dataclass
class ValidationResult:
    """数据验证结果"""
    valid: bool
    errors: List[str]
    warnings: List[str]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Success determination based on data presence
*For any* stock fetch operation, the success flag should be True if and only if at least one financial statement was successfully saved to the database.
**Validates: Requirements 1.1, 1.2**

### Property 2: Result structure completeness
*For any* fetch operation result, the result dictionary should contain the fields: code, success, has_data, error_type, and error_details.
**Validates: Requirements 1.3, 2.4, 2.5**

### Property 3: Error type classification
*For any* failed fetch operation, the error_type field should correctly classify the failure as one of: API_ERROR, NETWORK_ERROR, EMPTY_DATA, VALIDATION_ERROR, DATABASE_ERROR, or UNKNOWN_ERROR.
**Validates: Requirements 1.5, 2.1, 2.2, 2.3**

### Property 4: Batch statistics accuracy
*For any* batch fetch operation, the sum of success count and failed count should equal the total count, and the error_stats counts should sum to the failed count.
**Validates: Requirements 3.1, 3.2, 3.3**

### Property 5: Failed stocks grouping
*For any* batch fetch operation, all failed stock codes should appear in the failed_stocks dictionary grouped by their error_type, with no duplicates.
**Validates: Requirements 3.5**

### Property 6: Financial indicator calculations are safe
*For any* set of financial statement values, calculating indicators (ROE, ROA, gross_margin, etc.) should return None when inputs are invalid (None, zero denominators) rather than raising exceptions.
**Validates: Requirements 4.8**

### Property 7: ROE calculation correctness
*For any* valid net_profit and shareholders_equity values (both non-None, equity non-zero), ROE should equal net_profit / shareholders_equity * 100.
**Validates: Requirements 4.1**

### Property 8: Current ratio calculation correctness
*For any* valid current_assets and current_liabilities values (both non-None, liabilities non-zero), current_ratio should equal current_assets / current_liabilities.
**Validates: Requirements 4.6**

### Property 9: Quick ratio calculation correctness
*For any* valid current_assets, inventory, and current_liabilities values (all non-None, liabilities non-zero), quick_ratio should equal (current_assets - inventory) / current_liabilities.
**Validates: Requirements 4.7**

### Property 10: Date format validation
*For any* date string, the validator should return True only if the string matches the format YYYY-MM-DD with valid year, month, and day values.
**Validates: Requirements 7.1**

### Property 11: Report type validation
*For any* report_type value, the validator should return True only if the value is one of: 'Q1', 'Q2', 'Q3', 'annual'.
**Validates: Requirements 7.4**

### Property 12: All-None record rejection
*For any* DataFrame row where all data fields (excluding metadata like code, date) are None, the row should be filtered out before database insertion.
**Validates: Requirements 7.3**

### Property 13: Update frequency enforcement
*For any* stock with existing financial data updated within the last 7 days, the fetch operation should skip that stock unless force_update is True.
**Validates: Requirements 9.2, 9.3**

### Property 14: Timestamp recording
*For any* successful data save operation, the updated_at timestamp should be recorded and should be within 1 second of the current time.
**Validates: Requirements 9.5, 10.1**

### Property 15: Average speed calculation
*For any* completed batch operation, the average speed should equal total_stocks / elapsed_seconds, where elapsed_seconds = end_time - start_time.
**Validates: Requirements 10.2**

### Property 16: High failure rate alerting
*For any* batch operation where (failed_count / total_count) > 0.20, an ERROR level log entry should be generated.
**Validates: Requirements 10.3**

### Property 17: Custom stock list processing
*For any* provided list of stock codes, the batch fetch should process exactly those codes and no others.
**Validates: Requirements 6.2**

### Property 18: Report file generation
*For any* completed batch operation, a report file should be generated containing at minimum: total count, success count, failed count, error statistics, and elapsed time.
**Validates: Requirements 3.4, 10.4**

### Property 19: Failed list file generation
*For any* batch operation with failures, a failed list file should be generated containing all failed stock codes grouped by error type.
**Validates: Requirements 6.3**

## Error Handling

### Error Classification Strategy

The system classifies errors into distinct categories to enable appropriate handling:

1. **API_ERROR**: JSON parsing failures, malformed responses
   - Retry: Yes (max 2 times)
   - Log Level: ERROR
   - User Action: Check API status, report if persistent

2. **NETWORK_ERROR**: Connection timeouts, DNS failures
   - Retry: Yes (max 3 times)
   - Log Level: ERROR
   - User Action: Check network connection

3. **EMPTY_DATA**: API returns empty DataFrame
   - Retry: No
   - Log Level: WARNING
   - User Action: Normal for some stocks (newly listed, delisted, ST)

4. **VALIDATION_ERROR**: Data fails validation checks
   - Retry: No
   - Log Level: WARNING
   - User Action: Review data quality

5. **DATABASE_ERROR**: SQLite operation failures
   - Retry: No
   - Log Level: ERROR
   - User Action: Check database integrity, disk space

6. **UNKNOWN_ERROR**: Unexpected exceptions
   - Retry: No
   - Log Level: ERROR
   - User Action: Report with stack trace

### Retry Logic

```python
def _retry_with_backoff(func, max_retries, backoff_factor=2.0):
    """
    Exponential backoff retry strategy:
    - Attempt 1: immediate
    - Attempt 2: wait 1 second
    - Attempt 3: wait 2 seconds
    - Attempt 4: wait 4 seconds
    """
    for attempt in range(max_retries + 1):
        try:
            result = func()
            if attempt > 0:
                logger.info(f"Retry succeeded on attempt {attempt + 1}")
            return result
        except Exception as e:
            error_type = ErrorClassifier.classify_error(e)
            
            if not ErrorClassifier.should_retry(error_type):
                return FetchResult(success=False, error_type=error_type)
            
            if attempt < max_retries:
                wait_time = backoff_factor ** attempt
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"All {max_retries + 1} attempts failed")
                return FetchResult(success=False, error_type=error_type)
```

### Graceful Degradation

- If one statement fails, continue fetching others
- If indicators calculation fails, save statements anyway
- If database save fails, return data in memory for manual handling
- If progress tracking fails, continue operation without progress display

## Testing Strategy

### Dual Testing Approach

The system will be tested using both unit tests and property-based tests:

**Unit Tests** focus on:
- Specific error scenarios (JSON parse error, network timeout)
- Edge cases (zero denominators, None values, empty DataFrames)
- Integration points (database operations, API calls)
- Configuration and CLI argument parsing

**Property-Based Tests** focus on:
- Universal correctness properties across all inputs
- Financial calculation formulas with random valid inputs
- Success/failure determination logic with various data combinations
- Statistics aggregation with random batch results
- Validation functions with random input strings

### Property-Based Testing Configuration

- **Framework**: Hypothesis (Python)
- **Iterations**: Minimum 100 per property test
- **Test Tagging**: Each property test references its design property number

Example test structure:
```python
from hypothesis import given, strategies as st

@given(
    net_profit=st.floats(min_value=0, max_value=1e12),
    shareholders_equity=st.floats(min_value=1, max_value=1e12)
)
def test_roe_calculation_property(net_profit, shareholders_equity):
    """
    Feature: financial-data-fetcher, Property 7: ROE calculation correctness
    
    For any valid net_profit and shareholders_equity, 
    ROE should equal net_profit / shareholders_equity * 100
    """
    calculator = FinancialCalculator()
    roe = calculator.calculate_roe(net_profit, shareholders_equity)
    
    expected = (net_profit / shareholders_equity) * 100
    assert abs(roe - expected) < 0.01  # Allow small floating point error
```

### Test Coverage Goals

- Unit test coverage: >80% of code lines
- Property test coverage: All correctness properties (19 properties)
- Integration test coverage: All API endpoints and database operations
- Error path coverage: All error types and retry scenarios

### Testing Phases

1. **Development Phase**: Run unit tests on every code change
2. **Integration Phase**: Run full test suite including property tests
3. **Pre-deployment**: Run extended property tests (1000 iterations)
4. **Production Monitoring**: Health checks and error rate monitoring

## Performance Considerations

### Rate Limiting

- **Per-stock delay**: 0.5s between statements, 2s total per stock
- **Batch delay**: Additional 2s every 10 stocks
- **Estimated throughput**: ~0.4 stocks/second, ~1,400 stocks/hour
- **Full market (5,792 stocks)**: ~4 hours

### Memory Management

- Process statements one at a time, don't hold all in memory
- Use DataFrame chunking for large datasets
- Clear processed data from memory after database save
- Limit progress tracker history to last 1000 operations

### Database Optimization

- Use batch inserts where possible (INSERT OR REPLACE)
- Create indexes on (code, report_date) for fast lookups
- Use transactions for multi-statement operations
- Vacuum database periodically to reclaim space

### Scalability Considerations

- Support parallel processing (future enhancement)
- Consider distributed task queue for large-scale operations
- Implement connection pooling for database access
- Add caching layer for frequently accessed data

## Deployment and Operations

### Configuration

Configuration via environment variables or config file:

```python
# config.py
class Config:
    # Database
    DB_PATH = os.getenv('DB_PATH', 'data/a_share.db')
    
    # Rate Limiting
    PER_STOCK_DELAY = float(os.getenv('PER_STOCK_DELAY', '2.0'))
    BATCH_DELAY_INTERVAL = int(os.getenv('BATCH_DELAY_INTERVAL', '10'))
    BATCH_DELAY_SECONDS = float(os.getenv('BATCH_DELAY_SECONDS', '2.0'))
    
    # Retry
    MAX_RETRIES_NETWORK = int(os.getenv('MAX_RETRIES_NETWORK', '3'))
    MAX_RETRIES_API = int(os.getenv('MAX_RETRIES_API', '2'))
    RETRY_BACKOFF_FACTOR = float(os.getenv('RETRY_BACKOFF_FACTOR', '2.0'))
    
    # Update Strategy
    UPDATE_FREQUENCY_DAYS = int(os.getenv('UPDATE_FREQUENCY_DAYS', '7'))
    
    # Monitoring
    FAILURE_RATE_THRESHOLD = float(os.getenv('FAILURE_RATE_THRESHOLD', '0.20'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/financial_fetcher.log')
```

### Command-Line Interface

```bash
# Full market download
python tools/fetch_financial_data.py --all

# Download specific stocks
python tools/fetch_financial_data.py --codes 600519 000001 600036

# Force update (ignore existing data)
python tools/fetch_financial_data.py --all --force

# Resume from interruption
python tools/fetch_financial_data.py --all --resume-from 600100

# Retry failed stocks
python tools/fetch_financial_data.py --retry-failed failed_stocks_20260101.json

# Limit number of stocks (for testing)
python tools/fetch_financial_data.py --all --max-stocks 100
```

### Monitoring and Logging

**Log Levels:**
- DEBUG: Detailed operation traces
- INFO: Normal operations (start, progress, completion)
- WARNING: Recoverable issues (empty data, validation failures)
- ERROR: Serious issues (API errors, network failures, high failure rate)

**Key Metrics to Monitor:**
- Success rate (should be >80%)
- Average fetch time per stock
- Error type distribution
- Database growth rate
- API response times

**Health Check Endpoint:**
```python
def health_check() -> Dict:
    """Return system health status"""
    return {
        'status': 'healthy' | 'degraded' | 'unhealthy',
        'last_batch': {
            'timestamp': '2026-01-01 20:00:00',
            'total': 5792,
            'success': 4850,
            'failed': 942,
            'success_rate': 0.837
        },
        'database': {
            'total_stocks_with_data': 4850,
            'total_records': 485000,
            'last_update': '2026-01-01 20:00:00'
        }
    }
```

### Maintenance Tasks

**Daily:**
- Run incremental update for stocks needing refresh
- Check error logs for anomalies
- Verify database integrity

**Weekly:**
- Review failure patterns and adjust retry logic if needed
- Analyze performance metrics
- Update failed stock list and retry

**Monthly:**
- Full market re-download to catch any missed updates
- Database vacuum and optimization
- Review and update financial indicator calculations

### Disaster Recovery

**Backup Strategy:**
- Daily database backups before batch operations
- Keep last 7 days of backups
- Store failed stock lists for recovery

**Recovery Procedures:**
1. If database corrupted: Restore from latest backup
2. If batch interrupted: Use resume-from feature
3. If API unavailable: Wait and retry with exponential backoff
4. If high failure rate: Investigate API status, adjust rate limits

