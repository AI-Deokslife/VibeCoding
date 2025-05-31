import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image, ImageDraw, ImageFont
import io
import json
import copy
import uuid # For text item IDs
import os

# --- Configuration ---
# IMPORTANT: Download these font files and place them in a 'fonts' directory
# relative to your script, or provide absolute paths.
# Example: 'fonts/NotoSansKR-Regular.ttf'
AVAILABLE_FONTS = {
    "Noto Sans KR": "fonts/NotoSansKR-Regular.ttf",
    "Jua": "fonts/Jua-Regular.ttf",
    "Do Hyeon": "fonts/DoHyeon-Regular.ttf",
    "Nanum Gothic": "fonts/NanumGothic-Regular.ttf",
    "Nanum Myeongjo": "fonts/NanumMyeongjo-Regular.ttf",
    "Gowun Dodum": "fonts/GowunDodum-Regular.ttf",
    "Black Han Sans": "fonts/BlackHanSans-Regular.ttf",
    "Hahmlet": "fonts/Hahmlet-Regular.ttf",
    "Gaegu": "fonts/Gaegu-Regular.ttf",
    "Nanum Pen Script": "fonts/NanumPenScript-Regular.ttf",
    "Arial": "arial.ttf", # Common system font, often available
    "Default (Fallback)": "arial.ttf" # Fallback if others fail
}

# Create fonts directory if it doesn't exist, to avoid initial errors if user hasn't created it
if not os.path.exists("fonts"):
    os.makedirs("fonts")
    st.info("A 'fonts' directory has been created. Please place your .ttf font files there and update AVAILABLE_FONTS paths if necessary.")


def get_font_path(font_name, size=32): # Added size for default font
    """Gets the path to a font file, with fallback."""
    font_path_suggestion = AVAILABLE_FONTS.get(font_name)
    
    if font_path_suggestion and os.path.exists(font_path_suggestion):
        try:
            ImageFont.truetype(font_path_suggestion, size) # Test if font is valid
            return font_path_suggestion
        except IOError:
            st.warning(f"Could not load font '{font_name}' from '{font_path_suggestion}'. Trying fallback.")
            pass # Fall through to other fallbacks

    # Try Arial as a common system font
    arial_path = AVAILABLE_FONTS.get("Arial")
    if arial_path and os.path.exists(arial_path):
        try:
            ImageFont.truetype(arial_path, size)
            if font_name not in ["Arial", "Default (Fallback)"]: # Avoid warning if Arial was intended
                 st.warning(f"Font '{font_name}' not found or invalid. Using Arial as fallback.")
            return arial_path
        except IOError:
            pass # Arial also failed

    st.error(f"Font '{font_name}' and Arial fallback not found or invalid. Using Pillow's default font. Text rendering might be poor.")
    return None # Will lead to ImageFont.load_default()


# --- Session State Initialization ---
if "history" not in st.session_state:
    st.session_state.history = []
if "history_index" not in st.session_state:
    st.session_state.history_index = -1
if "current_text_items" not in st.session_state:
    st.session_state.current_text_items = [] 
if "current_drawing_json" not in st.session_state:
    st.session_state.current_drawing_json = {"objects": []} 
if "uploaded_image_pil" not in st.session_state:
    st.session_state.uploaded_image_pil = None
if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None
if "active_text_edit_id" not in st.session_state:
    st.session_state.active_text_edit_id = None
if "app_key_counter" not in st.session_state: 
    st.session_state.app_key_counter = 0
if "current_mode" not in st.session_state:
    st.session_state.current_mode = "텍스트" # Default mode
if "brush_color" not in st.session_state:
    st.session_state.brush_color = "#000000"
if "brush_size" not in st.session_state:
    st.session_state.brush_size = 10


# --- Helper Functions ---
def save_current_state():
    """Saves the current state (text items and drawing) to history."""
    st.session_state.history = st.session_state.history[:st.session_state.history_index + 1]
    
    state_snapshot = {
        "text_items": copy.deepcopy(st.session_state.current_text_items),
        "drawing_json": copy.deepcopy(st.session_state.current_drawing_json)
    }
    st.session_state.history.append(state_snapshot)
    st.session_state.history_index += 1

def load_state_from_history(index):
    """Loads a state from history by index."""
    if 0 <= index < len(st.session_state.history):
        snapshot = st.session_state.history[index]
        st.session_state.current_text_items = copy.deepcopy(snapshot["text_items"])
        st.session_state.current_drawing_json = copy.deepcopy(snapshot["drawing_json"])
        st.session_state.history_index = index
        st.session_state.active_text_edit_id = None 
        st.session_state.app_key_counter += 1 # Force re-render of components like canvas

def generate_image_with_text(base_image_pil, text_items_list):
    """Draws text items onto a copy of the base image."""
    if base_image_pil is None:
        img = Image.new("RGBA", (800, 600), (255, 255, 255, 255)) # Default blank white canvas
    else:
        img = base_image_pil.copy().convert("RGBA")

    draw = ImageDraw.Draw(img)
    for item in text_items_list:
        font_path = get_font_path(item["font"], item["size"])
        try:
            if font_path:
                font = ImageFont.truetype(font_path, item["size"])
            else: # Fallback to Pillow's default if get_font_path returned None
                font = ImageFont.load_default()
        except IOError:
            st.error(f"Error loading font: {item['font']} at path '{font_path}'. Using default.")
            font = ImageFont.load_default()

        text_content = item["content"]
        text_color = item["color"]
        
        # For rotation: draw on a separate transparent surface, rotate, then paste
        # Get text size using textbbox for better accuracy
        try:
            # Calculate bounding box on a dummy draw object to handle multi-line potential
            # For single line, (0,0) anchor is fine.
            text_bbox = draw.textbbox((0,0), text_content, font=font, anchor="lt") 
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
        except Exception as e: # Catch any error during textbbox calculation
            st.warning(f"Could not calculate text dimensions for '{text_content[:20]}...': {e}. Skipping text item.")
            continue


        if text_width <= 0 or text_height <= 0: continue # Skip empty or invalid text

        txt_img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0)) # Transparent background
        txt_draw = ImageDraw.Draw(txt_img)
        txt_draw.text((0, 0), text_content, font=font, fill=text_color, anchor="lt")

        rotated_txt_img = txt_img.rotate(float(item["angle"]), expand=True, resample=Image.BICUBIC)
        
        paste_x = item["x"] - rotated_txt_img.width // 2
        paste_y = item["y"] - rotated_txt_img.height // 2
        
        img.paste(rotated_txt_img, (paste_x, paste_y), rotated_txt_img)
            
    return img

# --- UI Layout ---
st.set_page_config(layout="wide", page_title="인스타툰 편집기")
st.title("🎨 인스타툰 편집기 (Streamlit Version)")
st.markdown("간단한 인스타툰 이미지 편집기입니다. 이미지를 올리고 텍스트를 추가하거나 그림을 그려보세요!")

# --- Sidebar Controls ---
with st.sidebar:
    st.header("🛠️ 도구")
    
    uploaded_file = st.file_uploader("1. 이미지 가져오기:", type=["png", "jpg", "jpeg"], key=f"uploader_{st.session_state.app_key_counter}")
    if uploaded_file:
        if st.session_state.uploaded_file_name != uploaded_file.name:
            try:
                st.session_state.uploaded_image_pil = Image.open(uploaded_file)
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.current_text_items = []
                st.session_state.current_drawing_json = {"objects": []}
                save_current_state() 
                st.session_state.app_key_counter += 1
                st.rerun()
            except Exception as e:
                st.error(f"이미지 파일을 여는 데 실패했습니다: {e}")
                st.session_state.uploaded_image_pil = None
                st.session_state.uploaded_file_name = None


    st.session_state.current_mode = st.radio(
        "2. 모드 선택:", 
        ("텍스트", "브러시"), 
        index=0 if st.session_state.current_mode == "텍스트" else 1, 
        key=f"mode_radio_{st.session_state.app_key_counter}"
    )

    # Text Mode Controls
    if st.session_state.current_mode == "텍스트":
        st.subheader("📝 텍스트 설정")
        with st.form(key="new_text_form"):
            new_text_content = st.text_input("텍스트 내용:")
            col1, col2 = st.columns(2)
            with col1:
                new_text_font = st.selectbox("폰트:", list(AVAILABLE_FONTS.keys()), index =0)
                new_text_x = st.number_input("X 좌표:", value=100, step=10, format="%d")
            with col2:
                new_text_size = st.slider("크기:", 10, 150, 32) # Increased max size
                new_text_y = st.number_input("Y 좌표:", value=100, step=10, format="%d")
            new_text_color = st.color_picker("색상:", "#000000")
            new_text_angle = st.slider("회전 각도 (-180° ~ 180°):", -180.0, 180.0, 0.0, 1.0) # Finer control for angle

            submitted_new_text = st.form_submit_button("텍스트 추가")
            if submitted_new_text and new_text_content:
                st.session_state.current_text_items.append({
                    "id": str(uuid.uuid4()), "content": new_text_content, 
                    "x": new_text_x, "y": new_text_y, "font": new_text_font, 
                    "size": new_text_size, "color": new_text_color, "angle": new_text_angle
                })
                save_current_state()
                st.session_state.app_key_counter += 1
                st.rerun()
        
        st.markdown("---")
        st.subheader("📜 텍스트 목록 & 편집")
        if not st.session_state.current_text_items:
            st.caption("추가된 텍스트가 없습니다.")

        for i, item in reversed(list(enumerate(st.session_state.current_text_items))): # Show newest first
            item_id = item["id"]
            with st.expander(f"텍스트 {len(st.session_state.current_text_items) - i}: {item['content'][:20]}"):
                if st.session_state.active_text_edit_id == item_id:
                    with st.form(key=f"edit_form_{item_id}"):
                        edit_content = st.text_input("내용:", value=item["content"], key=f"edit_content_{item_id}")
                        c1, c2 = st.columns(2)
                        edit_x = c1.number_input("X:", value=item["x"], step=10, key=f"edit_x_{item_id}", format="%d")
                        edit_y = c2.number_input("Y:", value=item["y"], step=10, key=f"edit_y_{item_id}", format="%d")
                        
                        default_font_index = 0
                        try:
                            default_font_index = list(AVAILABLE_FONTS.keys()).index(item["font"])
                        except ValueError: # If font not in keys, use default
                            pass
                        edit_font = st.selectbox("폰트:", list(AVAILABLE_FONTS.keys()), index=default_font_index, key=f"edit_font_{item_id}")
                        
                        edit_size = st.slider("크기:", 10, 150, value=item["size"], key=f"edit_size_{item_id}")
                        edit_color = st.color_picker("색상:", value=item["color"], key=f"edit_color_{item_id}")
                        edit_angle = st.slider("회전:", -180.0, 180.0, value=float(item["angle"]), step=1.0, key=f"edit_angle_{item_id}")

                        col_update, col_cancel = st.columns(2)
                        if col_update.form_submit_button("✔️ 업데이트", use_container_width=True):
                            st.session_state.current_text_items[i] = {
                                "id": item_id, "content": edit_content, "x": edit_x, "y": edit_y,
                                "font": edit_font, "size": edit_size, "color": edit_color, "angle": edit_angle
                            }
                            st.session_state.active_text_edit_id = None
                            save_current_state()
                            st.session_state.app_key_counter += 1
                            st.rerun()
                        if col_cancel.form_submit_button("✖️ 취소", type="secondary", use_container_width=True):
                            st.session_state.active_text_edit_id = None
                            st.rerun()
                else:
                    st.markdown(f"**내용**: `{item['content']}`")
                    st.markdown(f"**위치**: `({item['x']}, {item['y']})`, **크기**: `{item['size']}`, **각도**: `{item['angle']:.1f}°`")
                    st.markdown(f"**폰트**: `{item['font']}`, **색상**: <span style='color:{item['color']}; font-weight:bold;'>{item['color']}</span>", unsafe_allow_html=True)
                    
                    col_edit, col_delete = st.columns(2)
                    if col_edit.button("✏️ 편집", key=f"edit_{item_id}", use_container_width=True):
                        st.session_state.active_text_edit_id = item_id
                        st.rerun()
                    if col_delete.button("🗑️ 삭제", key=f"delete_{item_id}", type="primary", use_container_width=True):
                        st.session_state.current_text_items.pop(i)
                        st.session_state.active_text_edit_id = None # Ensure no lingering edit state
                        save_current_state()
                        st.session_state.app_key_counter += 1
                        st.rerun()

    # Brush Mode Controls
    elif st.session_state.current_mode == "브러시":
        st.subheader("🖌️ 브러시 설정")
        st.session_state.brush_color = st.color_picker("브러시 색상:", st.session_state.brush_color, key="brush_color_picker")
        st.session_state.brush_size = st.slider("브러시 크기:", 1, 100, st.session_state.brush_size, key="brush_size_slider") # Increased max size
        if st.button("브러시만 지우기", key="clear_brush_btn", use_container_width=True):
            st.session_state.current_drawing_json = {"objects": []} # Reset drawing
            save_current_state()
            st.session_state.app_key_counter += 1
            st.rerun()
    
    st.markdown("---")
    st.subheader("🎨 작업 관리")
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        can_undo = st.session_state.history_index > 0
        if st.button("↩️ 실행 취소", disabled=not can_undo, use_container_width=True):
            load_state_from_history(st.session_state.history_index - 1)
            st.rerun()
    with col_hist2:
        can_redo = st.session_state.history_index < len(st.session_state.history) - 1
        if st.button("↪️ 다시 실행", disabled=not can_redo, use_container_width=True):
            load_state_from_history(st.session_state.history_index + 1)
            st.rerun()

    if st.button("🗑️ 모두 지우기", key="clear_all_btn", type="primary", use_container_width=True):
        st.session_state.uploaded_image_pil = None 
        st.session_state.uploaded_file_name = None
        st.session_state.current_text_items = []
        st.session_state.current_drawing_json = {"objects": []}
        st.session_state.history = [] # Clear history too
        st.session_state.history_index = -1
        save_current_state() # Save this cleared state as the new initial state
        st.session_state.app_key_counter += 1
        st.rerun()

    # Prepare image for canvas
    image_with_text_pil = generate_image_with_text(
        st.session_state.uploaded_image_pil,
        st.session_state.current_text_items
    )
    
    st.markdown("---")
    st.subheader("💾 저장")
    # This will be updated after canvas rendering if there's drawing output
    final_image_for_download_pil = image_with_text_pil 


# --- Main Canvas Area ---
main_col1, main_col2 = st.columns([3, 1]) # Canvas column, Info column

with main_col1:
    st.markdown("### 🖼️ 캔버스")
    canvas_display_width = 700 # Max width for canvas display
    canvas_display_height = 500 # Max height for canvas display

    if image_with_text_pil:
        img_w, img_h = image_with_text_pil.size
        aspect_ratio = img_w / img_h
        
        # Calculate display dimensions maintaining aspect ratio
        if aspect_ratio > (canvas_display_width / canvas_display_height): # Wider than max aspect
            display_w = canvas_display_width
            display_h = int(canvas_display_width / aspect_ratio)
        else: # Taller than max aspect or fits
            display_h = canvas_display_height
            display_w = int(canvas_display_height * aspect_ratio)
        
        # Ensure display dimensions are at least 1x1
        display_w = max(1, display_w)
        display_h = max(1, display_h)

        resized_image_for_canvas = image_with_text_pil.resize((display_w, display_h), Image.Resampling.LANCZOS)
    else: 
        display_w, display_h = canvas_display_width, canvas_display_height
        resized_image_for_canvas = Image.new("RGBA", (display_w, display_h), (230, 230, 230, 255)) 

    canvas_key = f"drawable_canvas_{st.session_state.app_key_counter}"
    
    # Determine drawing mode for canvas: 'freedraw' for brush, 'transform' otherwise (though transform won't affect PIL text)
    # 'transform' allows selecting/moving objects drawn by st_canvas itself.
    canvas_drawing_mode = "freedraw" if st.session_state.current_mode == "브러시" else "transform"

    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.0)",  # Transparent fill for shapes drawn by canvas toolbar
        stroke_width=st.session_state.brush_size if st.session_state.current_mode == "브러시" else 2,
        stroke_color=st.session_state.brush_color if st.session_state.current_mode == "브러시" else "#0000FF", # Blue for transform mode shapes
        background_color="rgba(230, 230, 230, 1)", # Canvas element background if image is smaller
        background_image=resized_image_for_canvas, 
        update_streamlit=True, 
        height=display_h,
        width=display_w,
        drawing_mode=canvas_drawing_mode,
        initial_drawing=st.session_state.current_drawing_json if st.session_state.current_drawing_json else {"objects": []}, # Ensure valid JSON
        key=canvas_key,
        display_toolbar=True # Show the small toolbar of st_canvas for shapes/canvas-undo
    )

    # Process canvas results
    if canvas_result and canvas_result.image_data is not None:
        final_image_for_download_pil = Image.fromarray(canvas_result.image_data.astype('uint8'), 'RGBA')

        if canvas_result.json_data is not None and \
           canvas_result.json_data != st.session_state.current_drawing_json:
            if st.session_state.current_mode == "브러시": 
                st.session_state.current_drawing_json = canvas_result.json_data
                save_current_state()
                # No rerun here, update_streamlit=True handles it.

    # Download Button (moved to sidebar, but uses final_image_for_download_pil which is updated after canvas)
    if final_image_for_download_pil:
        buf = io.BytesIO()
        final_image_for_download_pil.save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.sidebar.download_button(
            label="이미지 저장 (PNG)",
            data=byte_im,
            file_name="instatoon_streamlit.png",
            mime="image/png",
            use_container_width=True
        )
    else:
        st.sidebar.caption("저장할 이미지가 없습니다.")

with main_col2:
    st.markdown("### ℹ️ 정보")
    st.caption(f"**현재 모드**: {st.session_state.current_mode}")
    if st.session_state.uploaded_image_pil:
        orig_w, orig_h = st.session_state.uploaded_image_pil.size
        st.caption(f"**원본 이미지 크기**: {orig_w}x{orig_h}")
    st.caption(f"**캔버스 크기**: {display_w}x{display_h}")
    st.caption(f"**텍스트 객체 수**: {len(st.session_state.current_text_items)}")
    
    num_drawing_objects = 0
    if st.session_state.current_drawing_json and "objects" in st.session_state.current_drawing_json:
        num_drawing_objects = len(st.session_state.current_drawing_json["objects"])
    st.caption(f"**브러시 객체 수**: {num_drawing_objects}")
    
    st.markdown("---")
    st.markdown("#### 사용 방법:")
    st.markdown("""
    1.  **이미지 가져오기**: 편집할 이미지를 업로드합니다.
    2.  **모드 선택**: '텍스트' 또는 '브러시' 모드를 선택합니다.
        * **텍스트 모드**: 글꼴, 크기, 색상, 위치, 회전을 설정하고 텍스트를 추가합니다. 목록에서 기존 텍스트를 편집하거나 삭제할 수 있습니다.
        * **브러시 모드**: 브러시 색상과 크기를 설정하고 캔버스에 그림을 그립니다. `streamlit-drawable-canvas`의 자체 툴바를 사용하여 도형을 그릴 수도 있습니다.
    3.  **작업 관리**: '실행 취소', '다시 실행', '모두 지우기' 기능을 사용합니다.
    4.  **저장**: 완성된 이미지를 PNG 파일로 다운로드합니다.
    """)
    st.markdown("---")
    st.markdown("##### 폰트 안내:")
    st.markdown("이 앱은 지정된 경로에서 폰트 파일(.ttf)을 로드하려고 시도합니다. `fonts` 폴더에 원하는 폰트를 넣고 `AVAILABLE_FONTS` 변수를 수정하세요. 폰트 로드 실패 시 경고가 표시될 수 있으며, 기본 폰트로 대체됩니다.")


# Debugging info (optional, uncomment to use)
# with st.sidebar.expander("Debug Info"):
#     st.json(st.session_state.current_text_items, expanded=False)
#     st.json(st.session_state.current_drawing_json, expanded=False)
#     st.write(f"History Index: {st.session_state.history_index} / {len(st.session_state.history)-1 if st.session_state.history else -1}")
#     st.write(f"App Key Counter: {st.session_state.app_key_counter}")
#     st.write(f"Uploaded File Name: {st.session_state.uploaded_file_name}")
#     st.write(f"Active Edit ID: {st.session_state.active_text_edit_id}")
