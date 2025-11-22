import os
import json
from openai import OpenAI

# 🔑 여기에 API Key를 입력하세요
API_KEY = "sk-proj-..." 

client = OpenAI(api_key=API_KEY)
MODEL_NAME = "gpt-4o"

def get_categorized_transactions(transactions):
    """
    [Step 1] AI를 사용하여 거래 내역에 카테고리 태그를 붙입니다.
    """
    prompt = f"""
    당신은 금융 데이터 분류 전문가입니다.
    아래 제공된 거래 내역(`transactions`)의 `printed_content`(적요)를 분석하여 
    가장 적절한 `category`를 할당하세요.
    
    [분류 카테고리 기준]:
    - 식비: 식당, 카페, 배달, 주점, 베이커리
    - 교통: 지하철, 택시, 버스, 기차, 주유, 하이패스
    - 쇼핑: 의류, 쿠팡, 백화점, 잡화, 미용실
    - 의료/건강: 병원, 약국, 한의원, 헬스장, 피트니스, 요가, 필라테스, 영양제
    - 문화/여가: 영화, OTT구독, 게임, 여행, 숙박, PC방
    - 공과금/고정비: 월세, 관리비, 통신비, 보험료, 정기결제
    - 이체: 친구송금, 회비, 적금, 부모님용돈, 계좌이체
    - 편의점/마트: 편의점, 대형마트, 슈퍼마켓, 식자재
    - 기타: 위 분류에 속하지 않는 것

    [입력 데이터]:
    {json.dumps(transactions, ensure_ascii=False)}

    [출력 형식]:
    반드시 아래와 같은 JSON 구조로 출력하세요. 다른 설명은 생략합니다.
    {{
        "transactions": [
            {{ "date": "...", "printed_content": "...", "amount": 1000, "category": "식비" }},
            ...
        ]
    }}
    """

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a precise data classifier. Output valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )

    result_json = json.loads(response.choices[0].message.content)
    
    if "transactions" in result_json:
        return result_json["transactions"]
    elif isinstance(result_json, list):
        return result_json
    else:
        return transactions

def calculate_statistics(categorized_transactions):
    """
    [Step 2] 분류된 데이터를 바탕으로 총액과 카테고리별 비율을 Python으로 정확히 계산합니다.
    """    
    total_expenditure = 0
    category_sums = {}

    for item in categorized_transactions:
        amount = item.get('amount', 0)
        category = item.get('category', '기타')
        
        total_expenditure += amount
        category_sums[category] = category_sums.get(category, 0) + amount

    statistics = []
    for cat, amt in category_sums.items():
        percentage = (amt / total_expenditure * 100) if total_expenditure > 0 else 0
        statistics.append({
            "category": cat,
            "total_amount": amt,
            "percentage": f"{percentage:.1f}%"
        })
    
    statistics.sort(key=lambda x: x['total_amount'], reverse=True)

    return {
        "summary": {
            "total_expenditure": total_expenditure,
            "category_breakdown": statistics
        },
        "details": categorized_transactions
    }

if __name__ == "__main__":
    raw_data = [
        {"date": "20251101", "printed_content": "스타벅스", "amount": 5000},      # 식비
        {"date": "20251102", "printed_content": "카카오택시", "amount": 12000},    # 교통
        {"date": "20251105", "printed_content": "온누리약국", "amount": 8500},     # 의료/건강
        {"date": "20251106", "printed_content": "스포애니헬스", "amount": 40000},   # 의료/건강 (피트니스)
        {"date": "20251108", "printed_content": "김철수송금", "amount": 50000},    # 이체
        {"date": "20251110", "printed_content": "넷플릭스", "amount": 13500}       # 문화/여가
    ]
    
    categorized_list = get_categorized_transactions(raw_data)
    final_result = calculate_statistics(categorized_list)

    print("\n✅ 최종 처리 결과 (JSON):")
    print(json.dumps(final_result, indent=2, ensure_ascii=False))
