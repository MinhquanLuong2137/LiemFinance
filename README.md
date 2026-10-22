<div align="center">

  <img src="web/LiemFinance.ico" alt="LiemFinance Logo" width="100" height="100" />

  # 💰 LiemFinance - Personal Expense Tracker

  **Ứng dụng Quản lý Tài chính Cá nhân Tối giản, Siêu nhẹ & Hiệu quả**

  [![Python Version](https://img.shields.io/badge/Python-3.8%2B-80121D?style=for-the-badge&logo=python&logoColor=F2B236)](https://www.python.org/)
  [![Platform](https://img.shields.io/badge/Platform-Windows-80121D?style=for-the-badge&logo=windows&logoColor=F2B236)](#)
  [![License](https://img.shields.io/badge/License-MIT-80121D?style=for-the-badge&logo=open-source-initiative&logoColor=F2B236)](LICENSE)
  [![UI Design](https://img.shields.io/badge/UI-Burgundy%20%26%20Amber-F2B236?style=for-the-badge&labelColor=80121D)](#)

  <p align="center">
    <a href="#-tính-năng-nổi-bật">Tính năng</a> •
    <a href="#-hướng-dẫn-chạy-ứng-dụng">Cách sử dụng</a> •
    <a href="#-đóng-gói-exe">Đóng gói .EXE</a> •
    <a href="#-cấu-trúc-dự-án">Cấu trúc</a>
  </p>

</div>

> **Quản lý tài chính cá nhân gọn nhẹ, rõ ràng và luôn trong tầm kiểm soát.**

LiemFinance là ứng dụng theo dõi thu chi cá nhân, chạy trên Python và cung cấp
giao diện Web hiện đại với tông **đỏ mận** và **vàng hổ phách**. Dữ liệu được lưu
cục bộ trong file JSON; ứng dụng không cần dịch vụ đám mây hay thư viện Python
bên thứ ba. Trên Windows, bạn cũng có thể đóng gói ứng dụng thành một file `.exe`
duy nhất.

## ✨ Tính năng nổi bật

- 💸 **Quản lý thu và chi** — thêm, xem, chỉnh sửa và xóa giao dịch.
- 📊 **Báo cáo bốn mốc thời gian** — hôm nay, 7 ngày gần nhất, 1 tháng gần nhất
  và 1 năm gần nhất.
- 📈 **Biểu đồ cột ngang linh hoạt** — xem dòng tiền theo ngày, tuần, tháng, năm
  hoặc toàn bộ lịch sử; giao dịch mới nhất hiển thị trước.
- 🛒 **Top mặt hàng chi tiêu** — tổng hợp hạng mục theo hôm nay, tuần này, tháng
  này, năm nay hoặc toàn bộ thời gian.
- 🔎 **Tìm kiếm và lọc giao dịch** — tìm theo tên hoặc ghi chú, lọc theo loại và
  khoảng ngày, sắp xếp theo số tiền hoặc ngày.
- 🧾 **Lịch sử gọn gàng** — mặc định hiển thị 8 giao dịch mới nhất, có thể mở
  rộng danh sách và xem chi tiết giao dịch/mặt hàng.
- 🌐 **Đa ngôn ngữ** — chuyển đổi giữa Tiếng Việt và English.
- 🌓 **Giao diện Sáng/Tối** — lưu lựa chọn trên trình duyệt.
- 🧹 **Tự động dọn dữ liệu quá hạn** — sao lưu dữ liệu trước khi xóa giao dịch
  cũ hơn 365 ngày.
- 🖥️ **Chạy cục bộ, không phụ thuộc dịch vụ ngoài** — Web server dùng thư viện
  chuẩn Python và chỉ lắng nghe trên `127.0.0.1`.
- 📦 **Đóng gói Windows một file** — PyInstaller nhúng giao diện và icon vào
  file thực thi.

## 🧰 Công nghệ

- Python Standard Library (`http.server`, `json`, `threading`, ...)
- HTML, CSS và JavaScript thuần
- JSON làm định dạng lưu trữ
- PyInstaller để đóng gói ứng dụng Windows

## 📁 Cấu trúc dự án

```text
LiemFinance/
├── LiemFinance.py          # Nghiệp vụ, CLI, Web server và API
├── expenses.json           # Dữ liệu giao dịch cục bộ (tự tạo khi cần)
├── Run_LiemFinance.vbs     # Chạy ẩn từ mã nguồn và mở Web UI
├── Stop_LiemFinance.bat    # Dừng tiến trình LiemFinance chạy từ Python
├── LiemFinance.spec        # Cấu hình PyInstaller
├── web/
│   ├── index.html          # Khung giao diện
│   ├── styles.css          # Kiểu dáng, responsive và theme
│   ├── app.js              # Tương tác, biểu đồ và localization
│   └── LiemFinance.ico     # Icon ứng dụng và favicon
├── build/                  # Tệp trung gian do PyInstaller tạo
├── release/                # Thư mục phát hành (nếu được cấu hình)
└── dist/
    └── LiemFinance.exe     # Bản đóng gói một file (sau khi build)
```

> `expenses.json` nằm cạnh `LiemFinance.py` khi chạy từ mã nguồn và nằm cạnh
> file `.exe` khi chạy bản đóng gói. Dữ liệu không nằm trong thư mục tạm giải nén
> của PyInstaller.

## 🚀 Bắt đầu

### Yêu cầu

- Python 3.10 trở lên ( không cần nếu dùng cách 3 ).
- Windows nếu dùng các script `.vbs`, `.bat` hoặc file `.exe`.
- Trình duyệt web hiện đại.

### Cách 1: Chạy từ mã nguồn

Mở Terminal tại thư mục dự án và chạy:

```powershell
python .\LiemFinance.py
```

Ứng dụng khởi động Web server cục bộ và tự mở trình duyệt tại địa chỉ được in
ra (mặc định là `http://127.0.0.1:8765`).

Các tùy chọn hữu ích:

```powershell
# Chọn cổng khác
python .\LiemFinance.py --port 9000

# Khởi động server nhưng không tự mở trình duyệt
python .\LiemFinance.py --no-browser

# Dùng giao diện dòng lệnh
python .\LiemFinance.py --cli
```

**Chạy một cú nhấp trên Windows:** mở `Run_LiemFinance.vbs`. Script gọi
`pythonw.exe`, không hiện cửa sổ console và đặt thư mục làm việc đúng theo vị trí
dự án. Để dừng server chạy từ mã nguồn, mở `Stop_LiemFinance.bat`.

### Cách 2: Đóng gói thành một file `.exe`

Cài PyInstaller nếu máy chưa có:

```powershell
python -m pip install pyinstaller
```

Tạo file `.exe` chạy ẩn, kèm toàn bộ thư mục `web/` và icon:

```powershell
python -m PyInstaller --noconfirm --onefile --windowed `
  --name LiemFinance `
  --icon ".\web\LiemFinance.ico" `
  --add-data ".\web;web" `
  ".\LiemFinance.py"
```

Sau khi build thành công, chạy:

```text
dist\LiemFinance.exe
```

### Cách 3 (Khuyên dùng): Download bản Portable app tại "https://github.com/MinhquanLuong2137/LiemFinance/releases"

Ứng dụng sẽ tự mở trình duyệt. File `expenses.json` được đọc/ghi cạnh
`LiemFinance.exe`. Các tùy chọn `--port` và `--no-browser` cũng có thể truyền
vào file `.exe`, ví dụ:

```powershell
.\dist\LiemFinance.exe --port 9000 --no-browser
```

> Nếu cổng đã chọn đang được sử dụng, ứng dụng sẽ thử dùng cổng khả dụng khác.
> Hãy mở địa chỉ localhost mà ứng dụng hiển thị/mở trong trình duyệt.

## 📜 Nguyên tắc nghiệp vụ và dữ liệu

- **Tương thích ngược:** ứng dụng tiếp tục đọc các bản ghi cũ trong
  `expenses.json`. Trường cốt lõi gồm `id`, `type`, `name`, `amount`, `date` và
  `note`; các trường mở rộng như chi tiết mặt hàng được giữ nếu có.
- **Kiểm tra giao dịch:** tên phải có nội dung; số tiền phải hữu hạn và lớn hơn
  0; ngày phải đúng định dạng `YYYY-MM-DD` và không quá 365 ngày.
- **Chuẩn hóa tên:** `strip_accents()` loại dấu tiếng Việt, chuẩn hóa khoảng
  trắng và viết hoa kiểu tiêu đề để việc lưu trữ, tìm kiếm nhất quán.
- **Dọn dữ liệu quá hạn:** khi chạy Web UI, bản sao lưu JSON được tạo cạnh ứng
  dụng trước khi dữ liệu cũ hơn 365 ngày bị loại bỏ. Chế độ CLI có bước xác nhận
  và tùy chọn sao lưu.
- **Lưu trữ cục bộ:** giao dịch không được gửi tới dịch vụ bên ngoài. Các tùy
  chọn giao diện như ngôn ngữ và theme được lưu trong `localStorage` của trình
  duyệt.

## 🔌 API Web

Một số endpoint chính dành cho giao diện:

| Phương thức | Endpoint | Mô tả |
| --- | --- | --- |
| `GET`, `POST` | `/api/transactions` | Đọc hoặc thêm giao dịch |
| `PUT`, `DELETE` | `/api/transactions/{id}` | Cập nhật hoặc xóa giao dịch |
| `GET` | `/api/transactions/top-spending` | Tổng hợp chi tiêu theo hạng mục |
| `GET` | `/api/reports/dashboard` | Tổng hợp thu/chi theo các mốc báo cáo |
| `GET` | `/api/reports/chart` | Dữ liệu cho biểu đồ theo thời gian |
| `POST` | `/api/shutdown` | Dừng Web server hiện tại |

## 🛡️ Riêng tư và an toàn

Web server chỉ bind trên `127.0.0.1`, nghĩa là chỉ có thể truy cập từ máy đang
chạy ứng dụng theo cấu hình mặc định. Hãy sao lưu `expenses.json` định kỳ nếu
dữ liệu quan trọng; các file JSON bị `.gitignore` để tránh vô tình đưa dữ liệu
cá nhân vào Git.

## 🧯 Khắc phục sự cố

- **Không mở được trang:** kiểm tra ứng dụng còn chạy không và thử địa chỉ
  localhost được mở/in ra khi khởi động. Nếu cổng mặc định bận, ứng dụng có thể
  chuyển sang cổng khả dụng khác.
- **Không tìm thấy `pythonw.exe`:** cài Python và đảm bảo Python có trong `PATH`;
  hoặc chạy trực tiếp lệnh `python .\LiemFinance.py`.
- **Lỗi tài nguyên khi chạy file `.exe`:** build lại với tùy chọn
  `--add-data ".\web;web"` như hướng dẫn ở trên.
- **Dừng server:** dùng nút “Tắt ứng dụng” trên giao diện hoặc chạy
  `Stop_LiemFinance.bat` khi server được khởi chạy bằng Python từ mã nguồn.


---

<div align="center">

### 🛡️ LiemFinance

Được phát triển với sự hỗ trợ của **GitHub Copilot Agent** • Tối ưu hoá cho Windows OS

[📄 Xem Giấy phép (LICENSE)](LICENSE) • [🐛 Báo lỗi / Góp ý](https://github.com/) • [⭐ Trở về đầu trang](#-liemfinance---personal-expense-tracker)

<p align="center">
  <i>© 2026 LiemFinance. All rights reserved.</i>
</p>

</div>
