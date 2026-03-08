#!/usr/bin/env python3
"""
秒杀系统压测脚本
模拟高并发场景
"""

import requests
import concurrent.futures
import time
import random

API_URL = "http://localhost:8080/api/seckill"

# 商品ID
PRODUCT_IDS = [1, 2, 3]

# 用户ID范围
USER_ID_START = 1000

def seckill_request(user_id, product_id):
    """发起秒杀请求"""
    try:
        start = time.time()
        response = requests.post(
            f"{API_URL}/{product_id}",
            headers={"userId": str(user_id)},
            timeout=5
        )
        elapsed = (time.time() - start) * 1000  # 毫秒
        
        result = response.json()
        return {
            'user_id': user_id,
            'product_id': product_id,
            'status': response.status_code,
            'code': result.get('code'),
            'message': result.get('message', ''),
            'elapsed': elapsed
        }
    except Exception as e:
        return {
            'user_id': user_id,
            'product_id': product_id,
            'error': str(e)
        }

def run_pressure_test(total_requests=1000, concurrency=100, product_id=1):
    """
    运行压测
    
    Args:
        total_requests: 总请求数
        concurrency: 并发数
        product_id: 商品ID
    """
    print(f"\n{'='*50}")
    print(f"🚀 秒杀系统压测开始")
    print(f"{'='*50}")
    print(f"总请求数: {total_requests}")
    print(f"并发数:   {concurrency}")
    print(f"商品ID:   {product_id}")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    
    # 准备请求参数
    tasks = []
    for i in range(total_requests):
        user_id = USER_ID_START + i
        tasks.append((user_id, product_id))
    
    # 并发执行
    results = []
    success = 0
    failed = 0
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(seckill_request, uid, pid) for uid, pid in tasks]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            results.append(result)
            
            if result.get('code') == 200:
                success += 1
            else:
                failed += 1
            
            # 进度显示
            if (i + 1) % 100 == 0:
                print(f"进度: {i+1}/{total_requests} ({(i+1)*100//total_requests}%)")
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # 统计结果
    print(f"\n{'='*50}")
    print(f"📊 压测结果")
    print(f"{'='*50}")
    print(f"总耗时:     {elapsed:.2f} 秒")
    print(f"QPS:        {total_requests/elapsed:.2f} 请求/秒")
    print(f"成功:       {success} ({success*100//total_requests}%)")
    print(f"失败:       {failed} ({failed*100//total_requests}%)")
    print(f"{'='*50}")
    
    return results

def run_continuous_test(duration=60, concurrency=100, product_id=1):
    """
    持续压测
    
    Args:
        duration: 持续时间(秒)
        concurrency: 并发数
        product_id: 商品ID
    """
    print(f"\n{'='*50}")
    print(f"🚀 持续压测开始")
    print(f"{'='*50}")
    print(f"持续时间: {duration} 秒")
    print(f"并发数:   {concurrency}")
    print(f"商品ID:   {product_id}")
    print(f"{'='*50}\n")
    
    start_time = time.time()
    success = 0
    failed = 0
    total = 0
    
    while time.time() - start_time < duration:
        # 每批并发请求
        batch_size = concurrency
        user_id = USER_ID_START + total
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = [executor.submit(seckill_request, user_id + i, product_id) 
                      for i in range(batch_size)]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result.get('code') == 200:
                    success += 1
                else:
                    failed += 1
                total += 1
        
        elapsed = time.time() - start_time
        print(f"[{elapsed:.0f}s] 总请求: {total}, 成功: {success}, 失败: {failed}, QPS: {total/elapsed:.1f}")
        
        time.sleep(0.1)  # 短暂休息
    
    print(f"\n{'='*50}")
    print(f"📊 持续压测完成")
    print(f"总请求: {total}")
    print(f"成功:   {success}")
    print(f"失败:   {failed}")
    print(f"QPS:    {total/duration:.2f}")
    print(f"{'='*50}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "burst":
            # 突发压测
            total = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
            conc = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            run_pressure_test(total, conc)
            
        elif mode == "continuous":
            # 持续压测
            duration = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            conc = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            run_continuous_test(duration, conc)
        else:
            print("用法:")
            print("  python3 seckill_test.py burst [请求数] [并发数]")
            print("  python3 seckill_test.py continuous [持续秒数] [并发数]")
    else:
        # 默认突发压测
        run_pressure_test(total_requests=500, concurrency=50, product_id=1)
