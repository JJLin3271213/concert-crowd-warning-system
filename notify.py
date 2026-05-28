import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from database import SessionLocal
from models import Alert


def _save_alert_to_db(zone_id, zone_name, congestion_rate, current_count, capacity, venue_name):
    """将预警记录持久化到数据库"""
    try:
        db = SessionLocal()
        level = "red" if congestion_rate >= 80 else "orange" if congestion_rate >= 60 else "yellow"
        message = f"{venue_name} - {zone_name} 拥挤度 {congestion_rate}% ({current_count}/{capacity}人)"
        alert = Alert(zone_id=zone_id, level=level, message=message)
        db.add(alert)
        db.commit()
        db.close()
    except Exception as e:
        print(f"保存预警记录失败: {e}")


def _send_and_save(zone_id, zone_name, congestion_rate, current_count, capacity, venue_name):
    """后台线程：发送邮件 + 持久化预警记录"""
    send_alert_email(zone_name, congestion_rate, current_count, capacity, venue_name)
    _save_alert_to_db(zone_id, zone_name, congestion_rate, current_count, capacity, venue_name)

# 邮件配置（生产环境通过环境变量覆盖）
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "2531458938@qq.com")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "olifyasznblfdjgj")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL", "2531458938@qq.com")

def send_alert_email(zone_name, congestion_rate, current_count, capacity, venue_name=None, custom_message=None):
    """发送拥堵预警邮件或自定义消息"""
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        if custom_message:
            msg['Subject'] = f"【演唱会应急系统】紧急求助通知 - {venue_name}"
            body = custom_message
        else:
            # 拥堵预警模式
            if congestion_rate >= 80:
                level = "严重拥堵"
                color = "#f44336"
            elif congestion_rate >= 60:
                level = "拥堵"
                color = "#FF9800"
            else:
                level = "较堵"
                color = "#FFC107"
            
            venue_text = f"<p><strong>所属场馆：</strong> {venue_name}</p>" if venue_name else ""
            msg['Subject'] = f"【人流预警】{venue_name} - {zone_name} {level}"
            body = f"""
            <html>
            <body>
            <div style="max-width: 600px; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                <h2 style="color: {color};">⚠️ 演唱会人流预警通知</h2>
                <hr>
                {venue_text}
                <p><strong>分区名称：</strong> {zone_name}</p>
                <p><strong>当前人数：</strong> {current_count} 人</p>
                <p><strong>分区容量：</strong> {capacity} 人</p>
                <p><strong>拥挤度：</strong> {congestion_rate}%</p>
                <p><strong>预警时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <hr>
                <p style="color: #f44336;">请及时采取疏导措施！</p>
            </div>
            </body>
            </html>
            """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 使用 587 端口 + TLS
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        print(f"邮件发送成功: {venue_name} - {zone_name}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

# 记录已发送的预警
sent_alerts = {}

def check_and_send_alert(zone_id, zone_name, congestion_rate, current_count, capacity, venue_name=None):
    """检查拥堵等级并发送预警（异步，不阻塞主请求）"""
    from datetime import datetime, timedelta
    import threading

    if congestion_rate >= 80:
        now = datetime.now()
        alert_key = f"{zone_id}_{venue_name}"

        if alert_key in sent_alerts:
            last_time = sent_alerts[alert_key]
            if (now - last_time) < timedelta(minutes=5):
                return

        sent_alerts[alert_key] = now
        # 邮件发送放到后台线程（同时持久化预警记录）
        t = threading.Thread(
            target=_send_and_save,
            args=(zone_id, zone_name, congestion_rate, current_count, capacity, venue_name),
            daemon=True
        )
        t.start()
    else:
        alert_key = f"{zone_id}_{venue_name}"
        if alert_key in sent_alerts:
            del sent_alerts[alert_key]