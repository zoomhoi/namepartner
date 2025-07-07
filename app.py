import streamlit as st
import openai

# 스트리밋 시크릿에서 API 키 읽기
api_key = st.secrets["api"]["OPENAI_API_KEY"]

if not api_key:
    st.error("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
    st.write("참고: Streamlit 대시보드에서 Secrets를 설정해야 합니다.")
    st.stop()

openai.api_key = api_key
st.write("API 키가 성공적으로 로드되었습니다.")  # 디버깅용 출력

# 자모 획수표
JAEMO_STROKES = {
    'ㄱ':2,'ㄲ':4,'ㄴ':2,'ㄷ':3,'ㄸ':6,'ㄹ':5,'ㅁ':4,'ㅂ':4,'ㅃ':8,
    'ㅅ':2,'ㅆ':4,'ㅇ':1,'ㅈ':3,'ㅉ':6,'ㅊ':4,'ㅋ':3,'ㅌ':4,'ㅍ':4,'ㅎ':3,
    'ㅏ':2,'ㅐ':3,'ㅑ':3,'ㅒ':4,'ㅓ':2,'ㅔ':3,'ㅕ':3,'ㅖ':4,'ㅗ':2,'ㅘ':4,
    'ㅙ':5,'ㅚ':3,'ㅛ':3,'ㅜ':2,'ㅝ':4,'ㅞ':5,'ㅟ':3,'ㅠ':3,'ㅡ':1,'ㅢ':2,'ㅣ':1
}

INITIAL_COMPAT = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
MEDIAL_COMPAT  = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
FINAL_COMPAT   = ['','ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

def get_syllable_stroke(char):
    code = ord(char) - 0xAC00
    if code < 0 or code > 11171:
        return 0
    cho, rem = divmod(code, 588)
    jung, jong = divmod(rem, 28)
    total = JAEMO_STROKES[INITIAL_COMPAT[cho]] + JAEMO_STROKES[MEDIAL_COMPAT[jung]]
    for c in FINAL_COMPAT[jong]:
        total += JAEMO_STROKES.get(c, 0)
    return total

def calculate_love_score(name1, name2):
    strokes = [get_syllable_stroke(s) for s in list(name1 + name2) if '\uac00' <= s <= '\ud7a3']
    if not strokes:
        return 0
    while len(strokes) > 2:
        strokes = [(strokes[i] + strokes[i+1]) % 100 for i in range(len(strokes)-1)]
    if len(strokes) == 2:
        return (strokes[0] % 10) * 10 + (strokes[1] % 10)
    elif len(strokes) == 1:
        return strokes[0] % 100
    return 0

# Streamlit UI
st.title("💖 이름 궁합점 테스트 (남자 연예인 ver.)")

user_name = st.text_input("당신의 이름을 입력하세요").strip()
celeb_name = st.text_input("남자 연예인 이름을 입력하세요").strip()

if st.button("궁합점 보기"):
    if not user_name or not celeb_name:
        st.warning("이름을 모두 입력해주세요.")
    elif not all('\uac00' <= ch <= '\ud7a3' for ch in user_name + celeb_name):
        st.warning("이름은 한글로만 입력해주세요.")
    else:
        score = calculate_love_score(user_name, celeb_name)
        st.subheader(f"궁합점수: {score}%")

        if score >= 50:
            st.success(f"{celeb_name}님이 꽃을 들고 {user_name}님께 프로포즈합니다! 💐")
            st.info("참고: AI는 실제 연예인 이미지를 생성할 수 없으므로, 가상의 잘생긴 한국 연예인 이미지를 보여드립니다.")
            with st.spinner("이미지 생성 중..."):
                try:
                    img_resp = openai.images.generate(
                        model="dall-e-3",
                        prompt=f"A handsome Korean male celebrity resembling {celeb_name}, holding a bouquet of roses, proposing romantically in a cinematic setting, ultra-realistic, high quality",
                        n=1,
                        size="1024x1024"
                    )
                    st.image(img_resp.data[0].url, caption=f"{celeb_name}을(를) 닮은 가상 연예인의 프로포즈 장면")
                    st.write("디버깅: 프로포즈 이미지 생성 완료")  # 디버깅용
                except openai.OpenAIError as e:
                    st.error(f"이미지 생성 중 에러: {e}")
                    st.write("디버깅: 프로포즈 이미지 생성 실패")
        else:
            st.error("아쉽게도 궁합점수가 낮아요.")
            st.write("다른 분들을 보시는 건 어떨까요?")
            st.info("힘내세요! 더 좋은 인연이 기다리고 있을 거예요. 😊")
