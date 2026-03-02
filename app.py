import streamlit as st
import time
from pylogix import PLC

# Cấu hình trang
st.set_page_config(page_title="PLC Monitor (EtherNet/IP)", layout="wide")
st.title("🌐 Bảng Điều Khiển Giám Sát PLC (Giao thức EtherNet/IP)")

# ==========================================
# 1. GIAO DIỆN CÀI ĐẶT KẾT NỐI (SIDEBAR)
# ==========================================
st.sidebar.header("⚙️ Cài đặt Kết nối")

# Ô nhập IP, sử dụng IP 192.168.1.2 từ bức ảnh của bạn làm mặc định
user_ip = st.sidebar.text_input("Nhập địa chỉ IP của PLC:", value="192.168.1.2")

st.sidebar.markdown("---")
st.sidebar.subheader("Tên Biến (Tag Names)")
st.sidebar.caption("Nhập đúng tên biến đã khai báo trong AutoShop")

# Ô nhập tên Tag thay vì địa chỉ số
tag_running = st.sidebar.text_input("Tag Trạng thái chạy:", value="TrangThaiChay")
tag_temp = st.sidebar.text_input("Tag Nhiệt độ:", value="NhietDo")

run_monitoring = st.sidebar.toggle("🚀 Bắt đầu Kết nối & Giám sát")

# ==========================================
# 2. HÀM LẤY DỮ LIỆU TỪ PLC QUA ETHERNET/IP
# ==========================================
def get_eip_data(ip, tag_run, tag_temperature):
    data = {"connected": False, "is_running": False, "temperature": 0}
    
    # Khởi tạo kết nối với PLC qua thư viện pylogix
    with PLC() as comm:
        comm.IPAddress = ip
        comm.SocketTimeout = 2.0 # Thời gian chờ tối đa 2 giây
        
        # Đọc cùng lúc 2 Tag từ PLC
        # pylogix trả về một đối tượng chứa Status và Value
        ret_run = comm.Read(tag_run)
        ret_temp = comm.Read(tag_temperature)
        
        # Kiểm tra xem việc đọc cả 2 biến có thành công không
        if ret_run.Status == 'Success' and ret_temp.Status == 'Success':
            data["connected"] = True
            
            # Xử lý kiểu dữ liệu: đảm bảo trạng thái là True/False
            # và nhiệt độ là một con số
            data["is_running"] = bool(ret_run.Value)
            data["temperature"] = ret_temp.Value
            
    return data

# ==========================================
# 3. GIAO DIỆN HIỂN THỊ CHÍNH TỰ ĐỘNG
# ==========================================
placeholder = st.empty()

if run_monitoring:
    while True:
        # Gọi hàm lấy dữ liệu với các thông số người dùng vừa nhập
        plc_data = get_eip_data(user_ip, tag_running, tag_temp)
        
        with placeholder.container():
            if plc_data["connected"]:
                st.success(f"🟢 Đã kết nối thành công tới PLC tại {user_ip} (EtherNet/IP)")
                
                col1, col2 = st.columns(2)
                with col1:
                    trang_thai = "Đang Chạy" if plc_data["is_running"] else "Đã Dừng"
                    st.metric(label=f"Trạng thái ({tag_running})", value=trang_thai)
                with col2:
                    st.metric(label=f"Nhiệt độ ({tag_temp})", value=f"{plc_data['temperature']} °C")
            else:
                st.error(f"🔴 Không thể đọc dữ liệu từ {user_ip}!")
                st.info("💡 Mẹo kiểm tra:\n"
                        "1. Máy tính và PLC đã cùng mạng chưa (thử ping 192.168.1.2).\n"
                        "2. Tên Tag nhập trên web có gõ sai chính tả so với trong AutoShop không.")
                
        time.sleep(2)
else:
    with placeholder.container():
        st.info("Hệ thống đang chờ. Vui lòng nhập IP, Tên Tag và bật công tắc để bắt đầu.")
