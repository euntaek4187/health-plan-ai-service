import streamlit as st
import boto3
import json


session = boto3.Session()

bedrock = session.client(
    service_name='bedrock-runtime',
    region_name='us-east-1',
    endpoint_url="https://bedrock-runtime.us-east-1.amazonaws.com"
)

# BMI 계산 함수
def calculate_bmi(height, weight):
    return weight / ((height / 100) ** 2)

# 건강 상태 평가 함수
def evaluate_health(bmi):
    if bmi < 18.5:
        return "저체중입니다. 영양 섭취가 필요합니다."
    elif bmi < 25:
        return "정상 체중입니다. 현재 상태를 유지하세요."
    elif bmi < 30:
        return "과체중입니다. 운동과 균형 잡힌 식단이 필요합니다."
    else:
        return "비만입니다. 운동과 근력 증진이 필요합니다."

# ask_claude 함수 정의
def ask_claude(prompt):
    body = json.dumps({
        "prompt": "\n\nHuman: " + prompt + "\n\nAssistant:",
        "max_tokens_to_sample": 2000,
        "temperature": 0.1,
        "top_p": 0.9,
    })

    modelId = 'anthropic.claude-v2'
    accept = 'application/json'
    contentType = 'application/json'

    response = bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
    response_body = json.loads(response.get('body').read())

    return response_body.get('completion')
# 메인 함수

def main():
    st.set_page_config(page_title="건강 관리 AI 서비스")
    st.title("🏥 건강 관리 AI 서비스")

    with st.form("user_input_form"):
        height = st.number_input("키(cm)", min_value=100, max_value=250)
        weight = st.number_input("몸무게(kg)", min_value=30, max_value=200)
        gender = st.selectbox("성별", ["남성", "여성"])
        job = st.text_input("직업")
        goal = st.selectbox("목표", ["다이어트", "근력증진", "건강관리"])
        submit_button = st.form_submit_button(label='결과 보기')

    if submit_button:
        bmi = calculate_bmi(height, weight)
        health_status = evaluate_health(bmi)
        st.success(f"BMI는 {bmi:.2f}입니다. {health_status}")

        # AI를 사용하여 운동 및 식단 계획 생성
        exercise_nutrition_prompt = f'''
        다음 정보를 바탕으로 사용자에게 맞춤형 운동 및 식단 계획을 제안해주세요:
        - 키: {height}cm
        - 몸무게: {weight}kg
        - 성별: {gender}
        - 직업: {job}
        - 목표: {goal}
        - BMI: {bmi:.2f}
        - 건강 상태: {health_status}
        '''

        # AI 응답 출력
        ai_response = ask_claude(exercise_nutrition_prompt)
        
        # 결과물 디자인
        st.markdown("## 📋 맞춤형 운동 및 식단 계획")
        st.markdown(ai_response, unsafe_allow_html=True)


if __name__ == '__main__':
    main()

