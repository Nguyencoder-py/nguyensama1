import cv2
import pyautogui
import time
import os
import numpy as np

# Hàm kiểm tra file tồn tại
def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} không tồn tại.")

# Hàm tìm kiếm và nhận diện hình ảnh trên màn hình
def find_image(image_path, threshold=0.8):
    check_file_exists(image_path)  # Kiểm tra file tồn tại
    screenshot = pyautogui.screenshot()  # Chụp màn hình
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # Chuyển sang BGR
    template = cv2.imread(image_path)  # Đọc hình ảnh cần tìm

    if template is None:
        raise ValueError("Không thể đọc được ảnh mẫu. Hãy kiểm tra đường dẫn hoặc định dạng ảnh.")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)  # Vị trí khớp với ngưỡng

    return loc  # Trả về tọa độ nếu tìm thấy hình ảnh

# Hàm kiểm tra hình ảnh hiện tại có giống với hình mẫu không
def is_image_matched(image_path, threshold=0.9):
    check_file_exists(image_path)  # Kiểm tra file tồn tại
    screenshot = pyautogui.screenshot()  # Chụp màn hình
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # Chuyển sang BGR
    template = cv2.imread(image_path)  # Đọc hình ảnh mẫu

    if template is None:
        raise ValueError("Không thể đọc được ảnh mẫu. Hãy kiểm tra đường dẫn hoặc định dạng ảnh.")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]  # Lấy giá trị khớp lớn nhất
    return max_val >= threshold  # Trả về True nếu khớp

# Hàm vuốt màn hình (swipe)
def swipe_device(start_x, start_y, end_x, end_y, duration=2000):
    os.system(f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}")

# Hàm nhấn nút "quay lại"
def press_back_button():
    os.system("adb shell input keyevent 4")  # Mã keyevent 4 là nút "quay lại"

# Hàm thực hiện vuốt liên tục và tìm hình ảnh
def swipe_until_image_found(start_x, start_y, end_x, end_y, target_image, check_image, swipe_duration=500, max_swipes=4):
    direction = 1  # Hướng vuốt ban đầu (1 = đúng hướng, -1 = ngược hướng)

    while True:
        for swipe_count in range(max_swipes):
            print(f"Vuốt lần thứ {swipe_count + 1} (Hướng: {'đúng' if direction == 1 else 'ngược'})...")

            # Vuốt màn hình theo hướng hiện tại
            swipe_device(
                start_x if direction == 1 else end_x,
                start_y,
                end_x if direction == 1 else start_x,
                end_y,
                swipe_duration,
            )
            time.sleep(1)  # Đợi một chút để ảnh chụp được cập nhật

            # Tìm kiếm hình ảnh mục tiêu
            loc = find_image(target_image)

            if len(loc[0]) > 0:  # Nếu tìm thấy hình ảnh
                print("Tìm thấy hình ảnh mục tiêu!")
                click_x = loc[1][0] + 10  # Offset
                click_y = loc[0][0] + 10
                os.system(f"adb shell input tap {click_x} {click_y}")

                # Kiểm tra hình ảnh hiện tại với hình kiểm tra
                time.sleep(2)  # Chờ màn hình cập nhật sau khi click
                if is_image_matched(check_image):
                    print("Hình ảnh kiểm tra trùng khớp. Kết thúc!")
                    return  # Thoát chương trình khi hoàn tất
                else:
                    print("Hình ảnh kiểm tra không trùng khớp. Quay lại và tiếp tục vuốt...")
                    press_back_button()  # Nhấn nút quay lại
            else:
                print("Hình ảnh mục tiêu không tìm thấy trong lần vuốt này.")

        # Sau khi vuốt 5 lần không thấy, đổi hướng
        print(f"Không tìm thấy hình ảnh sau {max_swipes} lần vuốt. Đổi hướng...")
        direction *= -1  # Đổi hướng vuốt

# Ví dụ sử dụng:
start_x, start_y = 1100, 200  # Tọa độ bắt đầu vuốt
end_x, end_y = 100, 200  # Tọa độ kết thúc vuốt
target_image = "4_5.png"  # Hình ảnh mục tiêu cần click
check_image = "check_image.png"  # Hình ảnh dùng để kiểm tra sau khi click

# Vuốt liên tục cho đến khi tìm thấy hình ảnh
swipe_until_image_found(start_x, start_y, end_x, end_y, target_image, check_image)
