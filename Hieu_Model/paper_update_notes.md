# Ghi chú cập nhật bài báo

File chính đã cập nhật: `paper_updated_if_xgb_shap.tex`.

## Đã cập nhật

- Thêm abstract sơ bộ dựa trên pipeline IF + XGBoost + SHAP và kết quả PasteTrace.
- Viết rõ hai nguồn dữ liệu:
  - PasteTrace đã tái cấu trúc về schema JSON hành vi.
  - Bộ dữ liệu chính thu tại FPT bằng IDE cấu hình lại từ PasteTrace.
- Bổ sung phần giải thích IF, XGBoost, SHAP và lý do kết hợp ba thành phần.
- Điền kết quả sơ bộ:
  - PasteTrace 16 phiên: Precision 0.867, Recall 0.929, F1 0.897, AUC 0.714.
  - PasteTrace 19 phiên: Precision 0.875, Recall 0.875, F1 0.875, AUC 0.833.
- Bổ sung phân tích SHAP sơ bộ và phân tích lỗi/công bằng.
- Viết lại thảo luận, giới hạn và kết luận theo hướng thận trọng hơn.

## Còn cần nhóm bổ sung

- Số lượng sinh viên/phiên/nhãn của bộ dữ liệu FPT sau khi thu xong.
- Kết quả pipeline IF + XGBoost + SHAP trên bộ FPT.
- Kết quả mô hình Mamba trên cùng fold với pipeline IF + XGBoost + SHAP.
- Chi phí chạy: thời gian train, tài nguyên, số tham số Mamba nếu có.
- Thông tin chính xác của tài liệu tham khảo PasteTrace và Mamba trước khi nộp.
- Nếu có hình pipeline hoặc biểu đồ SHAP, chèn thêm vào phần phương pháp/kết quả.

## Lưu ý diễn giải

PasteTrace rất nhỏ và lệch nhãn, nên chỉ nên gọi là kiểm chứng phụ hoặc case study.
Không nên dùng PasteTrace làm bằng chứng chính rằng mô hình đã tổng quát hóa tốt.
