#!/usr/bin/env python3
"""
秒杀系统高并发模拟脚本
模拟真实2分钟抢购场景
- 每用户最多购买5单
- 用户可以放弃订单
- 可视化实时数据
"""

import requests
import concurrent.futures
import time
import random
import json
from datetime import datetime
from collections import defaultdict

API_URL = "http://localhost:8080"

# 模拟商品数据（从Redis加载或初始化）
def init_products():
    """初始化商品库存"""
    # 设置充足的库存
    products = {
        1: {"name": "iPhone 15 Pro", "stock": 5000, "price": 6999},
        2: {"name": "MacBook Pro", "stock": 2000, "price": 12999},
        3: {"name": "AirPods Pro", "stock": 3000, "price": 999},
        4: {"name": "iPad Pro", "stock": 1500, "price": 4999},
        5: {"name": "Apple Watch", "stock": 2000, "price": 2999},
    }
    for pid, info in products.items():
        requests.get(f"http://localhost:8080/api/product/list")  # 确保后端运行
    return products

# 全局统计
class Stats:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.total_requests = 0
        self.success = 0
        self.failed = 0
        self.no_stock = 0
        self.duplicate = 0
        self.qps_history = []
        self.user_orders = defaultdict(list)  # 用户订单
        self.max_orders_per_user = 5
        self.abandoned_orders = []  # 放弃的订单

stats = Stats()

def seckill_request(user_id, product_id):
    """发起秒杀请求"""
    try:
        start = time.time()
        response = requests.post(
            f"{API_URL}/api/seckill/{product_id}",
            headers={"userId": str(user_id)},
            timeout=10
        )
        elapsed = (time.time() - start) * 1000
        
        result = response.json()
        
        # 检查用户购买上限
        if len(stats.user_orders[user_id]) >= stats.max_orders_per_user:
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': 403,
                'message': '已达购买上限(5单)',
                'elapsed': elapsed
            }
        
        if result.get('code') == 200:
            order_no = result.get('data')
            stats.user_orders[user_id].append({
                'order_no': order_no,
                'product_id': product_id,
                'time': datetime.now().isoformat()
            })
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': 200,
                'message': '秒杀成功',
                'order_no': order_no,
                'elapsed': elapsed
            }
        elif '已秒杀过' in result.get('message', ''):
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': 201,
                'message': '重复秒杀',
                'elapsed': elapsed
            }
        else:
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': result.get('code'),
                'message': result.get('message', '失败'),
                'elapsed': elapsed
            }
    except Exception as e:
        return {
            'user_id': user_id,
            'product_id': product_id,
            'error': str(e)
        }

def user_abandon_order(user_id, order_index=-1):
    """用户放弃订单（模拟）"""
    if user_id in stats.user_orders and stats.user_orders[user_id]:
        order = stats.user_orders[user_id].pop(order_index)
        stats.abandoned_orders.append(order)
        return True
    return False

def simulate_scenario(duration_seconds=120, total_users=500):
    """
    模拟抢购场景
    duration_seconds: 抢购持续时间（秒）
    total_users: 参与用户数
    """
    print(f"\n{'='*70}")
    print(f"🛒 模拟真实抢购场景")
    print(f"{'='*70}")
    print(f"抢购时长:   {duration_seconds} 秒")
    print(f"参与用户:   {total_users} 人")
    print(f"每用户限购: {stats.max_orders_per_user} 单")
    print(f"{'='*70}")
    
    # 重置
    stats.reset()
    
    # 初始化库存
    print("\n📦 初始化商品库存...")
    import subprocess
    subprocess.run(['redis-cli', 'SET', 'seckill:stock:1', '5000'])
    subprocess.run(['redis-cli', 'SET', 'seckill:stock:2', '2000'])
    subprocess.run(['redis-cli', 'SET', 'seckill:stock:3', '3000'])
    subprocess.run(['redis-cli', 'SET', 'seckill:stock:4', '1500'])
    subprocess.run(['redis-cli', 'SET', 'seckill:stock:5', '2000'])
    
    # 显示初始库存
    for pid in range(1, 6):
        stock = subprocess.run(['redis-cli', 'GET', f'seckill:stock:{pid}'], 
                              capture_output=True, text=True).stdout.strip()
        print(f"  商品{pid}: {stock} 件")
    
    print(f"\n🚀 抢购开始！倒计时 {duration_seconds} 秒...")
    print("-" * 70)
    
    start_time = time.time()
    last_print = start_time
    user_idx = 0
    
    # 持续模拟用户请求
    while time.time() - start_time < duration_seconds:
        current_time = time.time()
        elapsed = current_time - start_time
        
        # 模拟并发用户（每批100个用户同时点击）
        batch_size = 100
        product_id = random.randint(1, 5)
        
        # 每批用户同时发起请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            for i in range(batch_size):
                user_id = 50000 + user_idx + i  # 用户ID从50000开始
                futures.append(executor.submit(seckill_request, user_id, product_id))
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                stats.total_requests += 1
                
                if result.get('code') == 200:
                    stats.success += 1
                else:
                    stats.failed += 1
                    if '库存' in result.get('message', ''):
                        stats.no_stock += 1
                    elif '重复' in result.get('message', ''):
                        stats.duplicate += 1
        
        user_idx += batch_size
        
        # 每秒打印一次状态
        if current_time - last_print >= 1:
            # 计算当前QPS
            current_qps = stats.total_requests / elapsed if elapsed > 0 else 0
            print(f"[{int(elapsed):3d}s] 总请求: {stats.total_requests:5d} | "
                  f"成功: {stats.success:4d} | 失败: {stats.failed:4d} | "
                  f"QPS: {current_qps:6.1f} | 用户: {len(stats.user_orders)}")
            last_print = current_time
        
        # 模拟用户抢购间隔（0.1秒）
        time.sleep(0.1)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # 模拟部分用户放弃订单（10%概率）
    print("\n📝 模拟用户放弃订单...")
    users_who_abandon = 0
    for user_id in list(stats.user_orders.keys())[:int(len(stats.user_orders) * 0.1)]:
        if user_abandon_order(user_id):
            users_who_abandon += 1
    
    return generate_report(duration, total_users)

def generate_report(duration, total_users):
    """生成测试报告"""
    total = stats.total_requests
    success = stats.success
    failed = stats.failed
    
    # 唯一用户数
    unique_users = len(stats.user_orders)
    
    # 订单统计
    total_orders = sum(len(orders) for orders in stats.user_orders.values())
    users_with_5_orders = sum(1 for orders in stats.user_orders.values() if len(orders) >= 5)
    
    print(f"\n{'='*70}")
    print(f"📊 抢购模拟结果")
    print(f"{'='*70}")
    print(f"抢购时长:     {duration:.1f} 秒")
    print(f"总请求数:     {total}")
    print(f"成功下单:     {success} ({success*100//max(total,1)}%)")
    print(f"失败请求:     {failed} ({failed*100//max(total,1)}%)")
    print(f"  - 库存不足: {stats.no_stock}")
    print(f"  - 重复秒杀: {stats.duplicate}")
    print(f"QPS:          {total/duration:.1f}")
    print(f"\n👥 用户统计:")
    print(f"  参与用户:   {unique_users}")
    print(f"  总订单数:   {total_orders}")
    print(f"  购满5单用户: {users_with_5_orders}")
    print(f"  放弃订单:   {len(stats.abandoned_orders)}")
    print(f"{'='*70}")
    
    # 生成可视化HTML
    generate_html_report(duration, unique_users, users_with_5_orders)
    
    return stats

def generate_html_report(duration, unique_users, users_with_5_orders):
    """生成HTML可视化报告"""
    # 获取库存数据
    import subprocess
    stocks = []
    for pid in range(1, 6):
        stock = subprocess.run(['redis-cli', 'GET', f'seckill:stock:{pid}'], 
                              capture_output=True, text=True).stdout.strip()
        stocks.append(int(stock) if stock else 0)
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>秒杀系统抢购模拟报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); min-height: 100vh; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        h1 {{ color: #fff; text-align: center; font-size: 36px; margin-bottom: 10px; }}
        .subtitle {{ color: #aaa; text-align: center; margin-bottom: 30px; }}
        
        .summary {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 30px 0; }}
        .card {{ background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 25px; border-radius: 15px; min-width: 180px; text-align: center; border: 1px solid rgba(255,255,255,0.2); }}
        .card h3 {{ margin: 0 0 10px 0; color: #aaa; font-size: 14px; text-transform: uppercase; }}
        .card .value {{ font-size: 42px; font-weight: bold; color: #fff; }}
        .card.success .value {{ color: #4caf50; }}
        .card.failed .value {{ color: #f44336; }}
        .card.qps .value {{ color: #2196f3; }}
        .card.users .value {{ color: #ff9800; }}
        .card.orders .value {{ color: #9c27b0; }}
        
        .section {{ background: rgba(255,255,255,0.05); border-radius: 15px; padding: 25px; margin: 20px 0; }}
        .section h2 {{ color: #fff; margin-top: 0; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; }}
        
        .chart-row {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .chart-box {{ flex: 1; min-width: 400px; background: rgba(0,0,0,0.2); border-radius: 10px; padding: 20px; }}
        
        .stat-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .stat-item {{ background: rgba(255,255,255,0.1); padding: 15px; border-radius: 8px; }}
        .stat-item .label {{ color: #aaa; font-size: 12px; }}
        .stat-item .value {{ color: #fff; font-size: 24px; font-weight: bold; }}
        
        .product-table {{ width: 100%; border-collapse: collapse; color: #fff; }}
        .product-table th, .product-table td {{ padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .product-table th {{ color: #aaa; font-weight: normal; }}
        .product-table tr:hover {{ background: rgba(255,255,255,0.05); }}
        
        .user-examples {{ background: rgba(0,0,0,0.2); border-radius: 10px; padding: 20px; margin-top: 20px; }}
        .user-examples h3 {{ color: #fff; margin-top: 0; }}
        .order-list {{ display: flex; flex-wrap: wrap; gap: 10px; }}
        .order-tag {{ background: rgba(76,175,80,0.2); color: #4caf50; padding: 5px 12px; border-radius: 20px; font-size: 12px; }}
        
        .warning {{ background: rgba(255,152,0,0.2); border: 1px solid #ff9800; border-radius: 10px; padding: 15px; margin: 20px 0; color: #ff9800; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ 秒杀系统抢购模拟报告</h1>
        <div class="subtitle">测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="summary">
            <div class="card">
                <h3>总请求</h3>
                <div class="value">{stats.total_requests:,}</div>
            </div>
            <div class="card success">
                <h3>成功下单</h3>
                <div class="value">{stats.success:,}</div>
            </div>
            <div class="card failed">
                <h3>失败请求</h3>
                <div class="value">{stats.failed:,}</div>
            </div>
            <div class=" card qps">
                <h3>QPS</h3>
                <div class="value">{stats.total_requests/duration:.0f}</div>
            </div>
            <div class="card users">
                <h3>参与用户</h3>
                <div class="value">{unique_users:,}</div>
            </div>
            <div class="card orders">
                <h3>总订单</h3>
                <div class="value">{sum(len(o) for o in stats.user_orders.values()):,}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📦 商品库存剩余</h2>
            <table class="product-table">
                <tr><th>商品ID</th><th>商品名</th><th>抢购后剩余</th></tr>
                <tr><td>1</td><td>iPhone 15 Pro</td><td>{stocks[0]:,}</td></tr>
                <tr><td>2</td><td>MacBook Pro</td><td>{stocks[1]:,}</td></tr>
                <tr><td>3</td><td>AirPods Pro</td><td>{stocks[2]:,}</td></tr>
                <tr><td>4</td><td>iPad Pro</td><td>{stocks[3]:,}</td></tr>
                <tr><td>5</td><td>Apple Watch</td><td>{stocks[4]:,}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>📈 抢购数据分析</h2>
            <div class="stat-grid">
                <div class="stat-item">
                    <div class="label">成功率</div>
                    <div class="value">{stats.success*100//max(stats.total_requests,1)}%</div>
                </div>
                <div class="stat-item">
                    <div class="label">库存不足</div>
                    <div class="value">{stats.no_stock:,}</div>
                </div>
                <div class="stat-item">
                    <div class="label">重复秒杀</div>
                    <div class="value">{stats.duplicate:,}</div>
                </div>
                <div class="stat-item">
                    <div class="label">购满5单用户</div>
                    <div class="value">{users_with_5_orders}</div>
                </div>
                <div class="stat-item">
                    <div class="label">放弃订单</div>
                    <div class="value">{len(stats.abandoned_orders)}</div>
                </div>
                <div class="stat-item">
                    <div class="label">平均订单/用户</div>
                    <div class="value">{sum(len(o) for o in stats.user_orders.values())/max(unique_users,1):.1f}</div>
                </div>
            </div>
        </div>
        
        <div class="warning">
            ⚠️ 每位用户限购 <strong>5单</strong>，已购满5单的用户将无法继续下单
        </div>
        
        <div class="user-examples">
            <h3>👤 部分用户订单示例（购满5单的用户）</h3>
            <div class="order-list">
"""
    
    # 添加用户示例
    users_with_max = [(uid, orders) for uid, orders in stats.user_orders.items() if len(orders) >= 5]
    for uid, orders in users_with_max[:10]:
        for order in orders:
            html += f'<div class="order-tag">用户{uid}: 商品{order["product_id"]}</div>'
    
    html += f"""
            </div>
        </div>
    </div>
</body>
</html>
    """
    
    with open('/home/dev/seckill-system/frontend/public/stress_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n📄 可视化报告: http://localhost:8081/stress_report.html")

if __name__ == "__main__":
    import sys
    
    duration = 60  # 默认60秒
    users = 500   # 默认500用户
    
    if len(sys.argv) > 1:
        duration = int(sys.argv[1])
    if len(sys.argv) > 2:
        users = int(sys.argv[2])
    
    simulate_scenario(duration, users)
