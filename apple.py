import streamlit as st
import requests
import pandas as pd

# --- 설정 및 변수 ---
# YOUR_NICE_API_KEY 부분을 발급받은 인증키로 변경해주세요.
API_KEY = "1mp7CBP_8PXXbAzBmUiA0AkP1MdMvjkQRrAmd8V9e-2A"
NICE_API_BASE_URL = "https://open.neis.go.kr/hub/schoolInfo"

# --- Streamlit UI 구성 ---
st.set_page_config(page_title="나이스 학교 기본정보 조회", layout="centered")
st.title("🏫 나이스 학교 기본정보 조회")
st.markdown("---")

st.subheader("학교 검색")
school_name = st.text_input("검색할 학교 이름을 입력하세요:", help="예: 서울고, 한성여자고등학교")

if st.button("학교 정보 검색"):
    if not school_name:
        st.warning("학교 이름을 입력해주세요.")
    else:
        with st.spinner("학교 정보를 불러오는 중..."):
            params = {
                "KEY": API_KEY,
                "Type": "json",
                "pIndex": 1,
                "pSize": 100,  # 최대 100개까지 조회
                "SCHUL_NM": school_name,
            }

            try:
                response = requests.get(NICE_API_BASE_URL, params=params)
                data = response.json()

                # API 응답 구조 확인 및 데이터 파싱
                if "schoolInfo" in data and len(data["schoolInfo"]) > 1:
                    # 첫 번째 요소는 헤더, 두 번째 요소에 실제 데이터(row)가 있음
                    schools_data = data["schoolInfo"][1]["row"]
                    
                    if schools_data:
                        st.subheader(f"'{school_name}' 검색 결과 ({len(schools_data)}개)")
                        
                        # 필요한 컬럼만 추출하여 깔끔하게 표시
                        display_columns = [
                            "SCHUL_NM", "SCHUL_KND_SC_NM", "LCTN_SC_NM", 
                            "ORG_RDNMA", "ORG_TELNO", "HMPG_ADRES", 
                            "FOND_SC_NM", "FOND_YMD"
                        ]
                        
                        # 사용자에게 보여줄 한글 컬럼명 매핑
                        column_mapping = {
                            "SCHUL_NM": "학교명",
                            "SCHUL_KND_SC_NM": "학교종류",
                            "LCTN_SC_NM": "소재지",
                            "ORG_RDNMA": "주소",
                            "ORG_TELNO": "전화번호",
                            "HMPG_ADRES": "홈페이지",
                            "FOND_SC_NM": "설립구분",
                            "FOND_YMD": "개교기념일"
                        }
                        
                        # 데이터를 데이터프레임으로 변환하여 테이블로 보여주기
                        df = pd.DataFrame(schools_data)
                        df_display = df[display_columns].rename(columns=column_mapping)
                        
                        st.dataframe(df_display, use_container_width=True)

                        # 각 학교별 상세 정보를 expander로 제공 (선택 사항)
                        st.markdown("---")
                        st.subheader("상세 정보")
                        for i, school in enumerate(schools_data):
                            with st.expander(f"**{school.get('SCHUL_NM', '학교명 없음')}**"):
                                st.write(f"**학교 종류:** {school.get('SCHUL_KND_SC_NM', '정보 없음')}")
                                st.write(f"**소재지 교육청:** {school.get('ATPT_OFCDC_SC_NM', '정보 없음')}")
                                st.write(f"**소재지:** {school.get('LCTN_SC_NM', '정보 없음')}")
                                st.write(f"**도로명주소:** {school.get('ORG_RDNMA', '정보 없음')}")
                                st.write(f"**지번주소:** {school.get('ORG_RDNMZ', '정보 없음')}")
                                st.write(f"**전화번호:** {school.get('ORG_TELNO', '정보 없음')}")
                                st.write(f"**팩스번호:** {school.get('ORG_FAXNO', '정보 없음')}")
                                st.write(f"**홈페이지:** [{school.get('HMPG_ADRES', '정보 없음')}]({school.get('HMPG_ADRES', '#')})")
                                st.write(f"**남녀공학 구분:** {school.get('COEDU_SC_NM', '정보 없음')}")
                                st.write(f"**설립구분:** {school.get('FOND_SC_NM', '정보 없음')}")
                                st.write(f"**개교기념일:** {school.get('FOND_YMD', '정보 없음')}")
                                st.write(f"**설립인가일:** {school.get('DDDEP_YMD', '정보 없음')}")
                                # 추가 정보 필요시 여기에 더 많은 필드를 추가하세요
                    else:
                        st.info("검색된 학교 정보가 없습니다.")
                elif "RESULT" in data:
                    # API 오류 응답 처리
                    error_code = data["RESULT"]["CODE"]
                    error_message = data["RESULT"]["MESSAGE"]
                    st.error(f"API 호출 중 오류 발생: {error_message} (코드: {error_code})")
                    if error_code == "INFO-100":
                        st.warning("발급받은 인증키가 올바르지 않거나, 호출 권한이 없습니다. 키를 확인해주세요.")
                    elif error_code == "INFO-200":
                        st.warning("필수 파라미터가 누락되었거나 형식이 올바르지 않습니다.")
                    elif error_code == "INFO-300":
                        st.warning("데이터가 존재하지 않습니다. 학교 이름을 다시 확인해주세요.")
                else:
                    st.error("알 수 없는 API 응답 형식입니다.")

            except requests.exceptions.RequestException as e:
                st.error(f"네트워크 오류가 발생했습니다: {e}")
                st.info("인터넷 연결 상태를 확인하거나, 잠시 후 다시 시도해주세요.")
            except Exception as e:
                st.error(f"데이터 처리 중 예상치 못한 오류가 발생했습니다: {e}")
