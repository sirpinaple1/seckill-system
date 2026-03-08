#!/usr/bin/env python3
"""
秒杀系统高并发测试脚本
- 可视化数据展示
- 每个用户最多购买5单
- 支持放弃订单
"""

import requests
import concurrent.futures
import time
import random
import json
from datetime import datetime
from collections import defaultdict

API_URL = "http://localhost:8080"
PRODUCT_IDS = [1, 2, 3, 4, 5]

# 统计数据
stats = {
    "total_requests": 0,
    "success": 0,
    "failed": 0,
    "no_stock": 0,
    "duplicate": 0,
    "qps_history": [],
    "response_times": [],
    "user_orders": defaultdict(list),  # 用户订单记录
    "max_orders_per_user": 5,
}

# 模拟用户放弃订单
abandoned_orders = []

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
        
        # 检查用户是否已达购买上限
        if len(stats["user_orders"][user_id]) >= stats["max_orders_per_user"]:
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': 403,
                'message': '用户购买上限已达(5单)',
                'elapsed': elapsed
            }
        
        if result.get('code') == 200:
            order_no = result.get('data')
            stats["user_orders"][user_id].append({
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
            stats["duplicate"] += 1
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': 201,
                'message': '重复秒杀',
                'elapsed': elapsed
            }
        elif '库存不足' in result.get('message', '') or '秒杀已结束' in result.get('message', ''):
            stats["no_stock"] += 1
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': 202,
                'message': '库存不足',
                'elapsed': elapsed
            }
        else:
            stats["failed"] += 1
            return {
                'user_id': user_id,
                'product_id': product_id,
                'code': result.get('code'),
                'message': result.get('message', '未知错误'),
                'elapsed': elapsed
            }
    except Exception as e:
        stats["failed"] += 1
        return {
            'user_id': user_id,
            'product_id': product_id,
            'error': str(e)
        }

def abandon_order(user_id, order_index=None):
    """用户放弃订单"""
    if user_id in stats["user_orders"] and stats["user_orders"][user_id]:
        if order_index is None:
            order = stats["user_orders"][user_id].pop()
        else:
            order = stats["user_orders"][user_id].pop(order_index)
        abandoned_orders.append(order)
        return True
    return False

def get_order_count(user_id):
    """获取用户订单数"""
    return len(stats["user_orders"].get(user_id, []))

def run_concurrent_test(total_requests=1000, concurrency=100, product_id=1):
    """运行并发测试"""
    print(f"\n{'='*60}")
    print(f"🚀 高并发秒杀测试开始")
    print(f"{'='*60}")
    print(f"总请求数:   {total_requests}")
    print(f"并发数:     {concurrency}")
    print(f"商品ID:     {product_id}")
    print(f"每用户限购: {stats['max_orders_per_user']}单")
    print(f"{'='*60}\n")
    
    # 重置统计
    stats["total_requests"] = 0
    stats["success"] = 0
    stats["failed"] = 0
    stats["no_stock"] = 0
    stats["duplicate"] = 0
    stats["qps_history"] = []
    stats["response_times"] = []
    stats["user_orders"].clear()
    abandoned_orders.clear()
    
    start_time = time.time()
    success_count = 0
    failed_count = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        # 分批提交任务，每批100个
        batch_size = 100
        for batch_start in range(0, total_requests, batch_size):
            batch_end = min(batch_start + batch_size, total_requests)
            tasks = []
            
            for i in range(batch_start, batch_end):
                user_id = 10000 + i  # 用户ID从10000开始
                tasks.append((user_id, product_id))
            
            # 记录QPS
            batch_start_time = time.time()
            
            futures = [executor.submit(seckill_request, uid, pid) for uid, pid in tasks]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                stats["total_requests"] += 1
                stats["response_times"].append(result.get('elapsed', 0))
                
                if result.get('code') == 200:
                    success_count += 1
                    stats["success"] += 1
                else:
                    failed_count += 1
            
            batch_elapsed = time.time() - batch_start_time
            current_qps = batch_size / batch_elapsed if batch_elapsed > 0 else 0
            stats["qps_history"].append({
                'time': time.time() - start_time,
                'qps': current_qps,
                'success': success_count,
                'failed': failed_count
            })
            
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] 已完成: {stats['total_requests']}/{total_requests}, "
                  f"成功: {success_count}, 失败: {failed_count}, QPS: {current_qps:.1f}")
    
    end_time = time.time()
    total_elapsed = end_time - start_time
    
    return generate_report(total_elapsed)

def generate_report(duration):
    """生成测试报告"""
    total = stats["total_requests"]
    success = stats["success"]
    failed = stats["failed"]
    no_stock = stats["no_stock"]
    duplicate = stats["duplicate"]
    
    # 计算响应时间统计
    if stats["response_times"]:
        response_times = sorted(stats["response_times"])
        avg_rt = sum(response_times) / len(response_times)
        p50 = response_times[len(response_times) // 2]
        p90 = response_times[int(len(response_times) * 0.9)]
        p99 = response_times[int(len(response_times) * 0.99)]
        min_rt = min(response_times)
        max_rt = max(response_times)
    else:
        avg_rt = p50 = p90 = p99 = min_rt = max_rt = 0
    
    # 唯一用户数
    unique_users = len(stats["user_orders"])
    
    print(f"\n{'='*60}")
    print(f"📊 高并发测试报告")
    print(f"{'='*60}")
    print(f"测试时长:     {duration:.2f} 秒")
    print(f"总请求数:     {total}")
    print(f"总成功数:     {success} ({success*100//max(total,1)}%)")
    print(f"总失败数:     {failed} ({failed*100//max(total,1)}%)")
    print(f"  - 库存不足: {no_stock}")
    print(f"  - 重复秒杀: {duplicate}")
    print(f"  - 其他失败: {failed - no_stock - duplicate}")
    print(f"QPS:          {total/duration:.2f}")
    print(f"\n📈 响应时间统计:")
    print(f"  平均:       {avg_rt:.2f} ms")
    print(f"  最小:       {min_rt:.2f} ms")
    print(f"  最大:       {max_rt:.2f} ms")
    print(f"  P50:        {p50:.2f} ms")
    print(f"  P90:        {p90:.2f} ms")
    print(f"  P99:        {p99:.2f} ms")
    print(f"\n👥 用户统计:")
    print(f"  参与用户:   {unique_users}")
    print(f"  限购:       每用户最多{stats['max_orders_per_user']}单")
    print(f"  放弃订单:   {len(abandoned_orders)}")
    print(f"{'='*60}")
    
    # 生成HTML可视化报告
    generate_html_report(duration)
    
    return stats

def generate_html_report(duration):
    """生成HTML可视化报告"""
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>秒杀系统高并发测试报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; text-align: center; }}
        .summary {{ display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 20px 0; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); min-width: 200px; text-align: center; }}
        .card h3 {{ margin: 0 0 10px 0; color: #666; font-size: 14px; }}
        .card .value {{ font-size: 32px; font-weight: bold; color: #333; }}
        .card.success .value {{ color: #4caf50; }}
        .card.failed .value {{ color: #f44336; }}
        .card.qps .value {{ color: #2196f3; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .info {{ text-align: center; color: #666; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ 秒杀系统高并发测试报告</h1>
        <div class="info">测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        
        <div class="summary">
            <div class="card">
                <h3>总请求数</h3>
                <div class="value">{stats['total_requests']}</div>
            </div>
            <div class="card success">
                <h3>成功</h3>
                <div class="value">{stats['success']}</div>
            </div>
            <div class="card failed">
                <h3>失败</h3>
                <div class="value">{stats['failed']}</div>
            </div>
            <div class="card qps">
                <h3>QPS</h3>
                <div class="value">{stats['total_requests']/duration:.1f}</div>
            </div>
        </div>
        
        <div class="chart-container">
            <canvas id="qpsChart" height="100"></canvas>
        </div>
        
        <div class="chart-container">
            <canvas id="resultChart" height="80"></canvas>
        </div>
        
        <div class="summary">
            <div class="card">
                <h3>库存不足</h3>
                <div class="value">{stats['no_stock']}</div>
            </div>
            <div class="card">
                <h3>重复秒杀</h3>
                <div class="value">{stats['duplicate']}</div>
            </div>
            <div class="card">
                <h3>参与用户</h3>
                <div class="value">{len(stats['user_orders'])}</div>
            </div>
            <div class="card">
                <h3>放弃订单</h3>
                <div class="value">{len(abandoned_orders)}</div>
            </div>
        </div>
    </div>
    
    <script>
        // QPS趋势图
        new Chart(document.getElementById('qpsChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps([round(d['time'], 1) for d in stats['qps_history']])},
                datasets: [{{
                    label: 'QPS',
                    data: {json.dumps([round(d['qps'], 1) for d in stats['qps_history']])},
                    borderColor: '#2196f3',
                    backgroundColor: 'rgba(33, 150, 243, 0.1)',
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ title: {{ display: true, text: 'QPS 趋势图' }} }},
                scales: {{ y: {{ beginAtZero: true }} }}
            }}
        }});
        
        // 结果分布图
        new Chart(document.getElementById('resultChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['成功', '库存不足', '重复秒杀', '其他失败'],
                datasets: [{{
                    data: [{stats['success']}, {stats['no_stock']}, {stats['duplicate']}, {stats['failed'] - stats['no_stock'] - stats['duplicate']}],
                    backgroundColor: ['#4caf50', '#f44336', '#ff9800', '#9e9e9e']
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{ title: {{ display: true, text: '请求结果分布' }} }}
            }}
        }});
    </script>
</body>
</html>
    """
    
    with open('/home/dev/seckill-system/test_report.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n📄 可视化报告已生成: /home/dev/seckill-system/test_report.html")
    print(f"   可在浏览器中打开查看图表")

if __name__ == "__main__":
    import sys
    
    # 默认参数
    total_requests = 1000
    concurrency = 100
    product_id = 1
    
    if len(sys.argv) > 1:
        total_requests = int(sys.argv[1])
    if len(sys.argv) > 2:
        concurrency = int(sys.argv[2])
    if len(sys.argv) > 3:
        product_id = int(sys.argv[3])
    
    run_concurrent_test(total_requests, concurrency, product_id)
