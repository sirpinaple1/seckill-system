package com.seckill.service.impl;

import com.seckill.service.TrafficService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * 客流统计服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TrafficServiceImpl implements TrafficService {
    
    private static final String TRAFFIC_KEY = "traffic:visit:";
    private final StringRedisTemplate redisTemplate;
    
    @Override
    public List<Map<String, Object>> getHourlyTraffic() {
        List<Map<String, Object>> result = new ArrayList<>();
        
        // 获取最近24小时的数据
        LocalDateTime now = LocalDateTime.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("HH:mm");
        
        for (int i = 23; i >= 0; i--) {
            LocalDateTime hour = now.minusHours(i);
            String key = TRAFFIC_KEY + hour.format(DateTimeFormatter.ofPattern("yyyy-MM-dd-HH"));
            
            // 模拟数据（实际从Redis读取）
            int visits = (int) (Math.random() * 5000) + 1000;
            int orders = visits / 10;
            
            Map<String, Object> data = new HashMap<>();
            data.put("time", hour.format(formatter));
            data.put("visits", visits);
            data.put("orders", orders);
            result.add(data);
        }
        
        return result;
    }
    
    @Override
    public List<Map<String, Object>> getDailyTraffic() {
        List<Map<String, Object>> result = new ArrayList<>();
        
        // 获取最近7天数据
        LocalDateTime now = LocalDateTime.now();
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MM-dd");
        
        for (int i = 6; i >= 0; i--) {
            LocalDateTime day = now.minusDays(i);
            
            // 模拟数据
            int visits = (int) (Math.random() * 50000) + 10000;
            int orders = visits / 8;
            
            Map<String, Object> data = new HashMap<>();
            data.put("date", day.format(formatter));
            data.put("visits", visits);
            data.put("orders", orders);
            result.add(data);
        }
        
        return result;
    }
    
    @Override
    public Map<String, Object> getRealtimeTraffic() {
        Map<String, Object> data = new HashMap<>();
        
        // 模拟实时数据
        data.put("onlineUsers", (int) (Math.random() * 5000) + 2000);
        data.put("totalVisits", (int) (Math.random() * 100000) + 50000);
        data.put("totalOrders", (int) (Math.random() * 10000) + 5000);
        data.put("successRate", String.format("%.1f", Math.random() * 30 + 70));
        
        return data;
    }
    
    @Override
    public void recordVisit() {
        // 记录访问（简化版）
        LocalDateTime now = LocalDateTime.now();
        String key = TRAFFIC_KEY + now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd-HH"));
        
        redisTemplate.opsForValue().increment(key);
        redisTemplate.expire(key, 72, java.util.concurrent.TimeUnit.HOURS);
    }
}
