package com.seckill.controller;

import com.seckill.common.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 客流统计控制器
 */
@RestController
@RequestMapping("/api/traffic")
@RequiredArgsConstructor
public class TrafficController {
    
    private final StringRedisTemplate redisTemplate;
    
    /**
     * 实时客流数据
     */
    @GetMapping("/realtime")
    public Result<Map<String, Object>> getRealtimeData() {
        // 获取在线人数（模拟）
        String onlineUsers = redisTemplate.opsForValue().get("seckill:online:users");
        String totalVisits = redisTemplate.opsForValue().get("seckill:total:visits");
        String totalOrders = redisTemplate.opsForValue().get("seckill:total:orders");
        
        // 如果没有数据，初始化
        if (onlineUsers == null) {
            onlineUsers = String.valueOf((int)(Math.random() * 500 + 100));
            redisTemplate.opsForValue().set("seckill:online:users", onlineUsers);
        }
        if (totalVisits == null) {
            totalVisits = String.valueOf((int)(Math.random() * 5000 + 1000));
            redisTemplate.opsForValue().set("seckill:total:visits", totalVisits);
        }
        if (totalOrders == null) {
            totalOrders = String.valueOf((int)(Math.random() * 500 + 100));
            redisTemplate.opsForValue().set("seckill:total:orders", totalOrders);
        }
        
        // 更新在线人数（模拟波动）
        int currentOnline = Integer.parseInt(onlineUsers) + (int)(Math.random() * 20 - 10);
        redisTemplate.opsForValue().set("seckill:online:users", String.valueOf(currentOnline));
        
        // 增加访问量
        redisTemplate.opsForValue().increment("seckill:total:visits");
        
        int orders = Integer.parseInt(totalOrders);
        int visits = Integer.parseInt(totalVisits);
        double successRate = visits > 0 ? (orders * 100.0 / visits) : 0;
        
        Map<String, Object> data = new HashMap<>();
        data.put("onlineUsers", currentOnline);
        data.put("totalVisits", Integer.parseInt(totalVisits) + 1);
        data.put("totalOrders", orders);
        data.put("successRate", String.format("%.1f", successRate));
        
        return Result.success(data);
    }
    
    /**
     * 每小时客流数据
     */
    @GetMapping("/hourly")
    public Result<List<Map<String, Object>>> getHourlyData() {
        List<Map<String, Object>> data = new ArrayList<>();
        Calendar cal = Calendar.getInstance();
        
        for (int i = 23; i >= 0; i--) {
            cal.set(Calendar.HOUR_OF_DAY, i);
            String hour = String.format("%02d:00", i);
            int visits = (int)(Math.random() * 1000 + 200);
            int orders = (int)(Math.random() * 100 + 20);
            
            Map<String, Object> item = new HashMap<>();
            item.put("time", hour);
            item.put("visits", visits);
            item.put("orders", orders);
            data.add(item);
        }
        
        return Result.success(data);
    }
    
    /**
     * 每日客流数据
     */
    @GetMapping("/daily")
    public Result<List<Map<String, Object>>> getDailyData() {
        List<Map<String, Object>> data = new ArrayList<>();
        
        for (int i = 29; i >= 0; i--) {
            Calendar cal = Calendar.getInstance();
            cal.add(Calendar.DAY_OF_MONTH, -i);
            String date = String.format("%02d-%02d", cal.get(Calendar.MONTH) + 1, cal.get(Calendar.DAY_OF_MONTH));
            int visits = (int)(Math.random() * 10000 + 5000);
            int orders = (int)(Math.random() * 1000 + 200);
            
            Map<String, Object> item = new HashMap<>();
            item.put("date", date);
            item.put("visits", visits);
            item.put("orders", orders);
            data.add(item);
        }
        
        return Result.success(data);
    }
}
