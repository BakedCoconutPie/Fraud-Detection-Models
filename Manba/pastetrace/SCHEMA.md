# Schema chuẩn hóa dữ liệu hành vi PasteTrace (để tái sử dụng)

Mục tiêu: một format JSON độc lập với nguồn (PasteTrace sp2023 hiện tại, hoặc
dữ liệu thầy/nguồn khác sau này), chỉ chứa **hành vi** (KHÔNG có code cuối
`.pde`), để mọi pipeline sau này đọc từ MỘT định dạng duy nhất.

## 1. Cấu trúc 1 file phiên — `normalized/<session_id>.json`

```json
{
  "session_id": "111/A",
  "source": "pastetrace_sp2023",
  "label": 1,
  "events": [
    { "t": 0.0, "type": "paste", "text": "float shape1X, ...", "paste_source": "external" },
    { "t": 13.4, "type": "type",  "text": "int ",              "paste_source": null }
  ]
}
```

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| session_id | string | `"<case>/<student>"`, vd `"111/A"`. Có hậu tố `_<subfolder>` khi 1 SV có nhiều bài nộp độc lập (mục 3.4). |
| source | string | Tên nguồn gốc. Hiện luôn `"pastetrace_sp2023"`. Data thầy sau này dùng `source` khác (vd `"teacher_2026"`), CÙNG schema. |
| label | int 0/1 | 1=Cheated, 0=Normal. Nguồn: cột `Cheated` trong agrigation.csv. |
| events | array | Đã sắp theo thời gian tăng dần. |

## 2. Một event trong events[]

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| t | float (giây) | Thời gian TƯƠNG ĐỐI từ event đầu (event đầu t=0.0), làm tròn 0.1s. Luôn không giảm. |
| type | enum | "type" (gõ) \| "paste" (dán) \| "cut" (cắt) \| "other" (khác). |
| text | string | Nội dung thô của event (HÀNH VI, không phải code cuối). |
| paste_source | enum\|null | Chỉ khi type=="paste": "own" \| "external" \| "same_machine" \| "unknown". null với event khác. |

## 3. Quy tắc chuyển đổi từ meta.json gốc

### 3.1. Loại sự kiện — đọc từ trường `L` (KHÔNG phải `T`)
T→type, P→paste, C→cut, X→other. **L="O" BỊ LOẠI HOÀN TOÀN** (log "Untracked
file loaded" = mở đề bài, không phải hành vi SV). Không có trong sp2023 nhưng
giữ quy tắc cho data tương lai.

### 3.2. Thời gian — giải mã trường `T` gốc
T gốc = base64(bigEndianLong(...)) với ký tự 'A' dẫn đầu bị cắt. Giải mã: pad
'A' đủ 12 ký tự → base64-decode → big-endian signed long → đơn vị decisecond
(0.1s), wrap chu kỳ ~30 ngày. Tính t: delta = max(0, T[i]-T[i-1]) (CLIP delta
âm về 0), t[i]=t[i-1]+delta/10, t[0]=0.

### 3.3. Nguồn cú dán — đọc từ trường `N` của event paste (thứ tự ưu tiên)
1. N chứa "corrupt" → unknown
2. UUID trong N trùng CreatorUUID/ProjectUUID của chính phiên → own
3. "same creator"/"internal paste" → own
4. "noncoded source" → external
5. UUID rỗng 00000000-... → external
6. "same machine" → same_machine (GIỮ RIÊNG, mơ hồ — KHÔNG gộp vào own/external)
7. còn lại → unknown

### 3.4. Gộp/tách khi 1 SV có nhiều meta.json (quyết định THỦ CÔNG)
- GỘP thành 1 session khi các file nested là các TAB của cùng 1 sketch (cùng
  CreatorUUID, 1 evaluation.txt chung). VD: `111/B` (5 tab OOP).
- TÁCH thành nhiều session khi các thư mục con là bài nộp ĐỘC LẬP, mỗi cái có
  evaluation.txt riêng. VD: `211/O` → `211/O_BouncingBall` + `211/O_StudentFractalAssign`.
- Đây là quyết định thủ công cho sp2023, KHÔNG phải luật tự động. Data mới phải
  rà lại từng ca.

## 4. Nhãn (label)
Từ cột `Cheated` trong agrigation.csv: X→1, rỗng→0, ?/*→LOẠI, không có dòng→LOẠI.
Nhãn lưu RIÊNG ở normalized/labels.csv, KHÔNG nằm trong file JSON phiên (tránh
rò rỉ nhãn vào input model).

## 5. Giới hạn đã biết
- t chỉ chính xác 0.1s.
- Wrap chu kỳ ~30 ngày có thể gây delta âm (đã clip về 0) — chưa gặp trong sp2023.
- Quy tắc gộp/tách là thủ công cho 2 ca cụ thể.
