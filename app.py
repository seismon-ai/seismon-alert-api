from flask import Flask, request, jsonify
import pandas as pd

# 事前にアップロードした risk_grid.csv を読み込む
risk_data = pd.read_csv("risk_grid.csv")

app = Flask(__name__)

def get_grid(lat, lon):
    # 緯度経度を最寄りの整数グリッドに丸め
    return round(lat), round(lon)

def calculate_alert_level(score):
    if score >= 0.5:
        return "高"
    elif score >= 0.2:
        return "中"
    return "低"

@app.route("/risk-alert")
def risk_alert():
    lat = float(request.args.get("lat"))
    lon = float(request.args.get("lon"))
    previous = request.args.get("previous")

    lat_bin, lon_bin = get_grid(lat, lon)
    row = risk_data[
        (risk_data["lat_bin"] == lat_bin) & 
        (risk_data["lon_bin"] == lon_bin)
    ]
    if row.empty:
        return jsonify({"error": "Location out of range"}), 404

    score = float(row["risk_score"].values[0])
    current_level = calculate_alert_level(score)
    should_notify = (current_level != previous)

    message = ""
    if should_notify:
        message = f"地震リスクが上昇しています。警戒レベルが『{current_level}』に変わりました。"

    return jsonify({
        "risk_score": round(score, 2),
        "alert_level": current_level,
        "should_notify": should_notify,
        "message": message
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
