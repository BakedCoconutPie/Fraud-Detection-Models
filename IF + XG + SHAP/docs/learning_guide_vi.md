# Hướng dẫn hiểu toàn bộ phần PasteTrace -> IF + XGBoost + SHAP

Tài liệu này viết cho thành viên phụ trách:

1. Chuyển dữ liệu PasteTrace cũ sang schema chuẩn cho nhóm dùng.
2. Chạy pipeline IF + XGBoost + SHAP.
3. Giải thích được dữ liệu, code, kết quả và các metric khi bị hỏi.

Mục tiêu không phải là học thuộc từng dòng code, mà là hiểu "vì sao mình làm
như vậy" và "mỗi output có ý nghĩa gì".

---

## 1. Bức tranh tổng thể

Bài toán của nhóm là phát hiện rủi ro gian lận trong bài thi lập trình, nhưng
không nhìn vào code cuối cùng là chính. Thay vào đó, nhóm nhìn vào hành vi tạo
ra code:

- Sinh viên gõ gì?
- Dán gì?
- Cắt gì?
- Dán từ nguồn nào?
- Thao tác diễn ra nhanh/chậm ra sao?
- Có khoảng nghỉ dài bất thường không?
- Một phiên làm bài giống quá trình tự viết hay giống dán nguyên khối?

Pipeline hiện tại đi theo flow:

```text
PasteTrace/meta.json gốc
        |
        v
Data chuẩn hóa JSON theo từng session
        |
        v
Trích feature dạng bảng
        |
        v
Isolation Forest tạo anomaly score
        |
        v
XGBoost phân loại normal/cheated
        |
        v
SHAP giải thích feature nào ảnh hưởng dự đoán
        |
        v
metrics + predictions + shap_importance
```

Điểm quan trọng: model không dùng source code cuối cùng để học. Model chỉ dùng
log hành vi.

---

## 2. Data PasteTrace gốc có gì?

PasteTrace là hệ thống theo dõi hành vi lập trình trong IDE. Dữ liệu gốc thường
có các file như:

- `meta.json`: log thao tác trong IDE.
- code cuối cùng như `.pde`: sản phẩm cuối của sinh viên.
- `evaluation.txt` hoặc file đánh giá: ghi chú/nhãn đánh giá.
- file tổng hợp nhãn, ví dụ `agrigation.csv`.

Trong `meta.json`, mỗi event gốc không được trình bày dễ đọc như schema mới.
Một số thông tin quan trọng:

- Loại event nằm trong trường `L`.
- Thời gian event nằm trong trường `T`, nhưng bị mã hóa.
- Nguồn dán nằm trong trường `N` của event paste.
- Có các UUID để biết paste là từ project của chính sinh viên hay từ ngoài.

Vấn đề của data gốc:

- Khó đọc trực tiếp.
- Format phụ thuộc PasteTrace.
- Thời gian bị encode, không tiện đưa vào model.
- Event type chưa thân thiện cho pipeline chung.
- Một sinh viên có thể có nhiều file/tab/subfolder, phải quyết định gộp hay tách.
- Nếu đưa nguyên code cuối vào model thì dễ lệch mục tiêu nghiên cứu.

Vì vậy bạn phải chuẩn hóa.

---

## 3. Vì sao phải chuẩn hóa data?

Chuẩn hóa nghĩa là biến dữ liệu gốc rối và phụ thuộc nguồn thành một format
chung, dễ đọc, dễ tái sử dụng.

Lý do cần làm:

1. Để model đọc được một format duy nhất.
   Sau này data FPT cũng convert về schema này, code model không cần sửa nhiều.

2. Để loại bỏ thông tin không nên dùng.
   Ví dụ source code cuối cùng không đưa vào model IF + XGBoost + SHAP.

3. Để tránh rò rỉ nhãn.
   Nhãn `cheated/normal` được để trong `labels.csv`, không trộn vào feature
   đầu vào một cách vô tình.

4. Để tái lập thí nghiệm.
   Ai pull repo về cũng biết dùng 16 phiên gốc hay 19 phiên đầy đủ.

5. Để giải thích với người đọc.
   Một schema rõ ràng dễ viết vào paper hơn nhiều so với mô tả data gốc.

Nếu bị hỏi "đóng góp phần data của em là gì?", có thể trả lời:

> Em tái cấu trúc dữ liệu PasteTrace gốc thành một schema hành vi thống nhất ở
> cấp session. Schema này tách nhãn riêng, chuẩn hóa thời gian tương đối, chuẩn
> hóa loại event, chuẩn hóa nguồn paste, và giữ lại các tín hiệu hành vi cần cho
> cả pipeline IF + XGBoost + SHAP lẫn các model sau này.

---

## 4. Data chuẩn hóa của mình có gì?

Folder:

```text
PasteTrace_Normalized/
|-- README.md
|-- SCHEMA.md
|-- inventory.xlsx
`-- normalized/
    |-- labels.csv
    |-- 111_A.json
    |-- 111_B.json
    |-- ...
    `-- 211_Q.json
```

### 4.1. `normalized/<session_id>.json`

Mỗi file JSON là một phiên làm bài.

Ví dụ rút gọn:

```json
{
  "session_id": "111/A",
  "source": "pastetrace_sp2023",
  "events": [
    {
      "t": 0.0,
      "type": "paste",
      "text": "float shape1X, ...",
      "paste_source": "external"
    },
    {
      "t": 13.4,
      "type": "type",
      "text": "\\b",
      "paste_source": null
    }
  ]
}
```

Ý nghĩa:

- `session_id`: mã phiên, ví dụ `111/A`.
- `source`: nguồn dữ liệu, hiện là `pastetrace_sp2023`.
- `events`: danh sách thao tác theo thời gian.

Mỗi event:

- `t`: thời gian tương đối, tính bằng giây, event đầu tiên là `0.0`.
- `type`: loại thao tác.
- `text`: nội dung thao tác.
- `paste_source`: nguồn paste nếu event là `paste`.

### 4.2. Các loại event

| Type | Nghĩa | Ví dụ |
|---|---|---|
| `type` | Sinh viên gõ/chỉnh bằng bàn phím | gõ `int x = 0;`, backspace |
| `paste` | Dán nội dung | dán một hàm, một đoạn code |
| `cut` | Cắt/xóa một đoạn | cut một block code |
| `other` | Sự kiện khác | event không thuộc 3 nhóm trên |

### 4.3. `paste_source`

| Giá trị | Nghĩa |
|---|---|
| `own` | Dán từ chính project/creator của phiên |
| `external` | Dán từ nguồn ngoài hoặc nguồn không thuộc project |
| `same_machine` | Cùng máy, nhưng mơ hồ, không kết luận là hợp lệ hay ngoài |
| `unknown` | Không xác định được |
| `null` | Không phải event paste |

Điểm cực kỳ quan trọng: `same_machine` được giữ riêng.

Không nên gộp `same_machine` vào `own` hay `external`, vì nó mơ hồ. Nếu tự gộp
nó vào `external`, model có thể bị thiên lệch. Nếu tự gộp vào `own`, model có
thể bỏ qua rủi ro thật.

### 4.4. `labels.csv`

File này chứa nhãn:

```csv
session_id,label,in_original_16
111/A,1,yes
111/B,0,no
111/D,1,yes
...
```

Ý nghĩa:

- `session_id`: nối nhãn với file JSON tương ứng.
- `label`: `1` là cheated/risky, `0` là normal.
- `in_original_16`: session này có thuộc tập 16 phiên gốc không.

Vì sao tách labels riêng?

- Model input nên là hành vi, không phải nhãn.
- Dễ chạy nhiều subset.
- Dễ tránh lẫn nhãn vào feature.

### 4.5. Vì sao có 16 và 19 phiên?

Có hai cách dùng data:

| Tập | Số phiên | Phân bố nhãn | Dùng khi nào |
|---|---:|---:|---|
| `original16` | 16 | 14 cheated / 2 normal | Tái lập kết quả theo tập cũ |
| `all19` | 19 | 16 cheated / 3 normal | Dùng đầy đủ data chuẩn hóa |

Ba phiên thêm ngoài 16:

- `111/B`: normal, nhưng là ca ranh giới vì có copy hợp lệ giữa các tab OOP.
- `211/O_BouncingBall`: cheated.
- `211/O_StudentFractalAssign`: cheated.

Khi viết paper hoặc báo cáo, phải ghi rõ đang dùng tập nào. Không được trộn số
liệu 16 và 19 mà không nói.

---

## 5. Các quy tắc chuyển từ data gốc sang data mới

### 5.1. Chuyển loại event

Trong meta gốc, loại event đọc từ trường `L`:

| Gốc | Mới |
|---|---|
| `T` | `type` |
| `P` | `paste` |
| `C` | `cut` |
| `X` | `other` |
| `O` | bỏ |

Vì sao bỏ `O`?

`O` là kiểu "Untracked file loaded", thường là mở file/đề bài, không phải hành
vi lập trình của sinh viên. Giữ lại có thể làm nhiễu model.

### 5.2. Chuyển thời gian

Trong PasteTrace gốc, thời gian không phải số giây trực tiếp. Nó được encode
trong trường `T`. Sau khi decode, mình chuyển thành thời gian tương đối:

```text
t[0] = 0
t[i] = t[i-1] + max(0, raw_time[i] - raw_time[i-1]) / 10
```

Nói dễ hiểu:

- Event đầu tiên là giây 0.
- Các event sau tính khoảng cách so với event trước.
- Đơn vị cuối cùng là giây.
- Nếu delta âm do lỗi/wrap thì clip về 0 để không làm thời gian đi lùi.

Vì sao dùng thời gian tương đối?

- Model không cần biết ngày/giờ tuyệt đối.
- Model chỉ cần biết nhịp làm bài: nhanh, chậm, nghỉ lâu, dán ngay từ đầu...

### 5.3. Xác định nguồn paste

Nguồn paste lấy từ trường `N` và các UUID liên quan.

Quy tắc ưu tiên:

1. Có chữ corrupt -> `unknown`.
2. UUID trùng project/creator hiện tại -> `own`.
3. "same creator" hoặc "internal paste" -> `own`.
4. "noncoded source" -> `external`.
5. UUID rỗng toàn 0 -> `external`.
6. "same machine" -> `same_machine`.
7. Còn lại -> `unknown`.

Điểm trả lời khi bị hỏi:

> Em không tự gán mọi paste không rõ thành gian lận. Em tách `own`,
> `external`, `same_machine`, `unknown` để model và phân tích sau này kiểm soát
> được từng loại nguồn paste.

### 5.4. Gộp/tách session

Một số sinh viên có nhiều file/subfolder. Không phải lúc nào cũng gộp hết.

Quy tắc:

- Nếu nhiều file là nhiều tab của cùng một sketch/project -> gộp thành một
  session. Ví dụ `111/B`.
- Nếu nhiều folder là nhiều bài độc lập -> tách thành nhiều session. Ví dụ
  `211/O_BouncingBall` và `211/O_StudentFractalAssign`.

Đây là quyết định thủ công, không nên tự động hóa mù quáng.

---

## 6. Source code IF + XGBoost + SHAP chạy như thế nào?

File chính:

```text
src/pastetrace_if_xgb_shap.py
```

Chạy bằng:

```powershell
.\scripts\run_if_xgb_shap.ps1 `
  -DataDir "D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized" `
  -Subset original16 `
  -OutDir "outputs\pastetrace_original16"
```

Hoặc chạy trực tiếp:

```powershell
python src/pastetrace_if_xgb_shap.py `
  --data "D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized" `
  --subset original16 `
  --out outputs\pastetrace_original16
```

### 6.1. `main()`

`main()` nhận tham số:

- `--data`: đường dẫn folder data chuẩn hóa.
- `--subset`: `original16` hoặc `all`.
- `--out`: folder output.
- `--features-only`: chỉ trích feature, không train model.

Flow:

```text
main()
  -> load_features()
  -> ghi features.csv
  -> nếu không features-only:
       run_loo_pipeline()
```

### 6.2. `load_features()`

Nhiệm vụ:

1. Đọc `normalized/labels.csv`.
2. Nếu chọn `original16`, lọc `in_original_16 == yes`.
3. Với mỗi `session_id`, tìm file JSON tương ứng.
4. Gọi `summarize_session()` để biến event list thành một dòng feature.
5. Trả về bảng `features`.

Ví dụ:

```text
111/A -> normalized/111_A.json -> 1 dòng trong features.csv
211/Q -> normalized/211_Q.json -> 1 dòng trong features.csv
```

### 6.3. `summarize_session()`

Đây là phần biến log hành vi thành feature dạng bảng.

Input:

```text
1 file JSON session
1 dòng label tương ứng
```

Output:

```text
1 dòng feature
```

Các feature chính:

| Feature | Nghĩa |
|---|---|
| `event_count` | Tổng số event |
| `duration_sec` | Thời lượng phiên |
| `type_event_count` | Số event gõ |
| `paste_event_count` | Số event dán |
| `cut_event_count` | Số event cắt |
| `type_chars` | Tổng số ký tự gõ |
| `paste_chars` | Tổng số ký tự dán |
| `cut_chars` | Tổng số ký tự cắt |
| `paste_char_ratio` | Tỷ lệ ký tự đến từ paste |
| `max_paste_chars` | Cú dán dài nhất |
| `mean_paste_chars` | Độ dài dán trung bình |
| `max_type_chars` | Event gõ dài nhất |
| `mean_gap_sec` | Khoảng nghỉ trung bình giữa event |
| `max_gap_sec` | Khoảng nghỉ dài nhất |
| `long_gap_count_30s` | Số khoảng nghỉ từ 30 giây |
| `long_gap_count_120s` | Số khoảng nghỉ từ 120 giây |
| `paste_external_chars` | Số ký tự dán từ external |
| `paste_same_machine_count` | Số lần dán từ same machine |

Ví dụ đọc một dòng feature:

```text
session_id = 111/A
label = 1
event_count = 42
paste_chars = 2327
type_chars = 162
paste_char_ratio = 0.935
max_paste_chars = 2081
```

Diễn giải:

> Phiên này có 42 event, phần lớn ký tự đến từ paste, cú dán lớn nhất dài 2081
> ký tự. Đây là hành vi có rủi ro cao hơn so với quá trình gõ dần.

### 6.4. `run_loo_pipeline()`

Đây là phần train/evaluate model.

Flow:

```text
features.csv
   |
   v
Tách X và y
   |
   v
Leave-One-Out:
   mỗi lần giữ 1 session làm test
   các session còn lại làm train
   |
   v
StandardScaler
   |
   v
Isolation Forest
   |
   v
thêm if_anomaly_score vào feature
   |
   v
cân bằng lớp train
   |
   v
XGBoost
   |
   v
dự đoán prob_cheat cho session test
   |
   v
SHAP giải thích dự đoán
   |
   v
tổng hợp predictions + metrics + SHAP
```

---

## 7. Leave-One-Out là gì?

Leave-One-Out, viết tắt LOO, là một kiểu cross-validation cho dữ liệu nhỏ.

Nếu có 16 session:

- Fold 1: lấy session 1 làm test, 15 session còn lại train.
- Fold 2: lấy session 2 làm test, 15 session còn lại train.
- ...
- Fold 16: lấy session 16 làm test, 15 session còn lại train.

Cuối cùng có đúng 16 dự đoán, mỗi session được test một lần.

Vì sao dùng LOO?

- Dữ liệu rất nhỏ.
- Nếu chia train/test thường, test set có thể chỉ vài dòng.
- LOO tận dụng tối đa data để train trong từng fold.

Điểm cần nói rõ:

> Trong mỗi fold, model chỉ học từ các phiên train. Phiên test được giữ riêng,
> nên không bị dùng để fit scaler, Isolation Forest hoặc XGBoost.

---

## 8. Isolation Forest là gì?

Isolation Forest, viết tắt IF, là mô hình phát hiện bất thường.

Ý tưởng:

- Điểm bình thường thường nằm trong cụm đông.
- Điểm bất thường thường khác phần còn lại.
- Nếu dùng nhiều cây chia ngẫu nhiên, điểm bất thường dễ bị cô lập nhanh hơn.

Trong project này, IF không trực tiếp kết luận gian lận. Nó tạo ra:

```text
if_anomaly_score
```

Điểm này trả lời câu hỏi:

> Phiên này có hành vi tổng thể bất thường so với các phiên train không?

Ví dụ:

- Một session chỉ có 1 event paste rất dài.
- Một session có thời lượng cực dài.
- Một session có nhịp thao tác khác hẳn số đông.

Các trường hợp này có thể có anomaly score cao.

Vì sao dùng IF?

- Không cần nhãn để học pattern bất thường.
- Phù hợp dữ liệu nhỏ.
- Tạo thêm tín hiệu bổ sung cho XGBoost.

---

## 9. XGBoost là gì?

XGBoost là mô hình phân loại dựa trên nhiều cây quyết định.

Nói dễ hiểu:

- Một cây quyết định giống như chuỗi câu hỏi:
  - `paste_char_ratio > 0.8?`
  - `max_paste_chars > 1000?`
  - `event_count < 10?`
- Một cây đơn lẻ thường yếu.
- XGBoost ghép nhiều cây yếu lại để thành model mạnh hơn.

Trong project này, XGBoost nhận input:

```text
features hành vi + if_anomaly_score
```

Output:

```text
prob_cheat
```

`prob_cheat` là xác suất/risk score model gán cho session thuộc lớp `1`
(cheated/risky).

Ví dụ:

```text
prob_cheat = 0.9827
```

Diễn giải:

> Theo model, session này có điểm rủi ro rất cao.

Trong code hiện tại:

```text
pred_label = 1 nếu prob_cheat >= 0.5
pred_label = 0 nếu prob_cheat < 0.5
```

Lưu ý:

Ngưỡng `0.5` là ngưỡng mặc định. Trong ứng dụng thật, có thể chỉnh ngưỡng để ưu
tiên ít bỏ sót gian lận hoặc ít báo nhầm sinh viên trung thực.

---

## 10. SHAP là gì?

SHAP là phương pháp giải thích model.

Nếu XGBoost trả lời:

```text
Session này rủi ro cao.
```

SHAP giúp trả lời tiếp:

```text
Vì feature nào làm model nghĩ như vậy?
```

Ví dụ:

- `max_paste_chars` cao làm tăng rủi ro.
- `event_count` thấp/cao bất thường làm tăng rủi ro.
- `paste_external_chars` cao làm tăng rủi ro.
- `duration_sec` hoặc `max_type_chars` có thể làm tăng/giảm rủi ro tùy pattern.

Có hai mức SHAP:

1. Local explanation: giải thích một session cụ thể.
   File: `shap_values.csv`.

2. Global importance: feature nào quan trọng trung bình trên toàn bộ dataset.
   File: `shap_importance.csv` và `shap_importance.png`.

SHAP value:

- Dương: feature đẩy dự đoán về lớp 1 hơn.
- Âm: feature kéo dự đoán về lớp 0 hơn.
- Gần 0: feature ít ảnh hưởng trong dự đoán đó.

`mean_abs_shap`:

- Lấy trị tuyệt đối SHAP rồi trung bình.
- Dùng để xếp hạng feature quan trọng toàn cục.
- Càng lớn nghĩa là feature càng ảnh hưởng đến model.

---

## 11. Vì sao kết hợp IF + XGBoost + SHAP?

Ba thành phần có vai trò khác nhau:

| Thành phần | Vai trò |
|---|---|
| Isolation Forest | Bắt tín hiệu bất thường không cần nhãn |
| XGBoost | Học phân loại từ feature + nhãn |
| SHAP | Giải thích vì sao model dự đoán như vậy |

Nếu chỉ dùng IF:

- Có anomaly score.
- Nhưng không tận dụng nhãn cheated/normal.
- Bất thường không đồng nghĩa chắc chắn gian lận.

Nếu chỉ dùng XGBoost:

- Học được nhãn.
- Nhưng mất một tín hiệu bất thường tổng quát có ích trong data nhỏ.

Nếu không dùng SHAP:

- Có dự đoán.
- Nhưng khó giải thích với giảng viên/reviewer.

Vì vậy pipeline này hợp với mục tiêu bài báo:

> Tạo điểm rủi ro và giải thích hỗ trợ giảng viên xem lại, không tự động kết
> luận sinh viên gian lận.

---

## 12. Output của pipeline có gì?

Khi chạy xong, output nằm trong:

```text
outputs/pastetrace_original16/
outputs/pastetrace_all19/
```

### 12.1. `features.csv`

Đây là bảng đặc trưng sau khi trích từ JSON.

Mỗi dòng = một session.

Dùng để:

- Kiểm tra data đã đọc đúng chưa.
- Xem behavior thô ở dạng số.
- Là input cho model.

### 12.2. `predictions.csv`

Các cột:

| Cột | Nghĩa |
|---|---|
| `session_id` | Mã phiên |
| `label` | Nhãn thật |
| `prob_cheat` | Xác suất/risk score model dự đoán |
| `pred_label` | Nhãn dự đoán sau threshold 0.5 |
| `if_anomaly_score` | Điểm bất thường từ Isolation Forest |

Ví dụ:

```text
111/A,label=1,prob_cheat=0.9827,pred_label=1
```

Diễn giải:

> Phiên `111/A` thật sự là cheated, model dự đoán cheated, điểm rủi ro cao.

Ví dụ lỗi:

```text
111/E,label=0,prob_cheat=0.9811,pred_label=1
```

Diễn giải:

> Phiên `111/E` thật sự normal nhưng model báo cheated. Đây là false positive.

### 12.3. `metrics.json`

Chứa kết quả tổng hợp:

```json
{
  "n_sessions": 16,
  "positive_labels": 14,
  "negative_labels": 2,
  "precision": 0.8667,
  "recall": 0.9286,
  "f1": 0.8966,
  "auc": 0.7143,
  "confusion_matrix": [[0, 2], [1, 13]]
}
```

### 12.4. `shap_values.csv`

Mỗi dòng = một session.

Mỗi cột feature = SHAP value của feature đó trong session đó.

Dùng khi muốn giải thích:

> Vì sao session A bị model chấm rủi ro cao?

### 12.5. `shap_importance.csv`

Xếp hạng feature quan trọng toàn cục.

Top feature hiện tại trên original16:

| Feature | Ý nghĩa |
|---|---|
| `max_type_chars` | Độ dài event gõ dài nhất |
| `event_count` | Tổng số event |
| `max_paste_chars` | Cú dán dài nhất |
| `paste_same_machine_count` | Số lần paste từ same machine |
| `duration_sec` | Thời lượng phiên |
| `paste_external_chars` | Số ký tự paste từ nguồn ngoài |

Diễn giải thận trọng:

> Model đang dùng cả tín hiệu paste lẫn cấu trúc tổng thể của phiên. Không chỉ
> có paste ratio, mà số event, độ dài thao tác gõ, thời lượng và nguồn paste
> cũng ảnh hưởng.

### 12.6. `shap_importance.png`

Biểu đồ top feature quan trọng.

Dùng để chèn vào slide hoặc paper.

---

## 13. Confusion matrix là gì?

Với bài toán binary classification:

- Lớp 1 = cheated/risky.
- Lớp 0 = normal.

Có 4 trường hợp:

| Tên | Nghĩa |
|---|---|
| TP | True Positive: gian lận thật, model báo gian lận |
| FP | False Positive: normal thật, model báo gian lận |
| TN | True Negative: normal thật, model báo normal |
| FN | False Negative: gian lận thật, model báo normal |

Confusion matrix trong sklearn có dạng:

```text
[[TN, FP],
 [FN, TP]]
```

Với original16:

```text
[[0, 2],
 [1, 13]]
```

Nghĩa là:

- TN = 0: không có phiên normal nào được dự đoán đúng.
- FP = 2: có 2 phiên normal bị báo nhầm là cheated.
- FN = 1: có 1 phiên cheated bị bỏ sót.
- TP = 13: có 13 phiên cheated được bắt đúng.

Đây là lý do phải cẩn thận: F1 khá cao, nhưng model vẫn báo nhầm normal vì số
normal quá ít.

---

## 14. Precision, Recall, F1, AUC là gì?

### 14.1. Precision

Công thức:

```text
Precision = TP / (TP + FP)
```

Nghĩa:

> Trong các phiên model báo là cheated, bao nhiêu phiên thật sự cheated?

Precision cao nghĩa là ít báo nhầm normal.

Trong bài này, Precision quan trọng vì báo nhầm sinh viên trung thực là vấn đề
nhạy cảm.

### 14.2. Recall

Công thức:

```text
Recall = TP / (TP + FN)
```

Nghĩa:

> Trong các phiên cheated thật, model bắt được bao nhiêu?

Recall cao nghĩa là ít bỏ sót gian lận.

Trong bài này, Recall quan trọng vì hệ thống hỗ trợ phát hiện rủi ro, không
muốn bỏ sót quá nhiều ca đáng kiểm tra.

### 14.3. F1

Công thức:

```text
F1 = 2 * Precision * Recall / (Precision + Recall)
```

F1 là trung bình điều hòa của Precision và Recall.

Nó hữu ích khi data lệch nhãn hơn accuracy.

Nếu bạn gõ "D1" thì gần như chắc là đang muốn nói "F1".

### 14.4. Accuracy

Công thức:

```text
Accuracy = số dự đoán đúng / tổng số phiên
```

Vì sao bài này không nên quá dựa vào accuracy?

Data PasteTrace lệch nhãn: 14 cheated, 2 normal. Một model đoán gần như toàn
cheated cũng có accuracy nhìn không quá tệ, nhưng không công bằng với normal.

### 14.5. AUC

AUC thường là diện tích dưới đường ROC.

Nó đo khả năng xếp hạng:

> Model có gán điểm rủi ro cao hơn cho cheated so với normal không?

AUC:

- 1.0: xếp hạng hoàn hảo.
- 0.5: gần như random.
- Dưới 0.5: xếp hạng ngược.

AUC dùng `prob_cheat`, không chỉ dùng `pred_label`.

---

## 15. Kết quả hiện tại nên hiểu thế nào?

### 15.1. Tập original16

Kết quả:

| Metric | Giá trị |
|---|---:|
| Sessions | 16 |
| Cheated / Normal | 14 / 2 |
| Precision | 0.867 |
| Recall | 0.929 |
| F1 | 0.897 |
| AUC | 0.714 |

Diễn giải:

- Model bắt được phần lớn cheated.
- Nhưng cả 2 phiên normal đều bị báo nhầm trong confusion matrix hiện tại.
- Vì normal quá ít, kết quả chưa đủ để kết luận model công bằng.

### 15.2. Tập all19

Kết quả:

| Metric | Giá trị |
|---|---:|
| Sessions | 19 |
| Cheated / Normal | 16 / 3 |
| Precision | 0.875 |
| Recall | 0.875 |
| F1 | 0.875 |
| AUC | 0.833 |

Diễn giải:

- Khi thêm 3 phiên, kết quả thay đổi.
- AUC cao hơn, nhưng vẫn còn lỗi.
- Cần ghi rõ đây là tập 19, không so trực tiếp lẫn lộn với tập 16.

### 15.3. Vì sao không nên nói model "đã tốt" quá mạnh?

Vì:

- Data nhỏ.
- Nhãn lệch nhiều về cheated.
- Normal chỉ có 2 hoặc 3 phiên.
- Một vài lỗi làm metric thay đổi rất mạnh.

Cách nói an toàn trong paper:

> Kết quả PasteTrace cho thấy pipeline chạy được và tạo ra tín hiệu giải thích
> hữu ích, nhưng chỉ đóng vai trò kiểm chứng phụ. Kết luận chính cần dựa trên
> bộ dữ liệu FPT lớn hơn.

---

## 16. Các thuật ngữ quan trọng

| Thuật ngữ | Nghĩa ngắn |
|---|---|
| Session | Một phiên làm bài của một sinh viên |
| Event | Một thao tác trong IDE |
| Feature | Đặc trưng số đưa vào model |
| Label | Nhãn thật, 1 cheated/risky, 0 normal |
| Train set | Dữ liệu dùng để học |
| Test set | Dữ liệu giữ lại để kiểm tra |
| Fold | Một lượt chia train/test trong cross-validation |
| LOO | Leave-One-Out, mỗi fold test 1 session |
| Anomaly score | Điểm bất thường |
| Risk score | Điểm rủi ro, ở đây là `prob_cheat` |
| Threshold | Ngưỡng đổi xác suất thành nhãn |
| False positive | Báo nhầm normal là cheated |
| False negative | Bỏ sót cheated |
| Feature importance | Mức quan trọng của feature |
| SHAP value | Mức đóng góp của feature vào dự đoán |

---

## 17. Nếu người ta hỏi, trả lời sao?

### Hỏi: Vì sao không dùng code cuối cùng?

Trả lời:

> Vì mục tiêu của bài là phát hiện tín hiệu trong quá trình tạo code, không
> phải so khớp sản phẩm cuối. Nếu dùng code cuối cùng, bài toán dễ quay về phát
> hiện tương đồng mã nguồn và không khai thác được hành vi như gõ, dán, cắt,
> thời gian và nguồn paste.

### Hỏi: Vì sao phải chuẩn hóa PasteTrace?

Trả lời:

> Dữ liệu gốc của PasteTrace phụ thuộc format riêng, thời gian bị encode và
> event type chưa tiện dùng. Em chuẩn hóa thành schema JSON chung để cả data
> PasteTrace và data FPT sau này dùng cùng pipeline, tránh phải viết code đọc
> riêng cho từng nguồn.

### Hỏi: Vì sao label để riêng?

Trả lời:

> Để tránh rò rỉ nhãn vào input model và để dễ chạy nhiều subset. JSON chỉ chứa
> hành vi, còn nhãn nằm trong `labels.csv`.

### Hỏi: Vì sao dùng 16 và 19 phiên?

Trả lời:

> 16 phiên là tập gốc để tái lập kết quả cũ. 19 phiên là tập đầy đủ sau khi nhóm
> chuẩn hóa thêm các ca gộp/tách hợp lý. Khi báo cáo phải ghi rõ đang dùng tập
> nào.

### Hỏi: Vì sao kết hợp IF với XGBoost?

Trả lời:

> IF tạo điểm bất thường không cần nhãn, còn XGBoost học phân loại từ nhãn.
> Điểm IF được đưa thêm vào XGBoost như một feature để model vừa có tín hiệu
> bất thường tổng quát vừa tận dụng nhãn cheated/normal.

### Hỏi: SHAP dùng để làm gì?

Trả lời:

> SHAP giải thích dự đoán của XGBoost. Nó cho biết feature nào làm tăng hoặc
> giảm điểm rủi ro của từng session, và feature nào quan trọng nhất trên toàn
> bộ tập dữ liệu.

### Hỏi: Precision và Recall khác gì nhau?

Trả lời:

> Precision đo trong các ca model báo cheated thì bao nhiêu ca đúng. Recall đo
> trong các ca cheated thật thì model bắt được bao nhiêu. Precision liên quan
> báo nhầm, Recall liên quan bỏ sót.

### Hỏi: Vì sao không chỉ dùng F1?

Trả lời:

> F1 gộp Precision và Recall, nhưng trong bài toán giáo dục cần nhìn riêng FP
> và FN. Báo nhầm sinh viên trung thực và bỏ sót gian lận có ý nghĩa đạo đức
> khác nhau.

### Hỏi: Kết quả PasteTrace có đủ kết luận không?

Trả lời:

> Chưa. PasteTrace quá nhỏ và lệch nhãn, nên chỉ dùng làm kiểm chứng phụ cho
> pipeline. Kết luận chính cần dựa trên bộ dữ liệu FPT nhóm đang thu thập.

---

## 18. Cách tự soi thực hành theo từng bước

### Bước 1: Xem nhãn

Mở:

```text
D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized\normalized\labels.csv
```

Kiểm tra:

- Có bao nhiêu label `1`?
- Có bao nhiêu label `0`?
- Session nào thuộc `original16`?

### Bước 2: Xem một JSON session

Mở:

```text
D:\Desktop\PasteTrace_Normalized\PasteTrace_Normalized\normalized\111_A.json
```

Tự hỏi:

- Event đầu tiên là gì?
- Có bao nhiêu event paste?
- Paste source là `external`, `own`, hay `same_machine`?
- Thời gian `t` có tăng dần không?

### Bước 3: Xem `features.csv`

Mở:

```text
outputs/pastetrace_original16/features.csv
```

Chọn một session rồi đọc:

- `paste_char_ratio`
- `max_paste_chars`
- `event_count`
- `duration_sec`
- `paste_external_chars`

Tập diễn giải bằng lời.

### Bước 4: Xem `predictions.csv`

Mở:

```text
outputs/pastetrace_original16/predictions.csv
```

Tự phân loại:

- label=1, pred_label=1 -> TP.
- label=0, pred_label=1 -> FP.
- label=1, pred_label=0 -> FN.
- label=0, pred_label=0 -> TN.

### Bước 5: Xem `shap_importance.csv`

Mở:

```text
outputs/pastetrace_original16/shap_importance.csv
```

Tự hỏi:

- Top 5 feature là gì?
- Chúng thuộc nhóm gõ, paste, thời gian hay nguồn paste?
- Có feature nào dễ gây báo nhầm sinh viên giỏi không?

---

## 19. Những điều cần cẩn thận khi trình bày

Không nên nói:

> Model phát hiện gian lận chính xác.

Nên nói:

> Model tạo điểm rủi ro hỗ trợ giảng viên xem lại.

Không nên nói:

> Paste từ ngoài chắc chắn là gian lận.

Nên nói:

> Paste từ ngoài là một tín hiệu rủi ro, cần xem trong bối cảnh phiên làm bài.

Không nên nói:

> Kết quả PasteTrace chứng minh mô hình tổng quát tốt.

Nên nói:

> PasteTrace là kiểm chứng phụ vì nhỏ và lệch nhãn; kết luận chính cần data FPT.

Không nên nói:

> SHAP chứng minh nguyên nhân gian lận.

Nên nói:

> SHAP giải thích vì sao model đưa ra dự đoán, không chứng minh nguyên nhân
> thật ngoài đời.

---

## 20. Tóm tắt 1 phút để nói miệng

> Phần của em gồm hai việc. Đầu tiên, em tái cấu trúc dữ liệu PasteTrace gốc về
> một schema hành vi thống nhất. Mỗi phiên là một file JSON gồm các event theo
> thời gian như gõ, dán, cắt, kèm nguồn paste; nhãn được tách riêng trong
> `labels.csv` để tránh rò rỉ nhãn. Việc này giúp cả PasteTrace và data FPT sau
> này dùng chung một pipeline.
>
> Sau đó em xây pipeline IF + XGBoost + SHAP. Từ JSON, em trích feature cấp
> phiên như số event, tỷ lệ ký tự paste, cú paste dài nhất, nguồn paste, khoảng
> nghỉ. Isolation Forest tạo điểm bất thường, XGBoost dùng các feature đó để dự
> đoán rủi ro cheated, còn SHAP giải thích feature nào ảnh hưởng dự đoán. Kết
> quả trên PasteTrace chỉ là kiểm chứng phụ vì data rất nhỏ và lệch nhãn; mục
> tiêu chính là dùng pipeline này để so sánh tiếp với Mamba trên data FPT.

