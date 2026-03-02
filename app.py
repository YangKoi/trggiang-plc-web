import streamlit as st
import time
from pymodbus.client import ModbusTcpClient

# Cấu hình trang hiển thị rộng rãi hơn
st.set_page_config(page_title="PLC Monitor", layout="wide")
st.title("🌐 Bảng Điều Khiển Giám Sát PLC Inovance")

# ==========================================
# 1. GIAO DIỆN CÀI ĐẶT KẾT NỐI (SIDEBAR)
# ==========================================
# st.sidebar giúp tạo một khu vực cài đặt gọn gàng bên trái màn hình
st.sidebar.header("⚙️ Cài đặt Kết nối")

# Tạo ô nhập liệu cho người dùng tự gõ IP và Port
# Giá trị mặc định vẫn để là 127.0.0.1 để bạn tiện thử mô phỏng
user_ip = st.sidebar.text_input("Nhập địa chỉ IP của PLC:", value="127.0.0.1")
user_port = st.sidebar.number_input("Cổng (Port):", value=502, step=1)

# Chuyển công tắc bật/tắt sang thanh bên
run_monitoring = st.sidebar.toggle("🚀 Bắt đầu Kết nối & Giám sát")

# Các hằng số địa chỉ trong PLC (Giữ nguyên)
SLAVE_ID = 1
COIL_ADDRESS = 0
REGISTER_ADDRESS = 100

# ==========================================
# 2. HÀM LẤY DỮ LIỆU TỪ PLC (ĐÃ NÂNG CẤP)
# ==========================================
# Khai báo hàm nhận 2 tham số: ip và port
def get_plc_data(ip, port):
    client = ModbusTcpClient(ip, port=port, timeout=1) 
    data = {"connected": False, "is_running": False, "temperature": 0}
    
    if client.connect():
        data["connected"] = True
        
        # Đọc dữ liệu
        coil_result = client.read_coils(address=COIL_ADDRESS, count=1, slave=SLAVE_ID)
        if not coil_result.isError():
            data["is_running"] = coil_result.bits[0]
            
        reg_result = client.read_holding_registers(address=REGISTER_ADDRESS, count=1, slave=SLAVE_ID)
        if not reg_result.isError():
            data["temperature"] = reg_result.registers[0]
            
        client.close()
    return data

# ==========================================
# 3. GIAO DIỆN HIỂN THỊ CHÍNH TỰ ĐỘNG
# ==========================================
placeholder = st.empty()

if run_monitoring:
    while True:
        # Cung cấp IP và Port mà người dùng vừa nhập vào hàm
        plc_data = get_plc_data(user_ip, user_port)
        
        with placeholder.container():
            if plc_data["connected"]:
                st.success(f"🟢 Đã kết nối thành công tới PLC tại {user_ip}:{user_port}")
                
                col1, col2 = st.columns(2)
                with col1:
                    trang_thai = "Đang Chạy" if plc_data["is_running"] else "Đã Dừng"
                    st.metric(label="Trạng thái máy", value=trang_thai)
                with col2:
                    st.metric(label="Nhiệt độ hiện tại", value=f"{plc_data['temperature']} °C")
            else:
                st.error(f"🔴 Mất kết nối! Không thể tìm thấy PLC tại {user_ip}:{user_port}...")
                st.info("💡 Mẹo: Nếu chạy mô phỏng, hãy đảm bảo AutoShop đang ở trạng thái RUN và bật Modbus TCP.")
                
        time.sleep(2)
else:
    with placeholder.container():
        st.info(f"Hệ thống đang chờ. Vui lòng kiểm tra IP (hiện tại: {user_ip}) và bật công tắc bên trái để bắt đầu.")
