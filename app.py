import streamlit as st
import time
from pymodbus.client import ModbusTcpClient

# ==========================================
# 1. CẤU HÌNH KẾT NỐI
# ==========================================
PLC_IP = '127.0.0.1' # Cần đổi thành IP thật (Public IP) khi chạy trên Streamlit Cloud
PORT = 502
SLAVE_ID = 1
COIL_ADDRESS = 0
REGISTER_ADDRESS = 100

st.set_page_config(page_title="PLC Monitor", layout="centered")
st.title("🌐 Bảng Điều Khiển Giám Sát PLC Inovance")

# ==========================================
# 2. HÀM LẤY DỮ LIỆU TỪ PLC
# ==========================================
def get_plc_data():
    # Sử dụng timeout ngắn để web không bị treo nếu mất kết nối
    client = ModbusTcpClient(PLC_IP, port=PORT, timeout=1) 
    data = {"connected": False, "is_running": False, "temperature": 0}
    
    if client.connect():
        data["connected"] = True
        
        coil_result = client.read_coils(address=COIL_ADDRESS, count=1, slave=SLAVE_ID)
        if not coil_result.isError():
            data["is_running"] = coil_result.bits[0]
            
        reg_result = client.read_holding_registers(address=REGISTER_ADDRESS, count=1, slave=SLAVE_ID)
        if not reg_result.isError():
            data["temperature"] = reg_result.registers[0]
            
        client.close()
    return data

# ==========================================
# 3. GIAO DIỆN CẬP NHẬT TỰ ĐỘNG
# ==========================================
# Nút công tắc để bật/tắt giám sát
run_monitoring = st.toggle("🚀 Bật giám sát liên tục (Cập nhật mỗi 2 giây)")

# Tạo một "khung trống" để ghi đè dữ liệu mới vào, giúp web không bị nháy
placeholder = st.empty()

if run_monitoring:
    while True:
        # Lấy dữ liệu mới
        plc_data = get_plc_data()
        
        # Cập nhật thông tin vào khung trống
        with placeholder.container():
            if plc_data["connected"]:
                st.success(f"🟢 Đang nhận dữ liệu trực tiếp từ PLC ({PLC_IP})...")
                
                col1, col2 = st.columns(2)
                with col1:
                    trang_thai = "Đang Chạy" if plc_data["is_running"] else "Đã Dừng"
                    st.metric(label="Trạng thái máy", value=trang_thai)
                with col2:
                    st.metric(label="Nhiệt độ hiện tại", value=f"{plc_data['temperature']} °C")
            else:
                st.error(f"🔴 Mất kết nối! Đang thử kết nối lại tới {PLC_IP}...")
                
        # Dừng 2 giây trước khi vòng lặp chạy lại để tránh làm quá tải PLC
        time.sleep(2)
else:
    # Xóa dữ liệu cũ nếu tắt giám sát
    with placeholder.container():
        st.info("Hệ thống giám sát đang tạm dừng. Hãy bật công tắc phía trên để bắt đầu.")
