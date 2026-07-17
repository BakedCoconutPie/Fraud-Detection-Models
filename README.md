# Fraud Detection Models

Kho lưu trữ này gộp mã nguồn từ 2 nhánh nghiên cứu phát hiện gian lận học thuật:
- **Viet_Model**: Mô hình Mamba phân tích theo chuỗi dữ liệu (Sequence Model).
- **Hieu_Model**: Mô hình kinh điển (Isolation Forest + XGBoost + SHAP).

## Hướng dẫn chạy

### 1. Mô hình của anh Việt (Viet_Model / Mamba)
Yêu cầu thư viện: xem trong `Viet_Model/requirements.txt` và `Viet_Model/requirements-mamba.txt`.

Cách chạy trên Terminal/Command Prompt (chú ý `cd` vào thư mục `Viet_Model` trước):
```bash
cd Viet_Model
python -m src.data.build_sequences --min-events 1
python -m src.data.make_splits
python -m src.models.mamba_model train --epochs 80 --patience 10 --lr 3e-4 --batch-size 8 --seed 42
python -m src.models.mamba_model test
```

### 2. Mô hình của anh Hiếu (Hieu_Model / IF + XGBoost)
Yêu cầu thư viện: xem trong `Hieu_Model/requirements.txt`.

Trong thư mục `Hieu_Model` đã có sẵn các script PowerShell để chạy tự động.
Mở PowerShell và chạy:
```powershell
cd Hieu_Model
./scripts/run_all_experiments.ps1
```
Hoặc để chạy riêng lẻ mô hình:
```powershell
./scripts/run_if_xgb_shap.ps1
```

> **Lưu ý:** Để hiểu chi tiết hơn về cách thức hoạt động, data pipeline và giải thích kết quả, bạn hãy xem các file `README.md` riêng biệt đã được viết rất kỹ nằm ở bên trong từng thư mục `Viet_Model` và `Hieu_Model` nhé.
