import efinance as ef
from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = "randomstring12345"  # 非必需，但建议保留（避免 future warning）

def get_stock_data(
    quantity_ratio_min,
    quantity_ratio_max,
    change_min,
    change_max
):
    df = ef.stock.get_realtime_quotes()
    # 清洗“量比”列：去除“-”，转为 float
    df['量比'] = df['量比'].astype(str).str.replace("-", "0").astype(float)
    # 清洗“换手率”列：去除“%”，转为 float
    df['换手率'] = df['换手率'].astype(str).str.rstrip('%').astype(float)

    selected = df[
        (df['量比'] >= quantity_ratio_min) &
        (df['量比'] <= quantity_ratio_max) &
        (df['换手率'] >= change_min) &
        (df['换手率'] <= change_max)
    ]

    # 排序 + 选择指定列
    selected = selected.sort_values(by='量比', ascending=False)
    selected = selected[["股票代码", "股票名称", "换手率", "量比", "涨跌幅", "流通市值", "更新时间"]]

    return selected

@app.route("/api/stock", methods=["GET", "POST"])
@app.route("/api/stock", methods=["GET", "POST"])
def get_stock():
    def get_float_param(name, default=0.0):
        val = request.args.get(name) or request.form.get(name)
        return float(val) if val is not None else default

    quantity_ratio_min = get_float_param('quantity_ratio_min', 0.0)
    quantity_ratio_max = get_float_param('quantity_ratio_max', 0.0)
    up_min = get_float_param('up_min', 10.0)
    up_max = get_float_param('up_max', 12.0)

    try:
        filtered_df = get_stock_data(quantity_ratio_min, quantity_ratio_max, up_min, up_max)
        # ✅ 兼容旧版 pandas：使用 to_dict + jsonify 自动序列化
        result = filtered_df.to_dict(orient="records")
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        pass  # 确保 db.create_all() 已执行（如有）
    print("✅ 服务启动中... 访问 http://127.0.0.1:5001/api/stock")
    app.run(host="0.0.0.0", port=5001, debug=True)


