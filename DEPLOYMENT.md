# Thông Tin Deploy — Checkpoint 5

## Thông Tin Học Viên

| Mục | Nội dung |
|-----|----------|
| Họ và tên | Nguyễn Hoàng Anh |
| Mã học viên | 2A202602811 |
| Repo | https://github.com/VinUni-AI20k/K4-L3B-DAY12-NguyenHoangAnh-L3B202602811-CloudServicesAndDeployment |

## Service

| Mục | Nội dung |
|-----|----------|
| Public URL | https://day12-agent-oipu.onrender.com |
| Platform | Render |
| Ngày deploy | 2026-09-29 |

## Biến Môi Trường Đã Set Trên Cloud

| Biến | Đã set | Ghi chú |
|------|--------|---------|
| `PORT` | ✅ | Platform tự gán |
| `AGENT_API_KEY` | ✅ | Đặt trong Render dashboard, không nằm trong repo |
| `REDIS_URL` | ✅ | Render Redis service |
| `RATE_LIMIT_PER_MINUTE` | ✅ | 10 |
| `MONTHLY_BUDGET_USD` | ✅ | 10.0 |
| `LOG_LEVEL` | ✅ | INFO |

## Lệnh Kiểm Tra

### 1. Liveness

```text
GET https://day12-agent-oipu.onrender.com/health

HTTP/1.1 200 OK

{"status":"ok","service":"day12-agent","version":"1.0.0"}
```

### 2. Readiness — mong đợi 200 {"status":"ready"} (đã nối được Redis)
```text
GET https://day12-agent-oipu.onrender.com/ready

HTTP/1.1 200 OK

{"status":"ready","redis":true}
```

### 3. Không có API key — mong đợi 401
```text
POST https://day12-agent-oipu.onrender.com/ask

HTTP/1.1 401 Unauthorized
```

# 4. Có API key — mong đợi 200 kèm câu trả lời
```text
POST https://day12-agent-oipu.onrender.com/ask

HTTP/1.1 200 OK

Response:
{
  "answer": "Câu hỏi hay. Deploy là gì thường được giải quyết bằng cách chuẩn hóa môi trường chạy: cùng một image chạy giống nhau ở laptop và trên cloud.",
  "user_id": "cp5-test",
  "history_length": 0,
  "cost_usd": 2.145e-05,
  "tokens": {
    "in": 3,
    "out": 35
  }
}
```

# 5. Rate limit — gọi 15 lần, những lần cuối phải trả 429
```text
Đã thử gửi nhiều request liên tiếp tới /ask với cùng user.

Một số request trong lần kiểm tra thủ công trả 000 do kết nối không nhận được HTTP response, vì vậy kết quả này không được dùng làm bằng chứng cho HTTP 429.

Rate limit được cấu hình:
RATE_LIMIT_PER_MINUTE=10
```

## Kết Quả Chạy Thật

Public deployment đã được kiểm tra thành công:

- Public URL sử dụng HTTPS.
- `/health` trả HTTP 200.
- `/ready` trả HTTP 200 và Redis ở trạng thái ready.
- `/ask` không có API key trả HTTP 401.
- `/ask` với API key hợp lệ trả HTTP 200.

Kết quả kiểm tra CP5 sau khi hoàn thiện DEPLOYMENT.md:

```text
9 passed, 4 skipped
```

## Ảnh Chụp Màn Hình

Đặt ảnh trong thư mục `screenshots/`:

- `screenshots/dashboard.png` — trang quản lý service trên platform
- `screenshots/health.png` — kết quả gọi `/health` từ trình duyệt hoặc curl

---

