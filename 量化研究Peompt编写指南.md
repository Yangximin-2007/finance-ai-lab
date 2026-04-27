### 首先，完整的工作流程为：
用户输入策略描述
    ↓
SYSTEM PROMPT设定AI为量化研究员
    ↓
USER PROMPT包装策略描述+具体要求
    ↓
AI生成结构化输出
    ↓
解析并展示结果

### 其次，给出一个实例代码：
import openai

def quant_research_assistant(strategy_text, model="gpt-4"):
    """量化研究助手主函数"""
    
    system_prompt = """你是量化研究员..."""  # 上面定义的系统prompt
    
    user_prompt = f"""
策略描述：{strategy_text}

请输出：
1. 因子逻辑（具体到公式）
2. Python代码框架
3. 回测注意事项
"""
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,  # 较低温度，保证输出稳定性
        max_tokens=1500
    )
    
    return response.choices[0].message.content

# 使用示例
strategy = "基于北向资金流向的择时策略：当北向资金连续3日净流入时买入，连续3日净流出时卖出"
result = quant_research_assistant(strategy)
print(result)



### 紧接着，有细节讲解：

系统架构：
├── 量化思路生成
│   ├── 输入：策略描述
│   └── 输出：因子逻辑 + 代码框架
│
└── 风控提示
    ├── 输入：公告文本
    └── 输出：风险事件识别

system_prompt = """
你是专业的量化研究员，擅长将投资策略转化为可回测的量化因子。

你的任务：
1. 理解用户描述的投资策略逻辑
2. 拆解策略核心思想，转化为具体的因子逻辑
3. 设计可实现的Python代码框架
4. 考虑实际回测中的技术细节

请确保你的输出：
- 因子逻辑清晰、可量化
- 代码框架完整、可直接扩展
- 考虑数据来源、计算频率、参数设置
- 注明关键假设和潜在问题

输出格式要求：
请按照以下结构输出：
【因子逻辑】
1. 核心思想：
2. 计算方法：
3. 数据需求：
4. 参数说明：

【代码框架】
1. 数据准备模块：
2. 因子计算模块：
3. 回测接口模块：
4. 注意事项：

"""

# 基本模板
user_prompt_template = """
策略描述：{strategy_text}

请根据以上策略描述，完成以下任务：
1. 拆解出可用于回测的因子逻辑
2. 给出Python伪代码框架
3. 注明数据源和计算频率
4. 指出可能的实现难点

"""


### 完整实例：动量反转策略
# ==================== SYSTEM PROMPT ====================
system_prompt = """你是顶尖对冲基金的量化研究员，拥有10年A股因子开发经验。

你的核心能力：
- 将主观投资逻辑转化为数学公式
- 设计高效、稳健的因子计算框架
- 识别策略的过拟合风险和数据挖掘偏差

任务要求：
1. 深度理解策略的经济学逻辑
2. 设计至少3个备选因子计算方法
3. 考虑A股市场的特殊性（T+1、涨跌停、停牌等）
4. 给出完整的Python实现路径

输出结构：
【策略拆解】
- 经济学逻辑：
- 市场有效性假设：
- 预期收益来源：

【因子设计】
- 因子1（基础版）：
- 因子2（稳健版）：
- 因子3（优化版）：

【代码框架】
- 数据层：
- 计算层：
- 验证层：

【风险提示】
- 过拟合风险：
- 交易成本：
- 市场环境依赖："""

# ==================== USER PROMPT ====================
strategy_text = """
策略描述：动量反转策略
核心思想：过去一段时间表现较差的股票，在未来一段时间有反转上涨的趋势。
具体逻辑：选取过去20个交易日跌幅最大的10%的股票，等权重买入，持有5个交易日卖出。
选股范围：沪深300成分股
调仓频率：每周一开盘调仓
"""

user_prompt = f"""
策略描述：{strategy_text}

请按以下要求输出：
1. 因子逻辑要具体到数学公式
2. 代码框架要包含完整的pandas计算流程
3. 特别注意A股的涨跌停、停牌处理
4. 给出可运行的伪代码示例
"""

## 预期输出实例：
【策略拆解】
- 经济学逻辑：行为金融学中的过度反应假设，投资者对坏消息反应过度导致股价超跌，随后均值回归
- 市场有效性假设：弱式有效市场，历史价格信息可预测未来短期走势
- 预期收益来源：市场错误定价的修正收益

【因子设计】
因子1（基础版）：过去20日收益率排名因子
  formula: rank(-1 * (close_today / close_20d_ago - 1))
  选择：排名后10%的股票

因子2（稳健版）：标准化20日收益率 + 流动性筛选
  formula: (return_20d - mean_return) / std_return
  筛选：日均成交额 > 1亿元
  选择：Z-score < -1.5的股票

因子3（优化版）：残差动量（剔除行业和市值影响）
  steps:
    1. 回归：return_20d = α + β1*industry_return + β2*log(market_cap) + ε
    2. 取残差ε作为因子
    3. 选择残差最小的10%股票

【代码框架】
# 数据层
def load_data():
    - 日行情数据：开盘价、收盘价、成交额
    - 股票基本信息：行业分类、市值
    - 特殊数据：涨跌停状态、停牌日期

# 计算层
def calculate_factor(df, lookback=20):
    - 计算每只股票过去20日收益率
    - 处理缺失值（停牌期间）
    - 排除ST、退市风险股票
    - 按行业和市值做中性化处理（因子3）
    - 计算排名/百分位

# 回测接口
class ReversalStrategy:
    def __init__(self):
        self.holding_period = 5
        self.top_pct = 0.1
        
    def generate_signals(self, factor_values):
        - 每周一计算因子
        - 选择因子值最低的10%股票
        - 等权重分配资金
        - 记录调仓日期和权重

【风险提示】
1. 过拟合风险：20天/5天参数可能只是历史数据巧合
2. 交易成本：高频调仓导致佣金和滑点较高，回测需考虑
3. 市场环境依赖：反转效应在牛市中较弱，熊市中较强
4. 流动性风险：跌幅大的股票可能流动性差，实际成交困难


### 更复杂的例子：多因子策略
strategy_text = """
复合多因子策略
1. 质量因子：高ROE、高盈利增长、低负债率
2. 价值因子：低市盈率、低市净率、高股息率
3. 动量因子：过去6个月收益率（排除最近1个月）

组合方法：
- 每个因子独立排序，转换为十分位（1-10分）
- 质量因子权重40%，价值因子30%，动量因子30%
- 总分 = 质量分*0.4 + 价值分*0.3 + 动量分*0.3
- 选择总分最高的20只股票，月度调仓
- 行业中性化：每个行业不超过30%权重
"""

user_prompt = f"""
策略描述：{strategy_text}

请特别注意：
1. 每个因子的具体计算方法
2. 因子标准化和去极值处理
3. 行业中性化的实现方法
4. 月度再平衡的具体操作
5. 给出完整的pandas代码框架
"""

## 预期输出（简化版）：
【因子逻辑】
1. 质量因子计算：
   - ROE = 净利润 / 净资产 (TTM)
   - 盈利增长 = (本期净利润 - 上期净利润) / abs(上期净利润)
   - 负债率 = 总负债 / 总资产
   - 综合质量分 = 0.5*ROE_z + 0.3*盈利增长_z + 0.2*(1-负债率_z)

2. 价值因子计算：
   - PE = 市值 / 净利润 (剔除负值和极端值)
   - PB = 市值 / 净资产
   - 股息率 = 每股股息 / 股价
   - 综合价值分 = 0.4*PE_inv_z + 0.4*PB_inv_z + 0.2*股息率_z

3. 动量因子计算：
   - 过去6个月收益 = close_t / close_6m_ago - 1
   - 过去1个月收益 = close_t / close_1m_ago - 1
   - 动量因子 = 过去6个月收益 - 过去1个月收益 (排除近期反转)

【代码框架】
import pandas as pd
import numpy as np

class MultiFactorStrategy:
    def __init__(self):
        self.factor_weights = {'quality': 0.4, 'value': 0.3, 'momentum': 0.3}
        
    def calculate_factors(self, data):
        # 质量因子
        data['roe'] = data['net_profit'] / data['equity']
        data['profit_growth'] = data['net_profit'].pct_change(periods=4)  # 季度同比
        data['debt_ratio'] = data['total_debt'] / data['total_assets']
        
        # 价值因子
        data['pe'] = data['market_cap'] / data['net_profit']
        data['pb'] = data['market_cap'] / data['book_value']
        data['dividend_yield'] = data['dividend_per_share'] / data['close']
        
        # 动量因子
        data['return_6m'] = data['close'] / data['close'].shift(126) - 1
        data['return_1m'] = data['close'] / data['close'].shift(21) - 1
        data['momentum'] = data['return_6m'] - data['return_1m']
        
        return data
    
    def normalize_factors(self, data):
        # 去极值：MAD方法
        for factor in ['roe', 'pe', 'momentum']:
            median = data[factor].median()
            mad = (data[factor] - median).abs().median()
            data[f'{factor}_norm'] = data[factor].clip(
                median - 5*mad, median + 5*mad
            )
            
        # 标准化：Z-score
        for factor in ['roe_norm', 'pe_norm', 'momentum_norm']:
            mean = data[factor].mean()
            std = data[factor].std()
            data[f'{factor}_z'] = (data[factor] - mean) / std
            
        return data
    
    def combine_factors(self, data):
        # 计算综合分
        data['quality_score'] = 0.5*data['roe_norm_z'] + 0.3*data['profit_growth'] + 0.2*data['debt_ratio_norm_z']
        data['value_score'] = -0.4*data['pe_norm_z'] - 0.4*data['pb_norm_z'] + 0.2*data['dividend_yield_norm_z']
        data['momentum_score'] = data['momentum_norm_z']
        
        # 行业中性化
        data['quality_score_neutral'] = data.groupby('industry')['quality_score'].apply(
            lambda x: x - x.mean()
        )
        # 同样处理其他因子...
        
        # 加权总分
        data['total_score'] = (
            data['quality_score_neutral'] * 0.4 +
            data['value_score_neutral'] * 0.3 +
            data['momentum_score_neutral'] * 0.3
        )
        
        return data
    
    def generate_portfolio(self, data, date):
        # 每月初选股
        date_data = data[data['date'] == date]
        
        # 按总分排序
        date_data = date_data.sort_values('total_score', ascending=False)
        
        # 行业约束
        selected = []
        industry_count = {}
        for _, stock in date_data.iterrows():
            industry = stock['industry']
            if industry_count.get(industry, 0) < len(date_data) * 0.3:
                selected.append(stock['code'])
                industry_count[industry] = industry_count.get(industry, 0) + 1
                
            if len(selected) >= 20:
                break
                
        return selected


### 高级技巧：增加风控模块
system_prompt_enhanced = """
你是一个量化投研AI助手，包含两个核心功能：

功能一：量化思路生成
- 输入：策略描述文本
- 输出：因子逻辑 + 代码框架
- 要求：逻辑严谨、代码可实施

功能二：风控提示
- 输入：公司公告文本
- 输出：潜在风险事件识别
- 要求：识别财务风险、法律风险、经营风险

请根据用户输入判断需要使用哪个功能，并相应调整回答方式。

如果用户输入以"策略描述："开头，执行功能一。
如果用户输入以"公告："开头，执行功能二。

功能一的输出格式：
【因子逻辑】
...
【代码框架】
...

功能二的输出格式：
【风险事件识别】
1. 财务风险：
2. 法律风险：
3. 经营风险：
4. 建议措施：
"""

# 用户输入示例1（量化思路）
user_prompt_quant = """
策略描述：基于分析师预期修正的策略
逻辑：寻找最近30天内被分析师上调盈利预测的股票，选择上调幅度最大的20只
调仓：月度调仓
"""

# 用户输入示例2（风控提示）
user_prompt_risk = """
公告：XX科技股份有限公司关于收到证监会立案调查通知书的公告
公司于今日收到中国证监会《立案调查通知书》，因公司涉嫌信息披露违法违规，证监会决定对公司立案调查。
公司将积极配合证监会的调查工作，并严格按照监管要求履行信息披露义务。
"""
