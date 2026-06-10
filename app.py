import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import json
import base64
from io import BytesIO

st.set_page_config(
    page_title="知识书架系统",
    page_icon="📚",
    layout="wide"
)

# 初始化session state
if 'categories' not in st.session_state:
    st.session_state.categories = ['科技', '艺术', '文学', '生活', '其他']

if 'book_items' not in st.session_state:
    # 尝试从secrets加载（生产环境）
    try:
        if 'book_data' in st.secrets:
            st.session_state.book_items = json.loads(st.secrets['book_data'])
        else:
            st.session_state.book_items = []
    except:
        st.session_state.book_items = []

# 侧边栏
st.sidebar.title("📚 知识书架系统")

# 密码验证
password_correct = False
with st.sidebar:
    password = st.text_input("主机密码", type="password")
    if password == "admin123":
        password_correct = True
        st.sidebar.success("✅ 主机模式已解锁")
    else:
        st.sidebar.info("🔒 输入密码进入主机模式")

st.title("📚 知识书架系统")

# 主机模式 - 添加内容
if password_correct:
    st.header("✏️ 添加新内容")
    
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("标题 *")
            category = st.selectbox("分类", st.session_state.categories)
            text_content = st.text_area("文本内容", height=150)
        
        with col2:
            image_file = st.file_uploader("上传图片", type=['jpg', 'jpeg', 'png', 'gif'])
            tags = st.text_input("标签", placeholder="用逗号分隔，如：Python,教程")
        
        submitted = st.form_submit_button("📌 添加到书架")
        
        if submitted and title:
            # 处理图片
            image_base64 = None
            if image_file:
                image = Image.open(image_file)
                # 调整图片大小
                image.thumbnail((800, 800))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode()
            
            item = {
                "id": len(st.session_state.book_items),
                "title": title,
                "category": category,
                "text": text_content,
                "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                "image_base64": image_base64,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            st.session_state.book_items.append(item)
            st.success(f"✅ 已添加：{title}")
            st.rerun()
        elif submitted and not title:
            st.error("请填写标题")

# 浏览模式
st.header("📖 浏览书架")

# 筛选功能
col1, col2, col3 = st.columns(3)
with col1:
    filter_cat = st.selectbox("分类筛选", ["全部"] + st.session_state.categories)
with col2:
    search = st.text_input("关键词搜索", placeholder="标题或内容...")
with col3:
    if st.button("🔄 重置"):
        filter_cat = "全部"
        search = ""

# 过滤数据
items = st.session_state.book_items
if filter_cat != "全部":
    items = [item for item in items if item.get('category') == filter_cat]
if search:
    items = [
        item for item in items 
        if search.lower() in item.get('title', '').lower() 
        or search.lower() in item.get('text', '').lower()
    ]

st.markdown(f"**共找到 {len(items)} 个项目**")

# 备份和恢复
col1, col2 = st.columns(2)
with col1:
    if st.button("💾 备份数据"):
        data = json.dumps(st.session_state.book_items, ensure_ascii=False, indent=2)
        st.download_button("下载备份", data, "book_backup.json", "application/json")
with col2:
    backup_file = st.file_uploader("恢复备份", type=['json'])
    if backup_file:
        data = json.load(backup_file)
        st.session_state.book_items = data
        st.success("数据已恢复")
        st.rerun()

# 显示项目
if items:
    for i, item in enumerate(items):
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"### {item.get('title', '无标题')}")
                st.markdown(f"**分类：** {item.get('category', '未分类')}")
                st.markdown(f"**标签：** {', '.join(item.get('tags', [])) if item.get('tags') else '无'}")
                
                if item.get('text'):
                    text_preview = item['text'][:300]
                    if len(item['text']) > 300:
                        text_preview += "..."
                    st.markdown(f"**内容：** {text_preview}")
                
                st.caption(f"📅 {item.get('created_at', '未知')}")
            
            with col2:
                if item.get('image_base64'):
                    st.image(f"data:image/png;base64,{item['image_base64']}", use_container_width=True)
            
            # 删除按钮（仅主机）
            if password_correct:
                if st.button("🗑️ 删除", key=f"del_{item.get('id', i)}"):
                    st.session_state.book_items = [x for x in st.session_state.book_items if x.get('id') != item.get('id')]
                    st.rerun()
else:
    st.info("📭 书架上还没有内容，请切换到主机模式添加")

# 页脚
st.markdown("---")
st.markdown("### 📌 使用说明")
st.markdown("""
- **访客模式**：浏览、搜索、筛选内容
- **主机模式**：输入密码 `admin123` 进入，可添加、删除内容
- **数据备份**：点击"备份数据"下载，需要时用"恢复备份"还原
""")