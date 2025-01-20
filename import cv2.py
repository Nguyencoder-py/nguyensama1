import cv2
import time
import os
import numpy as np
import subprocess

# Hàm kiểm tra file tồn tại
def check_file_exists(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} không tồn tại.")

# Hàm lấy ảnh chụp màn hình từ thiết bị qua ADB
def get_device_screenshot():
    # Chụp ảnh màn hình từ thiết bị Android qua ADB
    result = subprocess.run(["adb", "shell", "screencap", "-p", "/sdcard/screen.png"], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception("Không thể chụp màn hình từ thiết bị qua ADB.")

    # Sao chép ảnh vào máy tính
    subprocess.run(["adb", "pull", "/sdcard/screen.png", "screen.png"])
    time.sleep(1)  # Đảm bảo ảnh đã được sao chép hoàn toàn

    # Đọc ảnh từ file
    return cv2.imread("screen.png")

# Hàm tìm kiếm và nhận diện hình ảnh trên màn hình
def find_image(image_path, threshold=0.8):
    check_file_exists(image_path)  # Kiểm tra file tồn tại
    screenshot = get_device_screenshot()  # Lấy ảnh từ thiết bị
    template = cv2.imread(image_path)  # Đọc hình ảnh cần tìm

    if template is None:
        raise ValueError("Không thể đọc được ảnh mẫu. Hãy kiểm tra đường dẫn hoặc định dạng ảnh.")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)  # Vị trí khớp với ngưỡng

    return loc  # Trả về tọa độ nếu tìm thấy hình ảnh

# Hàm kiểm tra hình ảnh hiện tại có giống với hình mẫu không
def is_image_matched(image_path, threshold=0.9):
    check_file_exists(image_path)  # Kiểm tra file tồn tại
    screenshot = get_device_screenshot()  # Lấy ảnh từ thiết bị
    template = cv2.imread(image_path)  # Đọc hình ảnh mẫu

    if template is None:
        raise ValueError("Không thể đọc được ảnh mẫu. Hãy kiểm tra đường dẫn hoặc định dạng ảnh.")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    max_val = cv2.minMaxLoc(result)[1]  # Lấy giá trị khớp lớn nhất
    return max_val >= threshold  # Trả về True nếu khớp

# Hàm vuốt màn hình (swipe)
def swipe_device(start_x, start_y, end_x, end_y, duration=3000):
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
            time.sleep(2)  # Đợi một chút để ảnh chụp được cập nhật

            # Tìm kiếm hình ảnh mục tiêu
            loc = find_image(target_image)

            if len(loc[0]) > 0:  # Nếu tìm thấy hình ảnh
                print(f"Tìm thấy hình ảnh mục tiêu tại vị trí: ({loc[1][0]}, {loc[0][0]})")
                time.sleep(1)
                click_x = loc[1][0]  # Lấy tọa độ đầu tiên
                click_y = loc[0][0]  # Lấy tọa độ đầu tiên
                
                print(f"Nhấn vào tọa độ ({click_x}, {click_y})")
                # Thực thi lệnh ADB để click vào tọa độ đã tìm
                subprocess.run(["adb", "shell", "input", "tap", str(click_x), str(click_y)])
                time.sleep(2)  # Đợi sau khi click

                # Kiểm tra lại hình ảnh kiểm tra
                if is_image_matched(check_image):
                    print("Hình ảnh kiểm tra trùng khớp. Kết thúc!")
                    return  # Kết thúc khi hoàn tất
                else:
                    print("Hình ảnh kiểm tra không trùng khớp. Quay lại và tiếp tục vuốt...")
                    press_back_button()  # Nhấn quay lại
            else:
                print("Không tìm thấy hình ảnh mục tiêu trong lần vuốt này.")

        # Sau khi vuốt 4 lần không thấy, đổi hướng
        print(f"Không tìm thấy hình ảnh sau {max_swipes} lần vuốt. Đổi hướng...")
        direction *= -1  # Đổi hướng vuốt

# Ví dụ sử dụng:
start_x, start_y = 1100, 200  # Tọa độ bắt đầu vuốt
end_x, end_y = 200, 200  # Tọa độ kết thúc vuốt
target_image = "4_5.png"  # Hình ảnh mục tiêu cần click
check_image = "check_image.png"  # Hình ảnh dùng để kiểm tra sau khi click

# Vuốt liên tục cho đến khi tìm thấy hình ảnh
swipe_until_image_found(start_x, start_y, end_x, end_y, target_image, check_image)
