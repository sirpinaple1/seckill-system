package com.seckill.service;

import java.util.List;
import java.util.Map;

/**
 * 客流统计Service接口
 */
public interface TrafficService {
    
    /**
     * 获取小时客流数据
     */
    List<Map<String, Object>> getHourlyTraffic();
    
    /**
     * 获取日客流数据
     */
    List<Map<String, Object>> getDailyTraffic();
    
    /**
     * 获取实时客流
     */
    Map<String, Object> getRealtimeTraffic();
    
    /**
     * 记录访问
     */
    void recordVisit();
}
