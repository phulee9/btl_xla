import pickle
import os
import json

print("=" * 80)
print("KIỂM TRA ĐƯỜNG DẪN VÀ FILE")
print("=" * 80)

# 1. Kiểm tra thư mục hiện tại
current_dir = os.getcwd()
print(f"\n1. Thư mục hiện tại: {current_dir}")

# 2. Kiểm tra thư mục images
images_dir = os.path.join(current_dir, 'images')
print(f"\n2. Thư mục images: {images_dir}")
if os.path.exists(images_dir):
    print("   ✓ Thư mục images TỒN TẠI")
    files = os.listdir(images_dir)
    print(f"   ✓ Số file trong thư mục: {len(files)}")
    if len(files) > 0:
        print(f"   ✓ Ví dụ 3 file đầu: {files[:3]}")
else:
    print("   ✗ Thư mục images KHÔNG TỒN TẠI!")

# 3. Đọc filenames.pkl
print("\n3. Kiểm tra filenames.pkl:")
try:
    with open('filenames.pkl', 'rb') as f:
        filenames = pickle.load(f)
    
    print(f"   ✓ Tổng số file trong pkl: {len(filenames)}")
    print(f"\n   Ví dụ 5 đường dẫn đầu tiên:")
    
    for i in range(min(5, len(filenames))):
        path = filenames[i]
        print(f"\n   [{i+1}] PKL path: {path}")
        print(f"       Type: {type(path)}")
        print(f"       Length: {len(path)} chars")
        
        # Thử nhiều cách để tìm file
        attempts = [
            path,  # Đường dẫn gốc
            os.path.join(current_dir, path),  # Thêm current dir
            path.replace('\\', '/'),  # Chuẩn hóa slash
            os.path.join(current_dir, path.replace('\\', '/')),
        ]
        
        found = False
        for attempt in attempts:
            if os.path.exists(attempt):
                print(f"       ✓ TÌM THẤY tại: {attempt}")
                found = True
                break
        
        if not found:
            print(f"       ✗ KHÔNG TÌM THẤY ở tất cả các vị trí!")
            print(f"       Đã thử:")
            for attempt in attempts:
                print(f"         - {attempt}")

    # 4. Kiểm tra đường dẫn đầu tiên chi tiết
    print("\n4. Phân tích chi tiết đường dẫn đầu tiên:")
    first_path = filenames[0]
    print(f"   Raw: {repr(first_path)}")
    print(f"   Stripped: {repr(first_path.strip())}")
    print(f"   Bytes: {first_path.encode('utf-8')}")
    
    # Kiểm tra các thành phần
    parts = first_path.replace('\\', '/').split('/')
    print(f"   Parts: {parts}")
    
except Exception as e:
    print(f"   ✗ Lỗi: {e}")

# 5. Tạo filenames.pkl MỚI từ thư mục images
print("\n5. TẠO FILENAMES.PKL MỚI:")
if os.path.exists(images_dir):
    print("   Đang quét thư mục images/...")
    
    new_filenames = []
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                # Tạo đường dẫn tương đối
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, current_dir)
                # Chuẩn hóa về forward slash
                relative_path = relative_path.replace('\\', '/')
                new_filenames.append(relative_path)
    
    print(f"   ✓ Tìm thấy {len(new_filenames)} ảnh")
    
    if len(new_filenames) > 0:
        print(f"\n   Ví dụ 5 đường dẫn mới:")
        for i in range(min(5, len(new_filenames))):
            print(f"   [{i+1}] {new_filenames[i]}")
        
        # Lưu backup
        with open('filenames_from_scan.pkl', 'wb') as f:
            pickle.dump(new_filenames, f)
        print(f"\n   ✓ Đã lưu: filenames_from_scan.pkl")
        print(f"   ! NẾU MUỐN SỬ DỤNG, chạy: copy filenames_from_scan.pkl filenames.pkl")
    else:
        print("   ✗ Không tìm thấy ảnh nào!")
else:
    print("   ✗ Không có thư mục images để quét!")

# 6. Tạo file JSON để test với Node.js
print("\n6. Tạo test.json cho Node.js:")
test_data = {
    "current_dir": current_dir,
    "images_dir": images_dir,
    "images_exists": os.path.exists(images_dir),
    "sample_paths": [filenames[i] for i in range(min(3, len(filenames)))] if 'filenames' in locals() else []
}

with open('test_paths.json', 'w', encoding='utf-8') as f:
    json.dump(test_data, f, indent=2, ensure_ascii=False)
print("   ✓ Đã tạo test_paths.json")

print("\n" + "=" * 80)
print("HOÀN TẤT KIỂM TRA")
print("=" * 80)