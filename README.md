# Port Inspector & Killer (Windows)

Hướng dẫn bằng tiếng Việt để build file `.exe` từ script Python `port_killer.py` và cách sử dụng.

Mục lục
- Giới thiệu
- Yêu cầu
- Cách build file .exe (PyInstaller)
- Cách chạy và sử dụng
- Ghi chú an toàn

## Giới thiệu

`port_killer.py` là một công cụ CLI nhỏ cho Windows giúp:

- Liệt kê tiến trình đang dùng một port TCP/UDP cụ thể (ví dụ 3306).
- Cho phép tắt (kill) một tiến trình hoặc tất cả các tiến trình đang chiếm port đó.

Không cần thư viện ngoài — script dùng `netstat`, `tasklist`, và `taskkill` có sẵn trên Windows.

## Yêu cầu

- Windows (Windows 10/11) với Python 3.7+ (bản test dùng Python 3.12).
- pip (để cài PyInstaller khi cần).
- Quyền Administrator để kill một số tiến trình hệ thống (nếu cần).


## Cài đặt Python & thư viện (chi tiết)

Nếu bạn chưa cài Python hoặc muốn dùng môi trường ảo (khuyến nghị), làm theo các bước dưới.

1. Cài Python

- Cách đơn giản: tải installer từ https://www.python.org/downloads/ và cài (chọn "Add Python to PATH").
- Hoặc cài từ Microsoft Store / package manager tùy môi trường.

2. Tạo và kích hoạt virtual environment (khuyến nghị)

```cmd
cd /d E:\[toolkit]
python -m venv .venv
.venv\Scripts\activate
```

Trên PowerShell (nếu dùng PowerShell):

```powershell
cd /d E:\[toolkit]
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Cập nhật pip và cài PyInstaller

```cmd
python -m pip install --upgrade pip
pip install pyinstaller
```

4. (Tuỳ chọn) Tạo file `requirements.txt` để dễ tái tạo môi trường

```text
pyinstaller
```

Sau đó cài từ file:

```cmd
pip install -r requirements.txt
```

Ghi chú:
- Nếu bạn không muốn dùng virtualenv, có thể cài trực tiếp bằng `pip install pyinstaller` trên Python toàn cục.
- Quyền Administrator chỉ cần khi bạn muốn kill tiến trình mà tài khoản hiện tại không có quyền.

## Cách build file .exe

1. Mở `cmd.exe` (nên chạy với quyền Administrator nếu bạn muốn exe có thể kill tiến trình cần quyền cao).
2. Chuyển thư mục tới nơi chứa `port_killer.py` (ví dụ `E:\[toolkit]`):

```cmd
cd /d E:\[toolkit]
```

3. Cài PyInstaller nếu chưa có:

```cmd
pip install pyinstaller
```

4. Build thành single-file executable:

```cmd
python -m PyInstaller --onefile --console --clean --noconfirm port_killer.py
```

Sau khi chạy xong, file exe sẽ nằm ở thư mục `dist` (ví dụ `E:\[toolkit]\dist\port_killer.exe`).

## Cách chạy & sử dụng

- Chạy file exe (hoặc script Python trực tiếp):

```cmd
cd /d E:\[toolkit]\dist
port_killer.exe
# hoặc chạy script trực tiếp
python E:\[toolkit]\port_killer.py
```

- Khi chạy, chương trình sẽ yêu cầu nhập port:

- Nhập số port (ví dụ `3306`) → chương trình hiển thị danh sách tiến trình đang dùng port đó.
- Sau khi hiển thị, bạn có thể nhập:
  - số (index) → để kill tiến trình tương ứng (sẽ hỏi xác nhận trước khi kill)
  - `a` → kill tất cả tiến trình được liệt kê (hỏi xác nhận từng PID)
  - `r` → refresh: script sẽ xóa toàn bộ console và hiển thị lại danh sách (gọn gàng)
  - `b` → quay lại bước nhập port

- Ở prompt nhập port, bạn có thể nhập `q` để thoát chương trình.

Ví dụ nhanh:

```text
Port inspector + killer (Windows). No external deps.
Enter port number (or 'q' to quit): 3306
# nếu có tiến trình sẽ hiển thị danh sách... sau đó nhập 'r' để refresh
```

## Ghi chú an toàn

- Khi dùng `taskkill /F` để tắt tiến trình, có thể làm mất dữ liệu nếu tiến trình đó đang xử lý công việc.
- Không tắt các tiến trình hệ thống quan trọng. Nếu không chắc, kiểm tra tên tiến trình trước khi kill.
- Nếu gặp lỗi khi kill (Access denied), chạy cmd.exe với quyền Administrator.

## Muốn tùy chỉnh hoặc tự động hóa

- Muốn có chế độ không tương tác (flags CLI như `--port 3306 --kill-all --yes`) tôi có thể thêm và build lại exe.
- Muốn file `.msi` hoặc trình cài đặt, hoặc phiên bản PowerShell, tôi cũng có thể giúp.

---

Nếu cần tôi sẽ thêm phần hướng dẫn dùng flag, hoặc build script batch tự động. Bạn muốn tôi làm tiếp gì không?
