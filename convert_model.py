#!/usr/bin/env python3
"""
モデル変換スクリプト
PyTorchモデルをONNX + INT8量子化に変換
"""
import os
import torch
from transformers import AutoTokenizer, AutoModel
from optimum.onnxruntime import ORTModelForFeatureExtraction, ORTQuantizer
from optimum.exporters.onnx import main_export

def convert_model():
    """モデルをONNX + INT8量子化に変換"""
    model_id = "oshizo/sbert-jsnli-luke-japanese-base-lite"
    output_dir = "onnx_model"
    
    print(f"🚀 モデル変換開始: {model_id}")
    
    # 出力ディレクトリ作成
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 1. モデルとトークナイザー読み込み
        print("📥 モデルとトークナイザー読み込み中...")
        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModel.from_pretrained(model_id)
        
        # 2. ONNXにエクスポート
        print("🔄 ONNXエクスポート中...")
        onnx_model = ORTModelForFeatureExtraction.from_pretrained(
            model_id, 
            export=True,
            provider="CPUExecutionProvider"
        )
        
        # 3. INT8量子化
        print("🔢 INT8量子化中...")
        quantizer = ORTQuantizer.from_pretrained(model_id)
        quantizer.quantize(
            save_dir=output_dir,
            calibration_tensors=[],
            per_channel=False,
            reduce_range=False,
            use_symmetric_quantization=False,
            num_samples=100
        )
        
        # 4. トークナイザー保存
        print("💾 トークナイザー保存中...")
        tokenizer.save_pretrained(output_dir)
        
        # 5. 変換後モデル保存
        onnx_model.save_pretrained(output_dir)
        
        print(f"✅ 変換完了！保存先: {output_dir}")
        print(f"📊 ファイル一覧:")
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            print(f"  📄 {file} ({size:.1f}MB)")
            
    except Exception as e:
        print(f"❌ 変換失敗: {e}")
        raise

if __name__ == "__main__":
    convert_model()
