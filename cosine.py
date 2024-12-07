import streamlit as st
import pandas as pd
import pickle

# Hàm lấy gợi ý sản phẩm
def get_recommendations(df, ma_san_pham, cosine_sim, nums=5):
    matching_indices = df.index[df['ma_san_pham'] == ma_san_pham].tolist()
    if not matching_indices:
        st.warning(f"Không tìm thấy sản phẩm với ID: {ma_san_pham}")
        return pd.DataFrame()
    idx = matching_indices[0]

    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:nums + 1]
    product_indices = [i[0] for i in sim_scores]

    return df.iloc[product_indices]

# Hiển thị sản phẩm gợi ý
def display_recommended_products(recommended_products, cols=5):
    for i in range(0, len(recommended_products), cols):
        col_list = st.columns(cols)
        for j, col in enumerate(col_list):
            if i + j < len(recommended_products):
                product = recommended_products.iloc[i + j]
                with col:
                    st.write(f"### {product['ten_san_pham']}")
                    gia_ban_formatted = f"{product['gia_ban']:,.0f}".replace(",", ".")
                    gia_goc_formatted = f"{product['gia_goc']:,.0f}".replace(",", ".")
                    st.write(f"**Giá bán:** {gia_ban_formatted} VND")
                    st.write(f"**Giá gốc:** {gia_goc_formatted} VND")
                    expander = st.expander("Mô tả")
                    product_description = product['mo_ta']
                    truncated_description = ' '.join(product_description.split()[:100]) + "..."
                    expander.write(truncated_description)

# Đọc dữ liệu sản phẩm và khách hàng
df_products = pd.read_csv('San_pham_2xuly.csv')
df_customers = pd.read_csv('Khach_hang_2xuly.csv')

# Đọc file cosine similarity
with open('products_cosine_sim.pkl', 'rb') as f:
    cosine_sim_new = pickle.load(f)
    # Giới hạn danh sách sản phẩm và khách hàng
limited_products = df_products.head(20)
limited_customers = df_customers.head(20)
# Giao diện Streamlit
st.image('hasaki1.jpg', use_container_width=True)
st.title("💎 Hệ thống gợi ý sản phẩm Recommender System 💎")
# GUI
st.title("Data Science Project 2 Deployment")
st.write("Content-Based Filtering")

menu = ["Business Objective","Hiển thị chart", "Gợi ý sản phẩm", "Gợi ý mã khách hàng"]
choice = st.sidebar.selectbox('Menu', menu)

st.sidebar.write("""#### Thành viên thực hiện:
                 Phan Văn Minh & Cao Anh Hào""")
st.sidebar.write("""#### Giảng viên hướng dẫn:Ms Phương """)
st.sidebar.write("""#### Ngày báo cáo tốt nghiệp: 16/12/2024""")

if choice == 'Business Objective':
   
    st.subheader("Business Objective")
    st.write("""
    ###### HASAKI.VN là hệ thống cửa hàng mỹ phẩm chính hãng và dịch vụ chăm sóc sắc đẹp chuyên sâu với hệ thống cửa hàng trải dài toàn quốc.Họ muốn biết về sản phẩm của mình thông qua lựa chọn sản phẩm,đánh giá của khách hàng nhằm phục vụ tốt cho việc phát triển kinh doanh và đáp ứng thị hiếu của khách hàng.
    """)  
    st.write("""###### => Yêu cầu: Dùng thuật toán Machine Learning trong Python để giải quyết vấn đề.Cụ thể là dùng Content-based recommender system""")
    st.image("2.png")

elif choice == 'Hiển thị chart':
    st.subheader("Biểu đồ Heatmap")
    st.write("Lấy một phần nhỏ trong Cosine_sim,tương ứng với ma trận 18 x18. Gồm các giá trị liên quan đến 18 sản phẩm đầu tiên trong danh sách để trực quan hoá")
    st.image('heatmap.png', use_container_width=True)
elif choice == 'Gợi ý sản phẩm':

    # Gợi ý theo mã sản phẩm
    st.header("🔍 Gợi ý sản phẩm tương tự")

    if "selected_ma_san_pham" not in st.session_state:
        st.session_state.selected_ma_san_pham = None

    product_options = [(row['ten_san_pham'], row['ma_san_pham']) for _, row in limited_products.iterrows()]
    selected_product = st.selectbox(
        "Chọn sản phẩm:",
        options=product_options,
        format_func=lambda x: x[0],
        key="product_selectbox"
    )

    if selected_product:
        st.session_state.selected_ma_san_pham = selected_product[1]

    if st.session_state.selected_ma_san_pham:
        ma_san_pham = st.session_state.selected_ma_san_pham
        selected_product_row = df_products[df_products['ma_san_pham'] == ma_san_pham].iloc[0]
        gia_ban_formatted = f"{selected_product_row['gia_ban']:,.0f}".replace(",", ".")
        gia_goc_formatted = f"{selected_product_row['gia_goc']:,.0f}".replace(",", ".")
        st.write("### Bạn đã chọn:")
        st.write(f"**Tên sản phẩm:** {selected_product_row['ten_san_pham']}")
        st.write(f"**Giá bán:** {gia_ban_formatted} VND")
        st.write(f"**Giá gốc:** {gia_goc_formatted} VND")


        recommendations = get_recommendations(df_products, ma_san_pham, cosine_sim_new, nums=5)
        if not recommendations.empty:
            st.write("### Các sản phẩm tương tự:")
            display_recommended_products(recommendations, cols=3)
        else:
            st.write("Không tìm thấy sản phẩm tương tự.")
elif choice == 'Gợi ý mã khách hàng':
    # Gợi ý theo ID khách hàng
    st.header("👤 Gợi ý sản phẩm theo mã khách hàng")

    if "selected_user_id" not in st.session_state:
        st.session_state.selected_user_id = None

    # Khởi tạo trạng thái lưu sản phẩm gần nhất của từng khách hàng
    if "recent_product_by_user" not in st.session_state:
        st.session_state.recent_product_by_user = {}

    # Lựa chọn khách hàng
    customer_options = [(row['ho_ten'], row['userId']) for _, row in limited_customers.iterrows()]
    selected_customer = st.selectbox(
        "Chọn khách hàng:",
        options=customer_options,
        format_func=lambda x: x[0],
        key="customer_selectbox"
    )

    if selected_customer:
        st.session_state.selected_user_id = selected_customer[1]

    if st.session_state.selected_user_id:
        user_id = st.session_state.selected_user_id
        customer_name = [cust[0] for cust in customer_options if cust[1] == user_id][0]
        st.write(f"Xin chào, **{customer_name}**!")

        # Kiểm tra sản phẩm gần nhất đã xem cho khách hàng, nếu chưa có thì khởi tạo
        if user_id not in st.session_state.recent_product_by_user:
            st.session_state.recent_product_by_user[user_id] = df_products.sample(1).iloc[0]

        # Lấy sản phẩm gần nhất cho khách hàng hiện tại
        recent_product = st.session_state.recent_product_by_user[user_id]

        st.write("### Sản phẩm gần nhất đã xem:")
        recent_gia_ban = f"{recent_product['gia_ban']:,.0f}".replace(",", ".")
        recent_gia_goc = f"{recent_product['gia_goc']:,.0f}".replace(",", ".")
        st.write(f"- **Tên sản phẩm:** {recent_product['ten_san_pham']}")
        st.write(f"- **Mã sản phẩm:** {recent_product['ma_san_pham']}")
        st.write(f"- **Giá bán:** {recent_gia_ban} VND")
        st.write(f"- **Giá gốc:** {recent_gia_goc} VND")


        # Lấy gợi ý sản phẩm dựa trên sản phẩm gần nhất
        recommendations = get_recommendations(df_products, recent_product['ma_san_pham'], cosine_sim_new, nums=5)
        if not recommendations.empty:
            st.write("### Các sản phẩm gợi ý:")
            display_recommended_products(recommendations, cols=3)
        else:
            st.write("Không tìm thấy sản phẩm gợi ý cho khách hàng này.")