import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# 邮件配置（已配置你的QQ邮箱）
SMTP_SERVER = "smtp.qq.com"
SMTP_PORT = 465
SENDER_EMAIL = "2531458938@qq.com"
SENDER_PASSWORD = "olifyasznblfdjgj"
RECEIVER_EMAIL = "2531458938@qq.com"  # 接收预警的邮箱（可改成其他邮箱）

def send_alert_email(zone_name, congestion_rate, current_count, capacity, venue_name=None, custom_message=None):
    """
    发送拥堵预警邮件或自定义消息
    - zone_name: 分区名称
    - congestion_rate: 拥挤度百分比
    - current_count: 当前人数
    - capacity: 容量
    - venue_name: 场馆名称
    - custom_message: 自定义消息（用于应急求助等场景）
    """
    try:
        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL
        
        if custom_message:
            # 应急求助模式
            msg['Subject'] = f"【演唱会应急系统】紧急求助通知 - {venue_name}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    {custom_message}
                    <hr>
                    <p style="color: #666; font-size: 12px;">请立即处理！</p>
                    <p style="color: #999; font-size: 11px;">本邮件由演唱会人流预警系统自动发送</p>
                </div>
            </body>
            </html>
            """
        else:
            # 拥堵预警模式
            if congestion_rate >= 80:
                level = "🔴 严重拥堵"
                color = "#f44336"
            elif congestion_rate >= 60:
                level = "🟠 拥堵"
                color = "#FF9800"
            elif congestion_rate >= 40:
                level = "🟡 较堵"
                color = "#FFC107"
            else:
                level = "🟢 畅通"
                color = "#4CAF50"
            
            venue_text = f"<p><strong>所属场馆：</strong> {venue_name}</p>" if venue_name else ""
            msg['Subject'] = f"【人流预警】{venue_name} - {zone_name} {level}"
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: {color};">⚠️ 演唱会人流预警通知</h2>
                    <hr>
                    {venue_text}
                    <p><strong>分区名称：</strong> {zone_name}</p>
                    <p><strong>当前人数：</strong> {current_count} 人</p>
                    <p><strong>分区容量：</strong> {capacity} 人</p>
                    <p><strong>拥挤度：</strong> {congestion_rate}%</p>
                    <p><strong>预警等级：</strong> <span style="color: {color};">{level}</span></p>
                    <p><strong>预警时间：</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <hr>
                    <p style="color: #f44336; font-weight: bold;">请及时采取疏导措施！</p>
                    <p style="color: #999; font-size: 11px;">本邮件由演唱会人流预警系统自动发送</p>
                </div>
            </body>
            </html>
            """
        
        msg.attach(MIMEText(body, 'html', 'utf-8'))
        
        # 发送邮件
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        
        if custom_message:
            print(f"应急求助邮件已发送: {venue_name} - {zone_name}")
        else:
            print(f"预警邮件已发送: {venue_name} - {zone_name} 拥挤度 {congestion_rate}%")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False

# 记录已发送的预警，避免重复发送
sent_alerts = {}

def check_and_send_alert(zone_id, zone_name, congestion_rate, current_count, capacity, venue_name=None):
    """检查拥堵等级并发送预警"""
    from datetime import datetime, timedelta
    
    # 只有红色（严重拥堵，>=80%）才发送预警
    if congestion_rate >= 80:
        # 检查是否在5分钟内已经发送过预警
        now = datetime.now()
        alert_key = f"{zone_id}_{venue_name}" if venue_name else str(zone_id)
        if alert_key in sent_alerts:
            last_time = sent_alerts[alert_key]
            if (now - last_time) < timedelta(minutes=5):
                return  # 5分钟内不重复发送
        
        # 发送预警
        success = send_alert_email(zone_name, congestion_rate, current_count, capacity, venue_name)
        if success:
            sent_alerts[alert_key] = now
    else:
        # 拥堵等级降低时，重置预警记录
        alert_key = f"{zone_id}_{venue_name}" if venue_name else str(zone_id)
        if alert_key in sent_alerts:
            del sent_alerts[alert_key]