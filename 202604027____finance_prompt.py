# finance_prompts.py — 你的第一个作品


import os
from openai import OpenAI
# from google.colab import userdata  # 如果在Colab中



def get_report_summary_prompt():
    return {
        "system": """你是风控合规专员。
        从公告文本中识别：股权质押/减持/诉讼/监管函/业绩预警等风险事件，
        按严重程度排序。""",
        "template": "以下是研报：\n{text}\n请输出分析。",
        "temperature": 0.3
    }

def get_financial_extract_prompt():
    return {
        "system": """你是财务分析师。
        提取营收/净利润/毛利率/同比增速。
        数字带单位，无法确认标[待核实]。
        输出 JSON""",
        "template": "财报内容：\n{text}\n请提取关键财务数据。",
        "temperature": 0.1
    }

def call_api(client, prompt_config, text):
    p = prompt_config
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role":"system", "content": p["system"]},
            {"role":"user",   "content": p["template"].format(text=text)}
        ],
        temperature=p["temperature"]
    )
    return resp.choices[0].message.content



# 2. 初始化客户端（替换为你的API密钥）
client = OpenAI(
    api_key="sk-your-deepseek-api-key",  # 替换为你的真实API密钥
    base_url="https://api.deepseek.com"
)

# 3. 示例文本
announcement_text = """
公司公告：控股股东计划减持不超过2%股份
减持原因：个人资金需求
减持期间：2024年1月20日至2024年4月20日
"""

financial_text = """
2023年Q3财报：
营业收入：85.6亿元，同比增长25.3%
净利润：12.4亿元，同比增长18.7%
毛利率：32.5%
"""

# 4. 调用示例1：风控分析
print("=== 风控分析 ===")
risk_config = get_report_summary_prompt()
risk_result = call_api(client, risk_config, announcement_text)
print(risk_result)

# 5. 调用示例2：财务数据提取
print("\n=== 财务数据提取 ===")
finance_config = get_financial_extract_prompt()
finance_result = call_api(client, finance_config, financial_text)
print(finance_result)



# 扩展1：添加市场情绪分析
def get_market_sentiment_prompt():
    return {
        "system": """你是资深市场分析师。分析新闻文本中的市场情绪，判断对相关股票的影响。""",
        "template": "新闻内容：\n{text}\n\n请分析：\n1. 情绪倾向（正面/中性/负面）\n2. 影响程度（高/中/低）\n3. 可能影响的股票板块\n4. 投资建议",
        "temperature": 0.5
    }

# 扩展2：添加批量处理功能
def batch_analyze_documents(client, documents, analysis_type="risk"):
    """
    批量分析多个文档
    
    documents: 文档列表，每个元素是文本字符串
    analysis_type: "risk" 或 "finance"
    """
    results = []
    
    if analysis_type == "risk":
        config = get_report_summary_prompt()
    elif analysis_type == "finance":
        config = get_financial_extract_prompt()
    else:
        raise ValueError("不支持的analysis_type")
    
    for i, text in enumerate(documents, 1):
        print(f"正在分析第{i}/{len(documents)}个文档...")
        result = call_api(client, config, text)
        results.append({
            "doc_index": i,
            "content": result
        })
    
    return results

# 使用批量处理
documents = [financial_text, announcement_text]  # 你的文档列表
batch_results = batch_analyze_documents(client, documents, "risk")