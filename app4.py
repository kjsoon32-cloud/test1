"""
Step 2 – GPT API 기반 서술형 채점 + 피드백 (점수 미사용)
───────────────────────────────────────────────
• 기존 Step 1‑2 코드 하단에 그대로 이어 붙이면 됩니다. (별도 파일로도 사용 가능)
• 교사는 GRADING_GUIDELINES 사전에 문항별 ‘채점 기준’을 자유롭게 입력하세요.
• 피드백은 ‘정답/오답 + 200자 이내 설명’ 형식으로 반환됩니다.
• 비용 절감을 위해 temperature=0, max_tokens≈250(≈200자) 사용.
"""

import streamlit as st

# ── 1. 수업 제목 ──
st.title("엘니뇨와 라니냐")  # ← 교과별 제목으로 자유롭게 수정하세요.

# ── 2. 학번 입력 ──
student_id = st.text_input("학번", help="학생의 학번을 작성하세요. (예: 10130)")

# ── 3‑1. 서술형 문제 1 표시 ──
QUESTION_1 = """
엘니뇨 발생시 페루 연안의 수온과 해면기압은 평상시에 비해 어떻게 변하는지 서술하시오.
"""  # ← 교사가 원하는 서술형 문제로 변경
st.markdown("#### 서술형 문제 1")
st.write(QUESTION_1)
answer_1 = st.text_area("답안을 입력하세요", key="answer1", height=150)

# ── 3‑2. 서술형 문제 2 표시 ──
QUESTION_2 = """
라니냐 발생시 적도 해류의 속도 변화를 설명하시오.
"""
st.markdown("#### 서술형 문제 2")
st.write(QUESTION_2)
answer_2 = st.text_area("답안을 입력하세요", key="answer2", height=150)

# ── 3‑3. 서술형 문제 3 표시 ──
QUESTION_3 = """
남방진동의 개념을 설명하시오.
"""
st.markdown("#### 서술형 문제 3")
st.write(QUESTION_3)
answer_3 = st.text_area("답안을 입력하세요", key="answer3", height=150)

# 답안을 리스트로 모아 이후 채점 로직에서 재사용하기
answers = [answer_1, answer_2, answer_3]

# ── 4. 전체 제출 버튼 ──
if st.button("제출"):
    if not student_id.strip():
        st.warning("학번을 입력하세요.")
    elif any(ans.strip() == "" for ans in answers):
        st.warning("모든 답안을 작성하세요.")
    else:
        st.success(f"제출 완료! 학번: {student_id}")
        # ⚠️ Step 2에서 GPT 채점 및 DB 저장 로직을 여기에 추가할 예정입니다.
        
from openai import OpenAI, OpenAIError

# ── 0. OpenAI 클라이언트 ──
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("⚠️ secrets.toml 에 OPENAI_API_KEY 를 설정하세요.")
    st.stop()

# ── 1. 문항별 채점 기준 (교사가 수정) ──
GRADING_GUIDELINES = {
    1: "무역풍 약화로 적도 해류의 속도가 감소하면 평상시에 비해 페루 연안의 수온은 올라간다. 따라서 해면 기압은 낮아진다.",
    2: "라니냐는 무역풍의 강화를 원인으로 본다. 따라서 적도 해류가 강해진다.",
    3: "적도 태평양의 다윈과 타히티의 해면기압의 주기적 변동을 의미한다. 남방진동 지수에 (+)이면 엘니뇨, (-)이면 라니냐를 의미한다."
}

# ── 2. 제출 버튼 (Step 1‑2의 버튼을 대체/호출) ──
if st.button("GPT 피드백 확인"):

    # answers 리스트는 Step 1‑2 코드에서 정의됨
    try:
        answers
    except NameError:
        st.error("answers 리스트가 정의되지 않았습니다. Step 1‑2 코드와 함께 실행하세요.")
        st.stop()

    feedbacks = []
    for idx, ans in enumerate(answers, start=1):
        # 빈 답안 처리
        if ans.strip() == "":
            feedbacks.append("X: 답안이 제출되지 않았습니다.")
            continue
        criterion = GRADING_GUIDELINES.get(idx, "채점 기준이 없습니다.")

        # 프롬프트 구성
        prompt = (
            f"문항 번호: {idx}\n"
            f"채점 기준: {criterion}\n"
            f"학생 답안: {ans}\n"
            "요구사항: 1) 정답 여부(O/X) 한 글자, 2) 200자 이내 구체적 피드백.\n"
            "형식 예시 → O: (피드백)"
        )

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",            # 필요 시 모델 변경
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=250,
            )
            feedback_text = response.choices[0].message.content.strip()
        except OpenAIError as e:
            feedback_text = f"API 오류: {e}"

        feedbacks.append(feedback_text)

    # ── 3. 결과 표시 ──
    for i, fb in enumerate(feedbacks, start=1):
        st.markdown(f"##### ▶ 서술형 문제 {i} 피드백")
        st.write(fb)

    st.success("모든 피드백이 생성되었습니다. 교사 확인 후 학생에게 전달하세요.")
