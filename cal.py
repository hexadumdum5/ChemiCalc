import streamlit as st
import re

# 118개 원소 원자량 데이터 (생략 없이 그대로 사용)
ATOMIC_WEIGHTS = {
    'H': 1.008, 'He': 4.0026, 'Li': 6.94, 'Be': 9.0122, 'B': 10.81, 'C': 12.011, 'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180,
    'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.085, 'P': 30.974, 'S': 32.06, 'Cl': 35.45, 'Ar': 39.95, 'K': 39.098, 'Ca': 40.078,
    'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38,
    'Ga': 69.723, 'Ge': 72.630, 'As': 74.922, 'Se': 78.971, 'Br': 79.904, 'Kr': 83.798, 'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224,
    'Nb': 92.906, 'Mo': 95.95, 'Tc': 98.0, 'Ru': 101.07, 'Rh': 102.91, 'Pd': 106.42, 'Ag': 107.87, 'Cd': 112.41, 'In': 114.82, 'Sn': 118.71,
    'Sb': 121.76, 'Te': 127.60, 'I': 126.90, 'Xe': 131.29, 'Cs': 132.91, 'Ba': 137.33, 'La': 138.91, 'Ce': 140.12, 'Pr': 140.91, 'Nd': 144.24,
    'Pm': 145.0, 'Sm': 150.36, 'Eu': 151.96, 'Gd': 157.25, 'Tb': 158.93, 'Dy': 162.50, 'Ho': 164.93, 'Er': 167.26, 'Tm': 168.93, 'Yb': 173.05,
    'Lu': 174.97, 'Hf': 178.49, 'Ta': 180.95, 'W': 183.84, 'Re': 186.21, 'Os': 190.23, 'Ir': 192.22, 'Pt': 195.08, 'Au': 196.97, 'Hg': 200.59,
    'Tl': 204.38, 'Pb': 207.2, 'Bi': 208.98, 'Po': 209.0, 'At': 210.0, 'Rn': 222.0, 'Fr': 223.0, 'Ra': 226.0, 'Ac': 227.0, 'Th': 232.04,
    'Pa': 231.04, 'U': 238.03, 'Np': 237.0, 'Pu': 244.0, 'Am': 243.0, 'Cm': 247.0, 'Bk': 247.0, 'Cf': 251.0, 'Es': 252.0, 'Fm': 257.0,
    'Md': 258.0, 'No': 259.0, 'Lr': 266.0, 'Rf': 267.0, 'Db': 268.0, 'Sg': 269.0, 'Bh': 270.0, 'Hs': 269.0, 'Mt': 278.0, 'Ds': 281.0,
    'Rg': 282.0, 'Cn': 285.0, 'Nh': 286.0, 'Fl': 289.0, 'Mc': 290.0, 'Lv': 293.0, 'Ts': 294.0, 'Og': 294.0
}

def parse_formula(formula):
    """화학식을 파싱하여 딕셔너리로 반환 (예: 'Nd2O3' -> {'Nd': 2, 'O': 3})"""
    if not formula:
        return {}
    matches = re.findall(r'([A-Z][a-z]*)(\d*)', formula)
    elements = {}
    for el, count in matches:
        if el not in ATOMIC_WEIGHTS:
            raise ValueError(f"주기율표에 없는 기호: {el}")
        count = int(count) if count else 1
        elements[el] = elements.get(el, 0) + count
    return elements

def calculate_mw(elements_dict):
    """파싱된 딕셔너리로 분자량 계산"""
    return sum(ATOMIC_WEIGHTS[el] * count for el, count in elements_dict.items())

def find_stoichiometric_ratio(react_dict, prod_dict):
    """두 화학식의 공통 원소를 기반으로 반응비를 자동 계산"""
    common_elements = set(react_dict.keys()) & set(prod_dict.keys())
    
    if not common_elements:
        return 1.0, None # 공통 원소가 없으면 1:1로 가정
        
    # 핵심 원소 찾기 (수소, 산소, 탄소 등 흔한 원소보다 금속/무거운 원소를 우선 기준점으로 삼음)
    target_element = None
    for el in common_elements:
        if el not in ['H', 'O', 'C', 'N']:
            target_element = el
            break
            
    # 흔한 원소밖에 없다면 탄소 -> 산소 -> 수소 순으로 기준점 설정
    if not target_element:
        if 'C' in common_elements: target_element = 'C'
        elif 'O' in common_elements: target_element = 'O'
        elif 'H' in common_elements: target_element = 'H'
        else: target_element = list(common_elements)[0]
        
    # 반응비 계산: (출발 물질의 기준 원소 개수) / (생성물의 기준 원소 개수)
    # 예: Nd2O3 (Nd 2개) -> NdF3 (Nd 1개) => 2 / 1 = 2
    ratio = react_dict[target_element] / prod_dict[target_element]
    return ratio, target_element

# --- UI 레이아웃 설정 ---
st.set_page_config(page_title="스마트 수율 계산기", page_icon="💡", layout="centered")

st.title("💡 스마트 화합물 수율 계산기")
st.markdown("출발 물질과 생성물의 화학식을 분석하여 **분자량**과 **반응비**를 스스로 찾아냅니다.")

# 레이아웃 구성
col1, col2 = st.columns(2)

with col1:
    st.subheader("반응물 (Reactant)")
    reactant_formula = st.text_input("출발 물질 화학식", value="Nd2O3")
    reactant_mass = st.number_input("투입량 (g)", min_value=0.0001, value=10.0, step=0.1, format="%.4f")

with col2:
    st.subheader("생성물 (Product)")
    product_formula = st.text_input("생성물 화학식", value="NdF3")
    product_mass = st.number_input("실제 생산량 (g)", min_value=0.0, value=11.9, step=0.1, format="%.4f")

st.markdown("---")

# 실시간 계산 로직
try:
    if reactant_formula and product_formula:
        # 1. 화학식 파싱
        react_dict = parse_formula(reactant_formula)
        prod_dict = parse_formula(product_formula)
        
        # 2. 분자량 계산
        reactant_mw = calculate_mw(react_dict)
        product_mw = calculate_mw(prod_dict)
        
        # 3. 반응비 자동 계산
        auto_ratio, target_el = find_stoichiometric_ratio(react_dict, prod_dict)
        
        # UI: 계산된 반응비 정보 표시 및 수동 오버라이드 옵션
        st.subheader("⚖️ 반응비 설정")
        if target_el:
            st.info(f"✨ **공통 원소 [{target_el}]** 를 기준으로 분석한 결과, **자동 계산된 반응비는 [ {auto_ratio:.2f} ]** 입니다.")
        else:
            st.warning("공통 원소를 찾을 수 없어 기본 반응비(1)를 적용합니다.")
            
        use_manual_ratio = st.checkbox("자동 계산된 반응비 대신 직접 입력하기")
        if use_manual_ratio:
            ratio = st.number_input("반응비 직접 입력", min_value=0.001, value=float(auto_ratio), step=0.1)
        else:
            ratio = auto_ratio
        
        st.markdown("### 📊 분석 결과")
        c1, c2 = st.columns(2)
        c1.metric(f"출발 물질 ({reactant_formula})", f"{reactant_mw:.4f} g/mol")
        c2.metric(f"생성물 ({product_formula})", f"{product_mw:.4f} g/mol")
        
        if reactant_mw > 0 and product_mw > 0:
            # 4. 이론적 생산량 계산
            moles_reactant = reactant_mass / reactant_mw
            theoretical_yield = moles_reactant * ratio * product_mw
            
            st.markdown("---")
            st.success(f"🎯 **이론적 생산 가능량:** {theoretical_yield:.4f} g")
            
            # 5. 수율 계산
            if product_mass > 0:
                percent_yield = (product_mass / theoretical_yield) * 100
                
                if percent_yield > 100:
                    st.warning(f"**최종 수율:** {percent_yield:.2f} % (100% 초과 - 용매 건조 상태 등 확인 필요)")
                else:
                    st.info(f"**최종 수율:** {percent_yield:.2f} %")
                    
except ValueError as e:
    st.error(f"입력 오류: {e}")
except Exception as e:
    st.error(f"계산 중 오류가 발생했습니다: {e}")