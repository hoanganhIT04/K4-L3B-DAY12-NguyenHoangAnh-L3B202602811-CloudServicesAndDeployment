# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Cách trả lời: thay dòng `> *Câu trả lời của bạn*` bằng câu trả lời.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Nguyễn Hoàng Anh  Mã học viên: 2A202602811.

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

> *Khi deploy hoặc chạy app trên một máy mới mà tôi quên cấu hình AGENT_API_KEY, ứng dụng sẽ báo lỗi ngay lúc khởi động thay vì chạy với một key mặc định không an toàn. Điều này giúp tôi phát hiện cấu hình bị thiếu trước khi service nhận request thật. Nếu dùng "changeme", app vẫn có thể chạy và tôi có thể vô tình deploy một service với API key yếu.*

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

> *Từ dòng log JSON, tôi có thể lọc các request theo user_id và thống kê số token hoặc chi phí bằng chương trình/log system. Tôi cũng có thể tìm kiếm và tổng hợp các event "ask_completed" theo thời gian để theo dõi hoạt động của service. Với print("đã trả lời xong"), thông tin không có cấu trúc nên khó tự động lọc, thống kê hoặc phân tích theo từng trường dữ liệu.*

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | ... MB |
| Multi-stage | ... MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

> *Hiện tại tôi chưa đo được dung lượng image thực tế vì Docker Engine trên máy chưa khởi động được do virtualization chưa được bật. Vì vậy tôi không ghi số MB ước lượng để tránh nhầm với số đo thực tế.

> Về nguyên lý, bản multi-stage nhỏ hơn vì image runtime chỉ giữ Python runtime, virtual environment và source code cần thiết. Các thành phần phục vụ quá trình build như cache của pip và các file trung gian của build stage không được đưa sang runtime image.*

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

> *Khi chỉ sửa một ký tự trong app/main.py, các layer trước bước COPY app vẫn được Docker lấy lại từ cache, đặc biệt là layer cài dependencies. Các layer từ COPY app trở đi phải được build lại vì nội dung source code đã thay đổi.

> Nếu đặt COPY . . trước RUN pip install thì mỗi lần source code thay đổi, layer COPY sẽ thay đổi và Docker phải chạy lại RUN pip install. Điều này làm thời gian build lâu hơn dù requirements.txt không thay đổi.*

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

> *Nếu Python application có một lỗ hổng cho phép kẻ tấn công thực thi lệnh, các lệnh đó sẽ được thực thi với quyền của user đang chạy container. Nếu container chạy bằng root thì attacker có quyền rất cao bên trong container và nếu kết hợp với một lỗ hổng escape container hoặc cấu hình Docker không an toàn thì rủi ro có thể lan tới host.

> Lệnh USER appuser khiến process Python chạy bằng user không có quyền root. Vì vậy ngay cả khi attacker thực thi được lệnh thông qua lỗ hổng trong application, quyền của process bị giới hạn và giảm mức độ ảnh hưởng.*

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

> *Nếu dùng cách đếm theo phút đồng hồ và giới hạn là 10 request/phút, người dùng có thể gửi tối đa 20 request trong khoảng 2 giây nằm ngay quanh thời điểm chuyển phút. Ví dụ, gửi 10 request ngay trước giây 00 của phút mới và tiếp tục gửi 10 request ngay sau giây 00. Bộ đếm của phút cũ và phút mới được reset riêng nên cả hai nhóm đều được cho phép.

Sliding window 60 giây tránh được hiện tượng này vì mọi request trong 60 giây gần nhất đều được tính chung.*

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

> *Rate limit giới hạn số lần request trong một khoảng thời gian, còn cost guard giới hạn tổng chi phí sử dụng của một user trong tháng.

> Ví dụ rate limit có thể cho qua một request vì user mới gửi vài request trong phút hiện tại, nhưng cost guard vẫn chặn nếu chi phí dự kiến của request làm tổng chi phí vượt monthly budget.

> Ngược lại, user có thể còn rất nhiều ngân sách nhưng gửi request với tốc độ quá nhanh. Khi đó cost guard vẫn cho phép nhưng rate limit sẽ trả về HTTP 429.*

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

> *Nếu /health cũng kiểm tra Redis, khi Redis mất kết nối thì cả 3 container đều bắt đầu trả trạng thái không khỏe thay vì chỉ /ready bị ảnh hưởng.

> Load balancer hoặc platform health check gọi /health trên từng container. Vì /health phụ thuộc Redis nên cả 3 container có thể bị đánh dấu unhealthy. Platform có thể restart hoặc loại từng container khỏi traffic. Trong khoảng Redis mất kết nối 30 giây, service có thể bị restart hàng loạt dù bản thân application process vẫn đang chạy. Khi Redis hoạt động lại, các container mới hoặc các container còn sống mới có thể trở lại trạng thái healthy.

> Thiết kế hiện tại tách /health và /ready: /health chỉ kiểm tra process, còn /ready kiểm tra Redis. Vì vậy mất Redis không đồng nghĩa application container bị coi là đã chết.*

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

> *Nếu /health cũng kiểm tra Redis, khi Redis mất kết nối thì cả 3 container đều bắt đầu trả trạng thái không khỏe thay vì chỉ /ready bị ảnh hưởng.

> Load balancer hoặc platform health check gọi /health trên từng container. Vì /health phụ thuộc Redis nên cả 3 container có thể bị đánh dấu unhealthy. Platform có thể restart hoặc loại từng container khỏi traffic. Trong khoảng Redis mất kết nối 30 giây, service có thể bị restart hàng loạt dù bản thân application process vẫn đang chạy. Khi Redis hoạt động lại, các container mới hoặc các container còn sống mới có thể trở lại trạng thái healthy.

> Thiết kế hiện tại tách /health và /ready: /health chỉ kiểm tra process, còn /ready kiểm tra Redis. Vì vậy mất Redis không đồng nghĩa application container bị coi là đã chết.*

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

> *Khi kiểm tra deployment trên Render, tôi gặp lỗi test không thể kết nối tới endpoint public và báo ConnectTimeout/ConnectError. Tôi kiểm tra lại service trên Render và gọi trực tiếp /health thì thấy service vẫn trả HTTP 200, nên nguyên nhân không phải Render service bị down.

> Sau đó tôi kiểm tra cách test lấy Public URL trong DEPLOYMENT.md và phát hiện URL đang được ghi dưới dạng Markdown link [https://day12-agent-oipu.onrender.com](https://day12-agent-oipu.onrender.com). Test dùng regex để lấy URL nên lấy cả phần cú pháp Markdown thay vì chỉ lấy URL thuần. Tôi đổi dòng Public URL thành https://day12-agent-oipu.onrender.com. Sau đó chạy lại pytest tests/test_cp5.py -v và kết quả là 9 passed, 4 skipped.*
