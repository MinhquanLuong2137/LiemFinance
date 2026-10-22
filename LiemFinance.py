"""
================================================================================
LIEMFINANCE - HƯỚNG DẪN DÀNH CHO AI DUY TRÌ & PHÁT TRIỂN CODE (AI CONTEXT)
================================================================================

1. CẤU TRÚC DỰ ÁN & CÁCH CHẠY:
   - `LiemFinance.py` chứa nghiệp vụ, CLI, HTTP server và API; `expenses.json` nằm cạnh file này.
   - Frontend thuần HTML/CSS/JS và icon nằm trong `web/`:
     `web/index.html`, `web/styles.css`, `web/app.js`, `web/LiemFinance.ico`.
   - Chạy Web UI mặc định bằng `python LiemFinance.py`; dùng `--port` để đổi cổng,
     `--no-browser` để không tự mở trình duyệt, hoặc `--cli` để dùng CLI.
   - Web server chỉ bind vào `127.0.0.1`; không thêm thư viện Python/JavaScript bên thứ ba.

2. TƯƠNG THÍCH DỮ LIỆU & SCHEMA - BẮT BUỘC:
   - `expenses.json` là danh sách các giao dịch, phải tiếp tục đọc được dữ liệu cũ.
   - Không đổi tên hoặc xóa các trường cốt lõi:
     `id`, `type`, `name`, `amount`, `date`, `note`.
   - Schema lịch sử: v1.0 có `id/name/amount/date`; v1.1 thêm `note`;
     v1.2 thêm `type` (`expense` hoặc `income`).
   - `load_data()` bù mặc định `type="expense"` và `note=""` cho bản ghi cũ.
     Trường mở rộng, ví dụ `items`, là tùy chọn; khi đọc phải dùng `dict.get()`.
   - Không làm mất trường mở rộng đã có trên bản ghi khi cập nhật giao dịch.

3. NGHIỆP VỤ CỐT LÕI:
   - `strip_accents()` chuyển văn bản tiếng Việt thành không dấu, chuẩn hóa khoảng trắng
     và Title Case; dùng nhất quán khi lưu tên và khi tìm kiếm.
   - Chỉ chấp nhận giao dịch có tên, số tiền hữu hạn lớn hơn 0 và ngày `YYYY-MM-DD`
     không cũ hơn `DAYS_RETENTION` (365 ngày).
   - Tự dọn bản ghi quá hạn. CLI cảnh báo và hỏi có xuất backup hay không; Web tự tạo
     backup JSON cạnh ứng dụng trước khi dọn. Không bỏ qua hoặc âm thầm nuốt lỗi đọc/ghi.
   - Import chỉ nhận giao dịch hợp lệ trong giới hạn 365 ngày.

4. API WEB:
   - CRUD: `GET/POST /api/transactions` và `PUT/DELETE /api/transactions/{id}`.
   - `GET /api/transactions` hỗ trợ `q` (tên/ghi chú, không dấu), `type`,
     `period` (`all`, `day`, `week`, `month`, `custom`), `date`, `from`, `to`,
     và `sort` (`date_desc`, `amount_asc`, `amount_desc`).
   - `GET /api/transactions/top-spending` tổng hợp chi tiêu theo tên hạng mục;
     `period` nhận `today`, `this_week`, `this_month`, `this_year` hoặc `all`.
     Chi tiết giao dịch gốc được giữ kèm để hiển thị.
   - `GET /api/reports/dashboard` trả tổng thu/chi theo các khoảng lăn 1, 7, 30,
     365 ngày (tính cả hôm nay) và chuỗi tổng theo ngày của 30 ngày gần nhất.
   - `GET /api/reports/chart?period=day|week|month|year|all` trả dữ liệu biểu đồ
     đã gom theo ngày, tuần, tháng, năm hoặc toàn bộ lịch sử.
   - `POST /api/shutdown` xác nhận yêu cầu tắt server; gọi `shutdown()` từ timer
     riêng để phản hồi HTTP hoàn tất trước khi server dừng.
   - Giữ response JSON và thông báo lỗi HTTP rõ ràng; không tin cậy đầu vào từ client.

5. DASHBOARD & GIAO DIỆN:
   - Báo cáo bốn khoảng thời gian lấy từ API dashboard; biểu đồ cột ngang lấy từ
     `/api/reports/chart`. Không nhân đôi phép tính thống kê trong UI.
   - Danh sách hỗ trợ tìm kiếm, lọc ngày, sắp xếp, Top chi tiêu và accordion;
     mặc định chỉ hiện 8 dòng đầu, nút mở rộng cho phép xem toàn bộ kết quả.
     Tùy chọn chi tiết món hàng mở ngay các giao dịch có dữ liệu mặt hàng.
     Các trường món hàng là tùy chọn, không phải trường bắt buộc của schema cốt lõi.
   - Giữ UI responsive, màu chủ đạo burgundy `#80121D` và amber `#F2B236`;
     biểu đồ dùng HTML/CSS/SVG thuần, không thêm thư viện JS cồng kềnh.

6. ĐÓNG GÓI:
   - Phải tiếp tục build được PyInstaller `--onefile`, chỉ dùng thư viện chuẩn Python.
   - `DATA_FILE` luôn nằm cạnh script/exe; tài nguyên giao diện lấy từ `web/`
     trong source và từ bundle (`sys._MEIPASS`) trong bản đóng gói.
================================================================================
"""









import os
import json
import csv
import argparse
import math
import sys
import threading
import unicodedata
import uuid
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(APP_DIR, "expenses.json")
DAYS_RETENTION = 365
DATA_LOCK = threading.RLock()
MAX_REQUEST_BODY = 1024 * 1024


class RequestValidationError(ValueError):
    pass


def resource_path(relative_path):
    """Resolve bundled resources in source runs and PyInstaller onefile builds."""
    bundle_dir = getattr(sys, "_MEIPASS", APP_DIR)
    return os.path.join(bundle_dir, relative_path)


def strip_accents(text):
    """Chuẩn hóa chuỗi tiếng Việt có dấu thành không dấu."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return " ".join(text.split()).title()


def get_cutoff_date():
    return (datetime.now() - timedelta(days=DAYS_RETENTION)).date()


def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Dữ liệu expenses.json phải là một danh sách.")
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("expenses.json có bản ghi không hợp lệ.")
        item.setdefault("type", "expense")
        item.setdefault("note", "")
    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def format_vnd(amount):
    return f"{int(amount):,}".replace(",", ".") + " ₫"


def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def print_transaction_table(records):
    """In danh sách giao dịch ra bảng terminal."""
    if not records:
        print("\nKhông có dữ liệu phù hợp.")
        return
    print("\n" + "-" * 95)
    print(f"{'STT':<4} | {'Loại':<5} | {'ID':<14} | {'Ngày':<10} | {'Mục / Nguồn':<20} | {'Số tiền':<16} | {'Ghi chú'}")
    print("-" * 95)
    for idx, r in enumerate(records, 1):
        t_type = "[THU]" if r.get("type") == "income" else "[CHI]"
        note = r.get("note", "")
        print(f"{idx:<4} | {t_type:<5} | {r['id']:<14} | {r['date']:<10} | {r['name']:<20} | {format_vnd(r['amount']):<16} | {note}")
    print("-" * 95)


# --- DỌN DẸP TỰ ĐỘNG & SAO LƯU ---

def check_and_prune():
    data = load_data()
    cutoff = get_cutoff_date()
    expired = [d for d in data if parse_date(d["date"]) and parse_date(d["date"]) < cutoff]

    if expired:
        print("\n" + "=" * 60)
        print(f"⚠️  CẢNH BÁO: Phát hiện {len(expired)} bản ghi cũ hơn 365 ngày chuẩn bị bị xóa!")
        print("=" * 60)
        ans = input("Bạn có muốn xuất bản sao lưu (JSON) trước khi dọn dẹp? (y/n): ").strip().lower()

        if ans == "y":
            backup_name = f"finance_backup_{int(datetime.now().timestamp())}.json"
            with open(backup_name, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Đã sao lưu dữ liệu vào file: {backup_name}")

        active_data = [d for d in data if parse_date(d["date"]) and parse_date(d["date"]) >= cutoff]
        save_data(active_data)
        print("🧹 Đã dọn dẹp các mục cũ hơn 1 năm thành công.\n")


def prune_expired_for_web():
    """Back up the existing file before automatically pruning expired entries."""
    data = load_data()
    cutoff = get_cutoff_date()
    expired = [item for item in data if parse_date(item.get("date", "")) and
               parse_date(item.get("date", "")) < cutoff]
    if not expired:
        return

    timestamp = int(datetime.now().timestamp() * 1000)
    backup_name = os.path.join(APP_DIR, f"finance_backup_{timestamp}.json")
    with open(backup_name, "w", encoding="utf-8") as backup_file:
        json.dump(data, backup_file, ensure_ascii=False, indent=2)

    active_data = [
        item for item in data
        if parse_date(item.get("date", "")) and parse_date(item.get("date", "")) >= cutoff
    ]
    save_data(active_data)
    display_path = backup_name.encode("ascii", "backslashreplace").decode("ascii")
    print(
        f"WARNING: Saved a backup of {len(expired)} expired transactions to "
        f"{display_path} before pruning."
    )


def validate_transaction(payload, existing=None):
    if not isinstance(payload, dict):
        raise ValueError("Nội dung giao dịch phải là một đối tượng JSON.")

    record = dict(existing or {})
    tx_type = payload.get("type", record.get("type", "expense"))
    if tx_type not in ("expense", "income"):
        raise ValueError("Loại giao dịch chỉ có thể là expense hoặc income.")

    name = payload.get("name", record.get("name", ""))
    if not isinstance(name, str) or not name.strip():
        raise ValueError("Tên giao dịch không được để trống.")
    name = strip_accents(name)

    amount = payload.get("amount", record.get("amount"))
    if isinstance(amount, bool):
        raise ValueError("Số tiền không hợp lệ.")
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Số tiền không hợp lệ.")
    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Số tiền phải lớn hơn 0.")

    date_value = payload.get("date", record.get("date", ""))
    if not isinstance(date_value, str):
        raise ValueError("Ngày giao dịch không hợp lệ.")
    parsed_date = parse_date(date_value)
    if not parsed_date:
        raise ValueError("Ngày giao dịch phải theo định dạng YYYY-MM-DD.")
    if parsed_date < get_cutoff_date():
        raise ValueError("Không thể lưu giao dịch cũ hơn 365 ngày.")

    note = payload.get("note", record.get("note", ""))
    if not isinstance(note, str):
        raise ValueError("Ghi chú phải là văn bản.")

    record.update({
        "type": tx_type,
        "name": name,
        "amount": amount,
        "date": date_value,
        "note": note.strip(),
    })
    return record


class FinanceRequestHandler(BaseHTTPRequestHandler):
    server_version = "LiemFinance/1.0"

    def _send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, relative_path, content_type):
        try:
            with open(resource_path(relative_path), "rb") as asset:
                body = asset.read()
        except OSError:
            self._send_json(404, {"error": "Không tìm thấy tài nguyên giao diện."})
            return
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Content-Length không hợp lệ.")
        if content_length <= 0 or content_length > MAX_REQUEST_BODY:
            raise ValueError("Kích thước nội dung yêu cầu không hợp lệ.")
        try:
            payload = json.loads(self.rfile.read(content_length).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Nội dung yêu cầu phải là JSON hợp lệ.")
        if not isinstance(payload, dict):
            raise ValueError("Nội dung yêu cầu phải là một đối tượng JSON.")
        return payload

    def _transaction_id(self):
        prefix = "/api/transactions/"
        if not self.path.startswith(prefix):
            return None
        value = unquote(urlparse(self.path).path[len(prefix):]).strip("/")
        return value or None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send_file("web/index.html", "text/html; charset=utf-8")
            return
        if path == "/styles.css":
            self._send_file("web/styles.css", "text/css; charset=utf-8")
            return
        if path == "/app.js":
            self._send_file("web/app.js", "text/javascript; charset=utf-8")
            return
        if path == "/LiemFinance.ico":
            self._send_file("web/LiemFinance.ico", "image/x-icon")
            return
        if path == "/api/reports/dashboard":
            try:
                with DATA_LOCK:
                    data = load_data()
                today = datetime.now().date()
                periods = {
                    "today": today,
                    "last_7_days": today - timedelta(days=6),
                    "last_30_days": today - timedelta(days=29),
                    "last_365_days": today - timedelta(days=364),
                }
                totals = {
                    key: {"income": 0.0, "expense": 0.0, "start": start.isoformat(),
                          "end": today.isoformat()}
                    for key, start in periods.items()
                }
                daily_totals = {}
                for offset in range(29, -1, -1):
                    day = today - timedelta(days=offset)
                    daily_totals[day.isoformat()] = {"income": 0.0, "expense": 0.0}

                for item in data:
                    item_date = parse_date(item.get("date", ""))
                    if not item_date or item_date > today:
                        continue
                    amount = float(item.get("amount", 0))
                    tx_type = "income" if item.get("type", "expense") == "income" else "expense"
                    for key, start in periods.items():
                        if start <= item_date <= today:
                            totals[key][tx_type] += amount
                    daily = daily_totals.get(item_date.isoformat())
                    if daily is not None:
                        daily[tx_type] += amount

                report = {
                    "periods": totals,
                    "daily": [
                        {"date": date_value, **amounts}
                        for date_value, amounts in daily_totals.items()
                    ],
                }
                self._send_json(200, report)
            except (OSError, json.JSONDecodeError, ValueError) as error:
                self._send_json(500, {"error": f"Không thể tạo báo cáo thu chi: {error}"})
            return
        if path == "/api/reports/chart":
            try:
                query = parse_qs(urlparse(self.path).query)
                period = query.get("period", ["day"])[0]
                if period not in ("day", "week", "month", "year", "all"):
                    raise RequestValidationError("Mốc thời gian biểu đồ không hợp lệ.")

                with DATA_LOCK:
                    data = load_data()
                today = datetime.now().date()
                dated_records = []
                for item in data:
                    item_date = parse_date(item.get("date", ""))
                    if item_date and item_date <= today:
                        dated_records.append((item_date, item))

                if period == "day":
                    start = today - timedelta(days=29)
                    bucket_dates = [start + timedelta(days=offset) for offset in range(30)]
                    bucket_for = lambda item_date: item_date
                elif period == "week":
                    current_week = today - timedelta(days=today.weekday())
                    start = current_week - timedelta(weeks=11)
                    bucket_dates = [start + timedelta(weeks=offset) for offset in range(12)]
                    bucket_for = lambda item_date: item_date - timedelta(days=item_date.weekday())
                elif period == "month":
                    current_month = today.replace(day=1)
                    bucket_dates = []
                    year, month = current_month.year, current_month.month
                    for _ in range(12):
                        bucket_dates.append(datetime(year, month, 1).date())
                        month -= 1
                        if month == 0:
                            year -= 1
                            month = 12
                    bucket_dates.reverse()
                    bucket_for = lambda item_date: item_date.replace(day=1)
                elif period == "year":
                    first_year = min((entry_date.year for entry_date, _ in dated_records), default=today.year)
                    bucket_dates = [datetime(year, 1, 1).date()
                                    for year in range(first_year, today.year + 1)]
                    bucket_for = lambda item_date: item_date.replace(month=1, day=1)
                else:
                    start = min((entry_date for entry_date, _ in dated_records), default=today)
                    bucket_dates = [
                        start + timedelta(days=offset)
                        for offset in range((today - start).days + 1)
                    ]
                    bucket_for = lambda item_date: item_date

                buckets = {
                    bucket_date: {"income": 0.0, "expense": 0.0}
                    for bucket_date in bucket_dates
                }
                for item_date, item in dated_records:
                    key = bucket_for(item_date)
                    if key not in buckets:
                        continue
                    tx_type = "income" if item.get("type", "expense") == "income" else "expense"
                    buckets[key][tx_type] += float(item.get("amount", 0))

                self._send_json(200, {
                    "period": period,
                    "points": [
                        {"date": bucket_date.isoformat(), **buckets[bucket_date]}
                        for bucket_date in bucket_dates
                    ],
                })
            except RequestValidationError as error:
                self._send_json(400, {"error": str(error)})
            except (OSError, json.JSONDecodeError, ValueError) as error:
                self._send_json(500, {"error": f"Không thể tạo dữ liệu biểu đồ: {error}"})
            return
        if path not in ("/api/transactions", "/api/transactions/top-spending"):
            self._send_json(404, {"error": "Không tìm thấy đường dẫn."})
            return

        query = parse_qs(urlparse(self.path).query)
        try:
            keyword = strip_accents(query.get("q", [""])[0]).lower()
            tx_type = query.get("type", ["all"])[0]
            period = query.get("period", ["all"])[0]
            sort = query.get("sort", ["date_desc"])[0]
            if tx_type not in ("all", "expense", "income"):
                raise RequestValidationError("Bộ lọc loại giao dịch không hợp lệ.")
            valid_periods = (
                ("all", "today", "this_week", "this_month", "this_year")
                if path == "/api/transactions/top-spending"
                else ("all", "day", "week", "month", "custom")
            )
            if period not in valid_periods:
                raise RequestValidationError("Bộ lọc thời gian không hợp lệ.")
            if sort not in ("date_desc", "amount_asc", "amount_desc"):
                raise RequestValidationError("Thứ tự sắp xếp không hợp lệ.")

            today = datetime.now().date()
            start_date = end_date = None
            if period == "today":
                start_date = end_date = today
            elif period == "this_week":
                start_date = today - timedelta(days=today.weekday())
                end_date = today
            elif period == "this_month":
                start_date = today.replace(day=1)
                end_date = today
            elif period == "this_year":
                start_date = today.replace(month=1, day=1)
                end_date = today
            elif period == "day":
                start_date = end_date = parse_date(query.get("date", [""])[0])
                if not start_date:
                    raise RequestValidationError("Ngày lọc phải theo định dạng YYYY-MM-DD.")
            elif period == "week":
                start_date = today - timedelta(days=today.weekday())
                end_date = start_date + timedelta(days=6)
            elif period == "month":
                start_date = today.replace(day=1)
                next_month = (start_date.replace(day=28) + timedelta(days=4)).replace(day=1)
                end_date = next_month - timedelta(days=1)
            elif period == "custom":
                start_date = parse_date(query.get("from", [""])[0])
                end_date = parse_date(query.get("to", [""])[0])
                if not start_date or not end_date:
                    raise RequestValidationError("Khoảng thời gian cần có ngày bắt đầu và kết thúc hợp lệ.")
                if start_date > end_date:
                    raise RequestValidationError("Ngày bắt đầu không thể sau ngày kết thúc.")

            with DATA_LOCK:
                data = load_data()
            filtered = []
            for item in data:
                item_date = parse_date(item.get("date", ""))
                if start_date and (not item_date or item_date < start_date):
                    continue
                if end_date and (not item_date or item_date > end_date):
                    continue
                if tx_type != "all" and item.get("type", "expense") != tx_type:
                    continue
                if keyword and keyword not in strip_accents(item.get("name", "")).lower() \
                        and keyword not in strip_accents(item.get("note", "")).lower():
                    continue
                filtered.append(item)

            if path == "/api/transactions/top-spending":
                categories = {}
                for item in filtered:
                    if item.get("type", "expense") != "expense":
                        continue
                    name = item.get("name", "")
                    key = strip_accents(name).lower()
                    category = categories.setdefault(key, {
                        "name": name, "amount": 0, "count": 0, "transactions": []
                    })
                    category["amount"] += float(item.get("amount", 0))
                    category["count"] += 1
                    category["transactions"].append(item)
                results = sorted(
                    categories.values(),
                    key=lambda category: (-category["amount"], category["name"].lower())
                )
            else:
                if sort == "amount_asc":
                    filtered.sort(key=lambda item: (float(item.get("amount", 0)), item.get("date", "")))
                elif sort == "amount_desc":
                    filtered.sort(key=lambda item: (-float(item.get("amount", 0)), item.get("date", "")))
                else:
                    filtered.sort(key=lambda item: (item.get("date", ""), str(item.get("id", ""))), reverse=True)
                results = filtered
            self._send_json(200, results)
        except RequestValidationError as error:
            self._send_json(400, {"error": str(error)})
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self._send_json(500, {"error": f"Không thể đọc dữ liệu giao dịch: {error}"})

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/shutdown":
            self._send_json(200, {"status": "shutting_down"})
            self.wfile.flush()
            threading.Timer(0.2, self.server.shutdown).start()
            return
        if path != "/api/transactions":
            self._send_json(404, {"error": "Không tìm thấy đường dẫn."})
            return
        try:
            payload = self._read_json()
            record = validate_transaction(payload)
            with DATA_LOCK:
                data = load_data()
                record["id"] = uuid.uuid4().hex
                data.append(record)
                save_data(data)
            self._send_json(201, record)
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
        except (OSError, json.JSONDecodeError) as error:
            self._send_json(500, {"error": f"Không thể lưu giao dịch: {error}"})

    def do_PUT(self):
        target_id = self._transaction_id()
        if target_id is None:
            self._send_json(404, {"error": "Không tìm thấy giao dịch."})
            return
        try:
            payload = self._read_json()
            with DATA_LOCK:
                data = load_data()
                index = next(
                    (i for i, item in enumerate(data) if str(item.get("id", "")) == target_id),
                    None
                )
                if index is None:
                    self._send_json(404, {"error": "Không tìm thấy giao dịch."})
                    return
                updated = validate_transaction(payload, data[index])
                updated["id"] = data[index]["id"]
                data[index] = updated
                save_data(data)
            self._send_json(200, updated)
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
        except (OSError, json.JSONDecodeError) as error:
            self._send_json(500, {"error": f"Không thể cập nhật giao dịch: {error}"})

    def do_DELETE(self):
        target_id = self._transaction_id()
        if target_id is None:
            self._send_json(404, {"error": "Không tìm thấy giao dịch."})
            return
        try:
            with DATA_LOCK:
                data = load_data()
                index = next(
                    (i for i, item in enumerate(data) if str(item.get("id", "")) == target_id),
                    None
                )
                if index is None:
                    self._send_json(404, {"error": "Không tìm thấy giao dịch."})
                    return
                deleted = data.pop(index)
                save_data(data)
            self._send_json(200, {"deleted": deleted.get("id")})
        except (OSError, json.JSONDecodeError, ValueError) as error:
            self._send_json(500, {"error": f"Không thể xóa giao dịch: {error}"})


def run_web_server(port=8765, open_browser=True):
    prune_expired_for_web()
    server = ThreadingHTTPServer(("127.0.0.1", port), FinanceRequestHandler)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"LiemFinance Web đang chạy tại {url} (nhấn Ctrl+C để dừng).")
    if open_browser:
        threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐang dừng LiemFinance Web...")
    finally:
        server.server_close()


# --- THÊM GIAO DỊCH MỚI (THU / CHI) ---

def add_transaction():
    print("\n--- CHỌN LOẠI GIAO DỊCH ---")
    print("1. Tiền ra (Chi tiêu)")
    print("2. Tiền vào (Thu nhập / Tiền nhận)")
    t_choice = input("Lựa chọn (1/2) [Mặc định: 1]: ").strip()
    tx_type = "income" if t_choice == "2" else "expense"
    type_label = "TIỀN VÀO (THU NHẬP)" if tx_type == "income" else "TIỀN RA (CHI TIÊU)"

    data = load_data()
    # Gợi ý danh sách dựa theo loại giao dịch
    filtered_names = [d["name"] for d in data if d.get("type", "expense") == tx_type]
    unique_names = list(dict.fromkeys(filtered_names))

    print(f"\n--- THÊM GIAO DỊCH: {type_label} ---")
    recent = []
    if unique_names:
        recent = unique_names[-8:]
        print("Gợi ý từ các mục đã nhập trước đó:")
        for idx, name in enumerate(recent, 1):
            print(f" [{idx}] {name}")

    name_input = input("Tên mục/Nguồn tiền (nhập tên mới hoặc số gợi ý): ").strip()
    if not name_input:
        print("❌ Tên mục không được để trống.")
        return

    normalized_input = strip_accents(name_input)

    if name_input.isdigit():
        choice_idx = int(name_input)
        if 1 <= choice_idx <= len(recent):
            item_name = recent[choice_idx - 1]
        else:
            item_name = normalized_input
    else:
        matched_name = next(
            (name for name in unique_names if strip_accents(name).lower() == normalized_input.lower()),
            None
        )
        item_name = matched_name if matched_name else normalized_input

    amount_str = input("Số tiền (VND): ").strip().replace(".", "").replace(",", "")
    try:
        amount = float(amount_str)
        if amount <= 0:
            raise ValueError
    except ValueError:
        print("❌ Số tiền không hợp lệ.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    date_input = input(f"Ngày giao dịch (YYYY-MM-DD) [Mặc định: {today_str}]: ").strip()
    date_str = date_input if date_input else today_str

    entry_date = parse_date(date_str)
    if not entry_date:
        print("❌ Định dạng ngày không hợp lệ.")
        return

    if entry_date < get_cutoff_date():
        print("❌ Không thể lưu giao dịch cũ hơn 1 năm.")
        return

    note_input = input("Ghi chú (nhấn Enter để bỏ qua): ").strip()

    record = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "type": tx_type,
        "name": item_name,
        "amount": amount,
        "date": date_str,
        "note": note_input
    }

    data.append(record)
    save_data(data)
    print(f"✅ Đã lưu [{type_label}]: \"{item_name}\" - {format_vnd(amount)} ({date_str})")


# --- TÌM KIẾM GIAO DỊCH ---

def search_transactions():
    data = load_data()
    if not data:
        print("\nChưa có bản ghi giao dịch nào.")
        return

    print("\n--- TÌM KIẾM GIAO DỊCH ---")
    print("1. Tìm theo ngày cụ thể (YYYY-MM-DD)")
    print("2. Tìm theo tuần (nhập 1 ngày trong tuần)")
    print("3. Tìm theo tháng cụ thể (YYYY-MM)")
    print("4. Tra cứu theo tên mục / nguồn tiền")
    choice = input("Lựa chọn (1-4): ").strip()

    filtered = []
    title = ""

    if choice == "1":
        d_str = input("Nhập ngày cần tìm (YYYY-MM-DD): ").strip()
        target_d = parse_date(d_str)
        if not target_d:
            print("❌ Ngày không đúng định dạng.")
            return
        filtered = [d for d in data if parse_date(d["date"]) == target_d]
        title = f"NGÀY {target_d}"

    elif choice == "2":
        d_str = input("Nhập 1 ngày bất kỳ trong tuần (YYYY-MM-DD): ").strip()
        target_d = parse_date(d_str)
        if not target_d:
            print("❌ Ngày không đúng định dạng.")
            return
        monday = target_d - timedelta(days=target_d.weekday())
        sunday = monday + timedelta(days=6)
        filtered = [d for d in data if parse_date(d["date"]) and monday <= parse_date(d["date"]) <= sunday]
        title = f"TUẦN TỪ {monday} ĐẾN {sunday}"

    elif choice == "3":
        m_str = input("Nhập tháng và năm (YYYY-MM): ").strip()
        try:
            datetime.strptime(m_str, "%Y-%m")
        except ValueError:
            print("❌ Định dạng tháng không hợp lệ (ví dụ đúng: 2026-05).")
            return
        filtered = [d for d in data if d["date"].startswith(m_str)]
        title = f"THÁNG {m_str}"

    elif choice == "4":
        keyword = input("Nhập tên mục / nguồn tiền muốn tra cứu: ").strip()
        clean_kw = strip_accents(keyword).lower()
        filtered = [d for d in data if clean_kw in strip_accents(d["name"]).lower()]
        title = f"MỤC LIÊN QUAN ĐẾN '{strip_accents(keyword)}'"

    else:
        print("Lựa chọn không hợp lệ.")
        return

    print_transaction_table(filtered)
    if filtered:
        inc = sum(d["amount"] for d in filtered if d.get("type") == "income")
        exp = sum(d["amount"] for d in filtered if d.get("type", "expense") == "expense")
        print(f"💵 TIỀN VÀO (THU): {format_vnd(inc)}")
        print(f"💸 TIỀN RA (CHI):  {format_vnd(exp)}")
        print(f"📈 SỐ DƯ RÒNG:     {format_vnd(inc - exp)} ({len(filtered)} giao dịch)\n")


# --- SỬA VÀ XÓA GIAO DỊCH ---

def edit_or_delete_transaction():
    data = load_data()
    if not data:
        print("\nChưa có bản ghi nào.")
        return

    print("\n1. Sửa thông tin giao dịch")
    print("2. Xóa giao dịch")
    action = input("Chọn thao tác (1/2): ").strip()

    if action not in ["1", "2"]:
        print("Lựa chọn không hợp lệ.")
        return

    recent = data[-10:]
    print("\n--- CÁC GIAO DỊCH GẦN NHẤT ---")
    print_transaction_table(recent)

    target_id = input("Nhập ID giao dịch cần thao tác: ").strip()
    idx_found = next((i for i, d in enumerate(data) if d["id"] == target_id), None)

    if idx_found is None:
        print("❌ Không tìm thấy bản ghi với ID trên.")
        return

    item = data[idx_found]

    if action == "2":
        confirm = input(f"Bạn có chắc muốn xóa '{item['name']}' ({format_vnd(item['amount'])})? (y/n): ").strip().lower()
        if confirm == "y":
            data.pop(idx_found)
            save_data(data)
            print("✅ Đã xóa giao dịch thành công.")
        else:
            print("Đã hủy thao tác xóa.")

    elif action == "1":
        print(f"\n--- SỬA BẢN GHI (Nhấn Enter để giữ nguyên giá trị cũ) ---")
        
        # Sửa loại
        cur_type = item.get("type", "expense")
        new_type_inp = input(f"Loại giao dịch (1. Chi tiêu | 2. Thu nhập) [Hiện tại: {'Thu' if cur_type == 'income' else 'Chi'}]: ").strip()
        if new_type_inp == "1":
            item["type"] = "expense"
        elif new_type_inp == "2":
            item["type"] = "income"

        # Sửa tên
        new_name = input(f"Tên mới [{item['name']}]: ").strip()
        if new_name:
            item["name"] = strip_accents(new_name)

        # Sửa số tiền
        new_amt_str = input(f"Số tiền mới [{int(item['amount'])}]: ").strip().replace(".", "").replace(",", "")
        if new_amt_str:
            try:
                amt = float(new_amt_str)
                if amt > 0:
                    item["amount"] = amt
            except ValueError:
                print("⚠️  Số tiền không hợp lệ, giữ nguyên giá trị cũ.")

        # Sửa ngày
        new_date = input(f"Ngày mới (YYYY-MM-DD) [{item['date']}]: ").strip()
        if new_date:
            parsed_d = parse_date(new_date)
            if parsed_d and parsed_d >= get_cutoff_date():
                item["date"] = new_date
            else:
                print("⚠️  Ngày không hợp lệ hoặc cũ hơn 1 năm, giữ nguyên ngày cũ.")

        # Sửa ghi chú
        current_note = item.get("note", "")
        new_note = input(f"Ghi chú mới [{current_note}]: ").strip()
        if new_note:
            item["note"] = new_note

        save_data(data)
        print("✅ Đã cập nhật giao dịch thành công.")


# --- THỐNG KÊ, BIỂU ĐỒ & DASHBOARD ---

def view_dashboard():
    data = load_data()
    if not data:
        print("\nChưa có bản ghi giao dịch nào.")
        return

    print("\n--- BỘ LỌC THỜI GIAN ---")
    print("1. Hôm nay (Day)")
    print("2. 7 ngày qua (Week)")
    print("3. 30 ngày qua (Month)")
    print("4. Toàn bộ (trong vòng 1 năm)")
    choice = input("Lựa chọn (1-4): ").strip()

    today = datetime.now().date()
    if choice == "1":
        filtered = [d for d in data if parse_date(d["date"]) == today]
    elif choice == "2":
        start_date = today - timedelta(days=7)
        filtered = [d for d in data if parse_date(d["date"]) and parse_date(d["date"]) >= start_date]
    elif choice == "3":
        start_date = today - timedelta(days=30)
        filtered = [d for d in data if parse_date(d["date"]) and parse_date(d["date"]) >= start_date]
    else:
        filtered = data[:]

    incomes = [d for d in filtered if d.get("type") == "income"]
    expenses = [d for d in filtered if d.get("type", "expense") == "expense"]

    total_income = sum(d["amount"] for d in incomes)
    total_expense = sum(d["amount"] for d in expenses)
    balance = total_income - total_expense

    print("\n" + "=" * 60)
    print("📊 BÁO CÁO THU - CHI TỔNG QUAN")
    print("=" * 60)
    print(f" 💵 Tổng tiền vào (Thu nhập):  {format_vnd(total_income):>18} ({len(incomes)} món)")
    print(f" 💸 Tổng tiền ra  (Chi tiêu):  {format_vnd(total_expense):>18} ({len(expenses)} món)")
    print(f" 📈 Số dư còn lại:             {format_vnd(balance):>18}")
    print("=" * 60)

    if not filtered:
        return

    # Biểu đồ xu hướng chi tiêu theo ngày
    if expenses:
        print("\n📉 XU HƯỚNG CHI TIÊU THEO NGÀY:")
        date_summary = {}
        for d in expenses:
            date_summary[d["date"]] = date_summary.get(d["date"], 0) + d["amount"]

        sorted_dates = sorted(date_summary.keys())
        max_amount = max(date_summary.values())

        for d in sorted_dates:
            amt = date_summary[d]
            bar_len = int((amt / max_amount) * 25) if max_amount > 0 else 0
            bar = "█" * bar_len
            print(f"{d} | {bar:<25} | {format_vnd(amt)}")

    # Top 10 mặt hàng chi tiêu nhiều nhất
    if expenses:
        print("\n🏆 TOP 10 MẶT HÀNG CHI TIÊU NHIỀU NHẤT:")
        item_totals = {}
        for d in expenses:
            item_totals[d["name"]] = item_totals.get(d["name"], 0) + d["amount"]

        sorted_items = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_items[:10]

        for idx, (item_name, total_amt) in enumerate(top_10, 1):
            print(f"{idx:>2}. {item_name:<25} : {format_vnd(total_amt)}")

        if len(sorted_items) > 10:
            see_all = input(f"\nXem toàn bộ danh sách {len(sorted_items)} mặt hàng chi tiêu? (y/n): ").strip().lower()
            if see_all == "y":
                print("\n--- TOÀN BỘ DANH SÁCH MẶT HÀNG CHI TIÊU ---")
                for idx, (item_name, total_amt) in enumerate(sorted_items, 1):
                    print(f"{idx:>3}. {item_name:<25} : {format_vnd(total_amt)}")

    # Thống kê nhanh các nguồn thu nhập
    if incomes:
        print("\n💰 NGUỒN THU NHẬP CHÍNH:")
        income_totals = {}
        for d in incomes:
            income_totals[d["name"]] = income_totals.get(d["name"], 0) + d["amount"]
        sorted_inc = sorted(income_totals.items(), key=lambda x: x[1], reverse=True)
        for idx, (src_name, total_amt) in enumerate(sorted_inc[:5], 1):
            print(f"{idx:>2}. {src_name:<25} : {format_vnd(total_amt)}")


# --- NHẬP & XUẤT DỮ LIỆU ---

def export_data():
    data = load_data()
    print("\n1. Xuất file JSON")
    print("2. Xuất file CSV")
    choice = input("Chọn định dạng (1/2): ").strip()

    ts = int(datetime.now().timestamp())
    if choice == "1":
        file_name = f"finance_export_{ts}.json"
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ Đã xuất JSON: {file_name}")
    elif choice == "2":
        file_name = f"finance_export_{ts}.csv"
        with open(file_name, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "type", "name", "amount", "date", "note"])
            writer.writeheader()
            for row in data:
                r = row.copy()
                if "type" not in r:
                    r["type"] = "expense"
                if "note" not in r:
                    r["note"] = ""
                writer.writerow(r)
        print(f"✅ Đã xuất CSV: {file_name}")


def import_data():
    file_path = input("\nNhập đường dẫn file (JSON hoặc CSV): ").strip().strip("'\"")
    if not os.path.exists(file_path):
        print("❌ File không tồn tại.")
        return

    cutoff = get_cutoff_date()
    incoming = []

    try:
        if file_path.endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                incoming = json.load(f)
        elif file_path.endswith(".csv"):
            with open(file_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    incoming.append({
                        "id": row.get("id") or str(int(datetime.now().timestamp() * 1000)),
                        "type": row.get("type", "expense"),
                        "name": row.get("name", ""),
                        "amount": float(row.get("amount", 0)),
                        "date": row.get("date", ""),
                        "note": row.get("note", "")
                    })
        else:
            print("❌ Chỉ hỗ trợ định dạng .json hoặc .csv")
            return

        current_data = load_data()
        imported = 0
        ignored = 0

        for item in incoming:
            entry_date = parse_date(item.get("date", ""))
            try:
                amt = float(item.get("amount", 0))
            except (ValueError, TypeError):
                amt = 0

            if item.get("name") and amt > 0 and entry_date and entry_date >= cutoff:
                current_data.append({
                    "id": str(item.get("id", int(datetime.now().timestamp() * 1000))),
                    "type": item.get("type", "expense"),
                    "name": strip_accents(item["name"]),
                    "amount": amt,
                    "date": item["date"],
                    "note": item.get("note", "")
                })
                imported += 1
            else:
                ignored += 1

        save_data(current_data)
        print(f"✅ Đã nhập thành công: {imported} mục.")
        if ignored > 0:
            print(f"⚠️  Bỏ qua {ignored} mục (dữ liệu sai định dạng hoặc cũ hơn 1 năm).")

    except Exception as e:
        print(f"❌ Có lỗi xảy ra khi đọc file: {e}")


# --- MENU CHÍNH ---

def main():
    check_and_prune()

    while True:
        print("\n" + "=" * 36)
        print("   QUẢN LÝ TÀI CHÍNH CÁ NHÂN (CLI)")
        print("=" * 36)
        print("1. Thêm giao dịch mới (Tiền vào / Tiền ra)")
        print("2. Báo cáo & Dashboard (Thu, Chi, Số dư)")
        print("3. Tìm kiếm giao dịch (Ngày/Tuần/Tháng/Tên)")
        print("4. Sửa / Xóa giao dịch")
        print("5. Xuất dữ liệu (Export)")
        print("6. Nhập dữ liệu (Import)")
        print("7. Thoát")

        choice = input("Chọn chức năng (1-7): ").strip()
        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_dashboard()
        elif choice == "3":
            search_transactions()
        elif choice == "4":
            edit_or_delete_transaction()
        elif choice == "5":
            export_data()
        elif choice == "6":
            import_data()
        elif choice == "7":
            print("Tạm biệt!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng thử lại.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LiemFinance - quản lý thu chi cá nhân")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Mở giao diện dòng lệnh thay vì Web UI.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Cổng localhost cho Web UI (mặc định: 8765).",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Không tự động mở trình duyệt.",
    )
    args = parser.parse_args()
    if args.cli:
        main()
    else:
        run_web_server(port=args.port, open_browser=not args.no_browser)