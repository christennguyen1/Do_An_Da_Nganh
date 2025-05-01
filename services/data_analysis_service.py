# services/data_analysis_service.py
import json
import os
import numpy as np
from datetime import datetime, timedelta
import pytz
from middleware.websocket_manager import send_notification
from databases.databases import collection_sensor_data
import requests

url = "http://10.28.128.38:8000/api/ai-simulator/monitor/single"
headers = {
    "Content-Type": "application/json"
}

# Đường dẫn đến file JSON lưu trữ lịch sử
HISTORY_FILE = "data/sensor_history.json"

# Số lượng giá trị trong lịch sử để giữ lại
HISTORY_LENGTH = 60  # Tương đương với 5 giờ dữ liệu (5 phút/mẫu)

# Kích thước cửa sổ trượt để tính IQR (số mẫu gần nhất)
SLIDING_WINDOW_SIZE = 15

# Ngưỡng số lỗi trước khi gửi thông báo lỗi cảm biến
ERROR_THRESHOLD = 12  # Tương đương 1 giờ dữ liệu (12 x 5 phút)

# Ngưỡng số lỗi trước khi gửi thông báo bất thường
WARNING_THRESHOLD = 3  # Tương đương 15 phút dữ liệu (3 x 5 phút)

# Số lần xuất hiện giá trị mới liên tiếp để coi là "thay đổi môi trường thực"
NEW_NORMAL_THRESHOLD = 2  # Nhanh chóng thích nghi với thay đổi (10 phút)

# Biến lưu trữ các thông tin phân tích không lưu trong file JSON chính
_analysis_data = {
    'last_valid_values': {
        'temperature': None,
        'humidity': None,
        'lux': None,
        'soil': None
    },
    'error_counts': {
        'temperature': 0,
        'humidity': 0,
        'lux': 0,
        'soil': 0
    },
    'consistent_changes': {
        'temperature': 0,
        'humidity': 0,
        'lux': 0,
        'soil': 0
    },
    'last_changes': {
        'temperature': 0,
        'humidity': 0,
        'lux': 0,
        'soil': 0
    },
    'error_levels': {
        'temperature': 'none',  # 'none', 'warning', 'error'
        'humidity': 'none',
        'lux': 'none',
        'soil': 'none'
    },
    'environment_status': {
        'rapid_change': False,
        'last_change_time': None,
        'related_sensors': []
    },
    'watering_status': {
        'detected': False,
        'last_time': None,
        'consecutive_count': 0,
        'max_soil': 0
    },
    'consecutive_same_values': {
        'temperature': {'value': None, 'count': 0},
        'humidity': {'value': None, 'count': 0},
        'lux': {'value': None, 'count': 0},
        'soil': {'value': None, 'count': 0}
    }
}

# Ngưỡng thay đổi đột ngột cho từng loại cảm biến
RAPID_CHANGE_THRESHOLDS = {
    'temperature': 5.0,    # Thay đổi 5°C được coi là đột ngột
    'humidity': 15.0,      # Thay đổi 15% được coi là đột ngột
    'lux': 500.0,          # Thay đổi 500 lux được coi là đột ngột
    'soil': 20.0           # Thay đổi 15% được coi là đột ngột (tăng từ 10% lên 15%)
}

# Hệ số IQR tùy chỉnh cho từng loại cảm biến
IQR_FACTORS = {
    'temperature': 2.0,    # Nhiệt độ thay đổi chậm hơn, ít hơn
    'humidity': 2.5,       # Độ ẩm không khí có thể thay đổi nhanh (như khi mưa)
    'lux': 3.0,            # Ánh sáng thay đổi rất đột ngột (mây che, bật đèn)
    'soil': 4.0            # Tăng từ 2.0 lên 2.5 để thích ứng với tưới nước
}

def _ensure_directory_exists():
    """Đảm bảo thư mục lưu trữ tồn tại"""
    directory = os.path.dirname(HISTORY_FILE)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def load_sensor_history():
    """Tải dữ liệu lịch sử từ file JSON"""
    _ensure_directory_exists()
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as file:
                data = json.load(file)
                return data
        except Exception as e:
            print(f"Lỗi khi đọc file lịch sử: {e}")
    
    # Trả về cấu trúc mặc định nếu không đọc được file
    return []

def save_sensor_history(history_data):
    """Lưu dữ liệu lịch sử vào file JSON"""
    _ensure_directory_exists()
    
    try:
        with open(HISTORY_FILE, 'w') as file:
            json.dump(history_data, file, indent=2)
        return True
    except Exception as e:
        print(f"Lỗi khi lưu file lịch sử: {e}")
        return False

def _get_vietnam_time():
    """Lấy thời gian hiện tại theo múi giờ Việt Nam"""
    vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    vietnam_time = datetime.now(vietnam_tz)
    return vietnam_time

def _format_time(time):
    """Format thời gian theo định dạng chuẩn"""
    return time.strftime("%Y-%m-%dT%H:%M:%S")

def _get_sensor_values_from_history(history_data, sensor_type):
    """Trích xuất giá trị của một loại cảm biến từ dữ liệu lịch sử"""
    return [entry[sensor_type] for entry in history_data if sensor_type in entry and entry.get('is_valid', True)]

def _calculate_iqr_bounds(values, sensor_type):
    """
    Tính toán giới hạn IQR để phát hiện outlier, sử dụng hệ số riêng cho từng loại cảm biến
    
    Args:
        values: Danh sách giá trị lịch sử
        sensor_type: Loại cảm biến để áp dụng hệ số phù hợp
    
    Returns:
        tuple: (lower_bound, upper_bound)
    """
    if not values or len(values) < 4:
        # Nếu không đủ dữ liệu, trả về giới hạn rộng
        return (float('-inf'), float('inf'))
    
    # Chuyển thành numpy array để dễ xử lý
    data_array = np.array(values)
    
    # Tính Q1 (25th percentile) và Q3 (75th percentile)
    q1 = np.percentile(data_array, 25)
    q3 = np.percentile(data_array, 75)
    
    # Tính IQR
    iqr = q3 - q1
    
    # Lấy hệ số IQR tùy chỉnh dựa trên loại cảm biến
    k = IQR_FACTORS.get(sensor_type, 1.5)
    
    # Tính giới hạn trên và dưới
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    
    return (lower_bound, upper_bound)

def _is_significant_change(current_value, sensor_type, history_data):
    """
    Kiểm tra xem có phải là thay đổi đáng kể trong giá trị cảm biến không
    
    Args:
        current_value: Giá trị hiện tại
        sensor_type: Loại cảm biến
        history_data: Dữ liệu lịch sử
    
    Returns:
        bool: True nếu là thay đổi đáng kể
    """
    # Lấy giá trị hợp lệ gần nhất
    last_value = _analysis_data['last_valid_values'][sensor_type]
    
    if last_value is None:
        return False
    
    # Tính mức độ thay đổi
    change = abs(current_value - last_value)
    
    # Lấy ngưỡng thay đổi đột ngột cho loại cảm biến này
    threshold = RAPID_CHANGE_THRESHOLDS.get(sensor_type, 0)
    
    return change > threshold

def _is_watering_event(data, history_data):
    """
    Phát hiện sự kiện tưới nước dựa trên sự tăng đột biến của độ ẩm đất
    mà không có thay đổi đáng kể ở các cảm biến khác
    
    Args:
        data: Dữ liệu cảm biến hiện tại
        history_data: Dữ liệu lịch sử
    
    Returns:
        bool: True nếu phát hiện sự kiện tưới nước
    """
    # Kiểm tra nếu không có dữ liệu lịch sử
    if not history_data or len(history_data) < 1:
        return False
    
    # Kiểm tra nếu không có giá trị độ ẩm đất
    soil_value = data.get('soil')
    if soil_value is None:
        return False
    
    # Lấy giá trị độ ẩm đất gần nhất từ lịch sử
    last_soil = None
    for entry in reversed(history_data):
        if 'soil' in entry and entry.get('is_valid', True):
            last_soil = entry['soil']
            print("Last time:", last_soil)
            break
    
    if last_soil is None:
        return False
    
    # Tính mức tăng độ ẩm đất
    soil_increase = soil_value - last_soil
    
    # Điều kiện 1: Độ ẩm đất tăng đáng kể
    if soil_increase > RAPID_CHANGE_THRESHOLDS['soil']:
        # Điều kiện 2: Các cảm biến khác không thay đổi đáng kể
        other_sensors_stable = True
        
        for sensor_type in ['temperature', 'humidity', 'lux']:
            current_value = data.get(sensor_type)
            if current_value is None:
                continue
                
            # Lấy giá trị gần nhất của cảm biến này
            last_value = None
            for entry in reversed(history_data):
                if sensor_type in entry and entry.get('is_valid', True):
                    last_value = entry[sensor_type]
                    break
            
            if last_value is None:
                continue
                
            # Tính mức độ thay đổi
            change = abs(current_value - last_value)
            threshold = RAPID_CHANGE_THRESHOLDS[sensor_type] * 0.5  # Ngưỡng thấp hơn
            
            # Nếu cảm biến này thay đổi đáng kể, không phải sự kiện tưới nước
            if change > threshold:
                other_sensors_stable = False
                break
        
        # Nếu độ ẩm đất tăng đáng kể và các cảm biến khác ổn định
        if other_sensors_stable:
            # Cập nhật trạng thái tưới nước
            _analysis_data['watering_status']['detected'] = True
            _analysis_data['watering_status']['last_time'] = _format_time(_get_vietnam_time())
            _analysis_data['watering_status']['consecutive_count'] += 1
            _analysis_data['watering_status']['max_soil'] = max(_analysis_data['watering_status']['max_soil'], soil_value)
            return True
    
    # Reset trạng thái nếu không phát hiện tưới nước
    # Trong hàm _is_watering_event

    # Reset trạng thái nếu không phát hiện tưới nước
    if _analysis_data['watering_status']['consecutive_count'] > 0:
        # Nếu đang trong giai đoạn tưới nước (hoặc sau tưới nước)
        if soil_value > last_soil:
            # Độ ẩm đất vẫn đang tăng, tiếp tục trạng thái tưới nước
            _analysis_data['watering_status']['max_soil'] = max(_analysis_data['watering_status']['max_soil'], soil_value)
            return True
        elif abs(soil_value - last_soil) < RAPID_CHANGE_THRESHOLDS['soil'] * 0.5:
            # Độ ẩm đất tương đối ổn định, vẫn coi là đang/sau tưới nước
            return True
        elif soil_value < last_soil and soil_value > last_soil * 0.8:
            # Độ ẩm đất đang giảm nhưng vẫn cao (giảm tối đa 20% so với lần trước)
            # Vẫn coi là giai đoạn "sau tưới nước"
            return True
        else:
            # Giảm dần số đếm nếu độ ẩm giảm nhiều
            _analysis_data['watering_status']['consecutive_count'] -= 1
        
        if _analysis_data['watering_status']['consecutive_count'] == 0:
            if soil_value < last_soil:
                _analysis_data['watering_status']['detected'] = False
                _analysis_data['watering_status']['max_soil'] = 0
        
        return False

def _detect_rapid_environmental_change(data, history_data):
    """
    Phát hiện thay đổi môi trường đột ngột dựa trên sự thay đổi đồng thời của nhiều cảm biến
    
    Args:
        data: Dữ liệu cảm biến hiện tại
        history_data: Dữ liệu lịch sử
    
    Returns:
        bool: True nếu phát hiện thay đổi môi trường đột ngột
    """
    # Danh sách các cảm biến có thay đổi đáng kể
    changing_sensors = []
    
    # Kiểm tra từng loại cảm biến
    for sensor_type in ['temperature', 'humidity', 'lux', 'soil']:
        value = data.get(sensor_type)
        if value is None:
            continue
        
        # Nếu là thay đổi đáng kể, thêm vào danh sách
        if _is_significant_change(value, sensor_type, history_data):
            changing_sensors.append(sensor_type)
    
    # Nếu có từ 2 cảm biến trở lên thay đổi đồng thời, coi là thay đổi môi trường
    rapid_change = len(changing_sensors) >= 2
    
    # Cập nhật trạng thái môi trường
    if rapid_change:
        _analysis_data['environment_status']['rapid_change'] = True
        _analysis_data['environment_status']['last_change_time'] = _format_time(_get_vietnam_time())
        _analysis_data['environment_status']['related_sensors'] = changing_sensors
    elif len(changing_sensors) == 0:
        # Reset trạng thái nếu không còn thay đổi
        _analysis_data['environment_status']['rapid_change'] = False
    
    return rapid_change

def _is_outlier(value, sensor_type, history_data, watering_detected=False):
    """
    Kiểm tra một giá trị có phải là outlier không, có xét đến thay đổi môi trường đột ngột và tưới nước
    
    Args:
        value: Giá trị cần kiểm tra
        sensor_type: Loại cảm biến ('temperature', 'humidity', 'lux', 'soil')
        history_data: Dữ liệu lịch sử
        watering_detected: Có phát hiện sự kiện tưới nước không
    
    Returns:
        tuple: (is_outlier, is_critical) - is_outlier: có phải outlier không, is_critical: có vượt ngưỡng vật lý không
    """
    # Nếu không phải số, coi là outlier nghiêm trọng
    if value is None or not isinstance(value, (int, float)):
        return (True, True)
    
    # Kiểm tra nếu giá trị nằm ngoài phạm vi hợp lý của cảm biến (outlier nghiêm trọng)
    is_critical = False
    if sensor_type == 'temperature' and (value < -50 or value > 100):
        is_critical = True
    elif sensor_type == 'humidity' and (value < 0 or value > 100):
        is_critical = True
    elif sensor_type == 'lux' and value < 0:
        is_critical = True
    elif sensor_type == 'soil' and (value < 0 or value > 100):
        is_critical = True
    
    # Nếu là sự kiện tưới nước và cảm biến là độ ẩm đất, bỏ qua kiểm tra vượt ngưỡng
    # và chỉ kiểm tra outlier cơ bản
    if watering_detected and sensor_type == 'soil':
        # Nếu đã phát hiện là đang tưới nước, chỉ kiểm tra phạm vi vật lý hợp lệ
        # và bỏ qua các kiểm tra khác
        return (is_critical, is_critical)
    
    # Kiểm tra xem giá trị xuất hiện liên tiếp nhiều lần
    if sensor_type not in _analysis_data.get('consecutive_same_values', {}):
        # Khởi tạo nếu chưa có
        if 'consecutive_same_values' not in _analysis_data:
            _analysis_data['consecutive_same_values'] = {}
        _analysis_data['consecutive_same_values'][sensor_type] = {'value': None, 'count': 0}

    # Kiểm tra nếu giá trị xuất hiện liên tiếp
    current_value = _analysis_data['consecutive_same_values'][sensor_type]['value']
    if current_value is not None and abs(current_value - value) < 5:  # Dung sai nhỏ
        _analysis_data['consecutive_same_values'][sensor_type]['count'] += 1
    else:
        _analysis_data['consecutive_same_values'][sensor_type]['value'] = value
        _analysis_data['consecutive_same_values'][sensor_type]['count'] = 1

    # Nếu giá trị xuất hiện liên tiếp đủ số lần, coi là hợp lệ
    if _analysis_data['consecutive_same_values'][sensor_type]['count'] >= 3:
        return (False, is_critical)
    
    # Nếu đang trong trạng thái thay đổi môi trường đột ngột và cảm biến này liên quan
    if (_analysis_data['environment_status']['rapid_change'] and 
        sensor_type in _analysis_data['environment_status']['related_sensors']):
        
        # Kiểm tra xem giá trị này có nhất quán không
        if _analysis_data['consistent_changes'][sensor_type] >= NEW_NORMAL_THRESHOLD:
            # Đây là "trạng thái bình thường mới", không phải outlier
            return (False, is_critical)
        
        # Tăng biến đếm nhất quán nếu giá trị gần với lần trước
        last_change = _analysis_data['last_changes'][sensor_type]
        if abs(value - last_change) < RAPID_CHANGE_THRESHOLDS[sensor_type] * 0.5:
            _analysis_data['consistent_changes'][sensor_type] += 1
        else:
            # Reset biến đếm nếu giá trị không nhất quán
            _analysis_data['consistent_changes'][sensor_type] = 1
        
        # Ghi nhớ giá trị này cho lần so sánh tiếp theo
        _analysis_data['last_changes'][sensor_type] = value
        
        # Sử dụng ngưỡng IQR cao hơn trong thời gian thay đổi môi trường
        valid_values = _get_sensor_values_from_history(history_data, sensor_type)
        if valid_values:
            # Sử dụng cửa sổ trượt cho dữ liệu gần đây
            recent_values = valid_values[-min(SLIDING_WINDOW_SIZE, len(valid_values)):]
            lower_bound, upper_bound = _calculate_iqr_bounds(recent_values, sensor_type)
            
            # Áp dụng hệ số IQR cao hơn để tăng dung sai
            adjusted_lower = lower_bound - (upper_bound - lower_bound) * 0.5
            adjusted_upper = upper_bound + (upper_bound - lower_bound) * 0.5
            
            # Kiểm tra với ngưỡng điều chỉnh
            if value < adjusted_lower or value > adjusted_upper:
                return (True, is_critical)
        
        # Nếu chưa đạt ngưỡng nhất quán nhưng đang trong giai đoạn thay đổi, tạm thời chấp nhận
        return (False, is_critical)
    
    # Reset biến đếm nhất quán nếu không trong trạng thái thay đổi
    _analysis_data['consistent_changes'][sensor_type] = 0
    
    # Lấy giá trị hợp lệ từ lịch sử
    valid_values = _get_sensor_values_from_history(history_data, sensor_type)
    
    if valid_values:
        # Sử dụng cửa sổ trượt cho dữ liệu gần đây
        recent_values = valid_values[-min(SLIDING_WINDOW_SIZE, len(valid_values)):]
        
        # Tính giới hạn IQR dựa trên dữ liệu lịch sử gần đây
        lower_bound, upper_bound = _calculate_iqr_bounds(recent_values, sensor_type)
        
        # Kiểm tra nếu giá trị nằm ngoài giới hạn IQR
        if value < lower_bound or value > upper_bound:
            return (True, is_critical)
    
    return (False, is_critical)

def _linear_interpolation(sensor_type, history_data):
    """
    Thực hiện nội suy tuyến tính dựa trên dữ liệu lịch sử
    
    Args:
        sensor_type: Loại cảm biến ('temperature', 'humidity', 'lux', 'soil')
        history_data: Dữ liệu lịch sử
    
    Returns:
        float: Giá trị nội suy
    """
    # Nếu có giá trị hợp lệ gần đây, sử dụng giá trị đó
    if _analysis_data['last_valid_values'][sensor_type] is not None:
        return _analysis_data['last_valid_values'][sensor_type]
    
    # Lấy các giá trị hợp lệ từ lịch sử
    valid_values = _get_sensor_values_from_history(history_data, sensor_type)
    
    # Nếu có đủ dữ liệu lịch sử, tính trung bình
    if valid_values and len(valid_values) > 0:
        # Ưu tiên dữ liệu gần đây
        recent_values = valid_values[-min(10, len(valid_values)):]
        return np.mean(recent_values)
    
    # Giá trị mặc định nếu không thể nội suy
    default_values = {
        'temperature': 25.0,
        'humidity': 50.0,
        'lux': 500.0,
        'soil': 50.0
    }
    
    return default_values[sensor_type]

async def handle_sensor_data(user_id, data, notify_error=True):
    """
    Xử lý dữ liệu cảm biến, phát hiện lỗi và nội suy nếu cần
    
    Args:
        user_id: ID của người dùng (sở hữu cảm biến)
        data: Dữ liệu cảm biến (dict với các khóa: temperature, humidity, lux, soil)
        notify_error: True nếu muốn gửi thông báo khi phát hiện lỗi
    
    Returns:
        dict: Dữ liệu cảm biến sau khi xử lý
    """
    # Tải dữ liệu lịch sử
    history_data = load_sensor_history()
    
    vietnam_time = _get_vietnam_time()
    formatted_time = _format_time(vietnam_time)
    
    # Dictionary lưu trữ dữ liệu đã xử lý
    processed_data = {
        'timestamp': formatted_time,
        'is_valid': True
    }
    
    # Danh sách các loại cảm biến cần xử lý
    sensor_types = ['temperature', 'humidity', 'lux', 'soil']
    
    # Phát hiện sự kiện tưới nước
    watering_detected = _is_watering_event(data, history_data)
    
    # Phát hiện thay đổi môi trường đột ngột 
    # Phát hiện sự kiện tưới nước
    watering_detected = _is_watering_event(data, history_data)

    # Nếu không phát hiện tưới nước, mới kiểm tra thay đổi môi trường đột ngột
    if not watering_detected:
        environmental_change = _detect_rapid_environmental_change(data, history_data)
    else:
        # Nếu đã phát hiện tưới nước, không cần kiểm tra thay đổi môi trường
        environmental_change = False
    
    has_errors = False
    errors = []
    events = []
    
    # Thêm thông tin sự kiện tưới nước vào processed_data nếu phát hiện
    if watering_detected:
        events.append("watering")
        processed_data['event'] = "watering"
        processed_data['watering_info'] = {
            'detected': True,
            'consecutive_count': _analysis_data['watering_status']['consecutive_count'],
            'last_time': _analysis_data['watering_status']['last_time']
        }
    
    # Thêm thông tin thay đổi môi trường vào processed_data nếu phát hiện
    if environmental_change:
        events.append("environmental_change")
        if 'event' not in processed_data:
            processed_data['event'] = "environmental_change"
        elif processed_data['event'] == "watering":
            processed_data['event'] = "multiple"
        
        processed_data['environmental_change'] = {
            'detected': True,
            'affected_sensors': _analysis_data['environment_status']['related_sensors'],
            'last_time': _analysis_data['environment_status']['last_change_time']
        }
    
    for sensor_type in sensor_types:
        value = data.get(sensor_type)
        
        # Kiểm tra xem giá trị có phải là outlier không, có xét đến thay đổi môi trường và tưới nước
        is_outlier, is_critical = _is_outlier(value, sensor_type, history_data, watering_detected)
        
        if is_outlier:
            # Tăng biến đếm lỗi
            _analysis_data['error_counts'][sensor_type] += 1
            
            # Thực hiện nội suy tuyến tính
            interpolated_value = _linear_interpolation(sensor_type, history_data)
            
            # Ghi nhận lỗi
            processed_data[sensor_type] = interpolated_value
            has_errors = True
            errors.append({
                'sensor_type': sensor_type,
                'raw_value': value,
                'interpolated_value': interpolated_value,
                'error_count': _analysis_data['error_counts'][sensor_type],
                'is_critical': is_critical
            })

            print(f"Phát hiện giá trị bất thường của cảm biến {sensor_type}: {value}")
            
            # Cập nhật mức độ lỗi
            error_level = 'error' if is_critical else 'warning'
            _analysis_data['error_levels'][sensor_type] = error_level
            
            # Thông báo mức độ Warning nếu đạt ngưỡng Warning
            if (notify_error and 
                _analysis_data['error_counts'][sensor_type] >= WARNING_THRESHOLD and 
                _analysis_data['error_counts'][sensor_type] < ERROR_THRESHOLD and
                not _analysis_data['error_levels'][sensor_type] == 'error'):
                
                if not (watering_detected and sensor_type == 'soil') and not environmental_change:
                    print(f"Gửi thông báo bất thường cảm biến {sensor_type}")
                    # await send_notification(
                    #     user_id=user_id,
                    #     message=f"Cảnh báo: Cảm biến {sensor_type} có giá trị bất thường ({_analysis_data['error_counts'][sensor_type]} lần liên tiếp)",
                    #     notification_type="warning",
                    #     data={
                    #         'sensor_type': sensor_type,
                    #         'error_count': _analysis_data['error_counts'][sensor_type],
                    #         'timestamp': formatted_time,
                    #         'during_environmental_change': environmental_change,
                    #         'during_watering': watering_detected and sensor_type == 'soil',
                    #         'events': events
                    #     }
                    # )
                    data = {
                        "user_id": 1,
                        "device": "Cảm biến nhiệt độ A1",
                        "description": "Nhiệt độ cao bất thường",
                        "severity": "Cao", 
                        "issue": "Nhiệt độ quá cao",
                        "recommendation": "Kiểm tra lại cảm biến",
                        "message": "Cảnh báo: Phát hiện độ ẩm cao bất thường."
                        }

                    response = requests.post(url, json=data, headers=headers)

                    # In ra kết quả
                    if response.status_code == 200:
                        print("✅ Relay created:", response.json())
                    else:
                        print("❌ Error:", response.status_code, response.text)

            
            # Thông báo lỗi nếu đạt ngưỡng Error hoặc là lỗi nghiêm trọng
            if ((notify_error and _analysis_data['error_counts'][sensor_type] >= ERROR_THRESHOLD) or 
                (is_critical and _analysis_data['error_counts'][sensor_type] >= WARNING_THRESHOLD)):
                
                print(f"Gửi thông báo lỗi cảm biến {sensor_type}")
                # await send_notification(
                #     user_id=user_id,
                #     message=f"Lỗi: Cảm biến {sensor_type} không hoạt động đúng ({_analysis_data['error_counts'][sensor_type]} lần liên tiếp)",
                #     notification_type="error",
                #     data={
                #         'sensor_type': sensor_type,
                #         'error_count': _analysis_data['error_counts'][sensor_type],
                #         'timestamp': formatted_time,
                #         'is_critical': is_critical,
                #         'during_environmental_change': environmental_change,
                #         'during_watering': watering_detected and sensor_type == 'soil',
                #         'events': events
                #     }
                # )

                data = {
                        "user_id": 1,
                        "device": "Cảm biến nhiệt độ A10",
                        "description": "Nhiệt độ cao bất thường",
                        "severity": "Cao", 
                        "issue": "Nhiệt độ quá cao",
                        "recommendation": "Kiểm tra lại cảm biến",
                        "message": f"Lỗi: Cảm biến {sensor_type} không hoạt động đúng ({_analysis_data['error_counts'][sensor_type]} lần liên tiếp)"
                        }

                response = requests.post(url, json=data, headers=headers)

                # In ra kết quả
                if response.status_code == 200:
                    print("✅ Relay created:", response.json())
                else:
                    print("❌ Error:", response.status_code, response.text)
                # Reset biến đếm lỗi sau khi gửi thông báo
                _analysis_data['error_counts'][sensor_type] = 0
        else:
            # Nếu giá trị hợp lệ
            processed_data[sensor_type] = value
            
            # Cập nhật giá trị hợp lệ gần nhất
            _analysis_data['last_valid_values'][sensor_type] = value
            
            # Reset biến đếm lỗi và mức độ lỗi
            _analysis_data['error_counts'][sensor_type] = 0
            _analysis_data['error_levels'][sensor_type] = 'none'
    
    # Thêm thông tin chi tiết về lỗi vào dữ liệu
    if has_errors:
        processed_data['errors_detail'] = {
            'count': len(errors),
            'sensors': [error['sensor_type'] for error in errors],
            'values': {error['sensor_type']: error['raw_value'] for error in errors},
            'interpolated': {error['sensor_type']: error['interpolated_value'] for error in errors},
            'critical': [error['sensor_type'] for error in errors if error['is_critical']]
        }
    
        # Cập nhật trạng thái hợp lệ của dữ liệu
    processed_data['is_valid'] = not has_errors
    
    # Thêm dữ liệu mới vào lịch sử
    history_data.append(processed_data)
    
    # Giới hạn kích thước lịch sử
    if len(history_data) > HISTORY_LENGTH:
        history_data = history_data[-HISTORY_LENGTH:]
    
    # Lưu lịch sử đã cập nhật
    save_sensor_history(history_data)
    
    # Lưu dữ liệu đã xử lý vào MongoDB
    # collection_sensor_data.insert_one(processed_data)
    
    return processed_data

async def detect_anomalies(user_id):
    """
    Phát hiện bất thường trong dữ liệu cảm biến và gửi thông báo
    
    Args:
        user_id: ID của người dùng
    
    Returns:
        dict: Kết quả phát hiện bất thường
    """
    # Tải dữ liệu lịch sử
    history_data = load_sensor_history()
    
    # Danh sách loại cảm biến
    sensor_types = ['temperature', 'humidity', 'lux', 'soil']
    anomalies = []
    
    # Kiểm tra nếu đang trong giai đoạn thay đổi môi trường đột ngột
    environmental_change = _analysis_data['environment_status']['rapid_change']
    
    # Kiểm tra nếu đang trong giai đoạn tưới nước
    watering_detected = _analysis_data['watering_status']['detected']
    
    for sensor_type in sensor_types:
        # Kiểm tra số lần lỗi
        error_count = _analysis_data['error_counts'][sensor_type]
        if error_count >= WARNING_THRESHOLD:  # Ngưỡng cảnh báo
            anomaly = {
                'sensor_type': sensor_type,
                'type': 'error_accumulation',
                'level': 'warning' if error_count < ERROR_THRESHOLD else 'error',
                'message': f"Cảm biến {sensor_type} đang tích lũy lỗi ({error_count}/{ERROR_THRESHOLD})",
                'data': {
                    'error_count': error_count,
                    'warning_threshold': WARNING_THRESHOLD,
                    'error_threshold': ERROR_THRESHOLD,
                    'during_environmental_change': environmental_change,
                    'during_watering': watering_detected and sensor_type == 'soil'
                }
            }
            anomalies.append(anomaly)
        
        # Lấy các giá trị hợp lệ từ lịch sử
        valid_values = _get_sensor_values_from_history(history_data, sensor_type)
        
        # Kiểm tra xu hướng bất thường dựa trên dữ liệu lịch sử
        if len(valid_values) >= 6:  # Cần ít nhất 6 điểm dữ liệu (30 phút)
            recent_values = valid_values[-6:]  # 6 giá trị gần nhất
            
            # Tính độ dốc của đường thẳng hồi quy
            x = np.arange(len(recent_values))
            try:
                slope, _ = np.polyfit(x, recent_values, 1)
                
                # Ngưỡng độ dốc để xác định xu hướng (điều chỉnh theo từng loại cảm biến)
                slope_thresholds = {
                    'temperature': 0.8,  # Độ C/mẫu (giảm từ 1.0)
                    'humidity': 4.0,     # %/mẫu (giảm từ 5.0)
                    'lux': 150.0,        # lux/mẫu (giảm từ 200.0)
                    'soil': 8.0          # %/mẫu (giảm từ 5.0)
                }
                
                # Nếu đang trong giai đoạn thay đổi môi trường, tăng ngưỡng lên
                if environmental_change and sensor_type in _analysis_data['environment_status']['related_sensors']:
                    slope_thresholds[sensor_type] *= 3.0
                
                # Nếu đang trong giai đoạn tưới nước và là cảm biến đất, tăng ngưỡng lên
                if watering_detected and sensor_type == 'soil':
                    slope_thresholds['soil'] *= 4.0
                
                if abs(slope) > slope_thresholds[sensor_type]:
                    trend_type = "tăng nhanh" if slope > 0 else "giảm nhanh"
                    anomaly = {
                        'sensor_type': sensor_type,
                        'type': 'abnormal_trend',
                        'level': 'warning',
                        'message': f"Dữ liệu cảm biến {sensor_type} có xu hướng {trend_type} bất thường",
                        'data': {
                            'slope': slope,
                            'threshold': slope_thresholds[sensor_type],
                            'recent_values': recent_values,
                            'during_environmental_change': environmental_change,
                            'during_watering': watering_detected and sensor_type == 'soil'
                        }
                    }
                    anomalies.append(anomaly)
                    
                    # Chỉ gửi thông báo xu hướng bất thường nếu không trong giai đoạn thay đổi môi trường
                    # hoặc tưới nước, hoặc nếu trend quá mạnh kể cả đang trong các sự kiện đó
                    notify_trend = False
                    
                    if ((not environmental_change and not (watering_detected and sensor_type == 'soil')) or
                        abs(slope) > slope_thresholds[sensor_type] * 2):
                        notify_trend = True
                    
                    if notify_trend:
                        await send_notification(
                            user_id=user_id,
                            message=anomaly['message'],
                            notification_type="warning",
                            data={
                                'sensor_type': sensor_type,
                                'trend': trend_type,
                                'slope': float(slope),
                                'during_environmental_change': environmental_change,
                                'during_watering': watering_detected and sensor_type == 'soil'
                            }
                        )
            except Exception as e:
                print(f"Lỗi khi phân tích xu hướng cảm biến {sensor_type}: {e}")
    
    return {
        'user_id': user_id,
        'timestamp': _format_time(_get_vietnam_time()),
        'anomaly_count': len(anomalies),
        'anomalies': anomalies,
        'environmental_change': {
            'detected': environmental_change,
            'time': _analysis_data['environment_status']['last_change_time'],
            'affected_sensors': _analysis_data['environment_status']['related_sensors']
        },
        'watering': {
            'detected': watering_detected,
            'time': _analysis_data['watering_status']['last_time']
        }
    }