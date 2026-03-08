package com.seckill.service.impl;

import com.seckill.mq.OrderMessage;
import com.seckill.service.OrderService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * 订单服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class OrderServiceImpl implements OrderService {
    
    private final StringRedisTemplate redisTemplate;
    
    @Override
    public void createOrder(OrderMessage message) {
        log.info("开始创建订单: {}", message.getOrderNo());
        
        // 模拟订单创建（实际应该入库MySQL）
        String orderKey = "order:" + message.getOrderNo();
        
        // 存储订单信息到Redis（简化版）
        redisTemplate.opsForValue().set(orderKey,
            String.format("{\"orderNo\":\"%s\",\"productId\":%d,\"userId\":%d,\"price\":%s,\"status\":\"PAID\",\"createTime\":\"%s\"}",
                message.getOrderNo(),
                message.getProductId(),
                message.getUserId(),
                message.getPrice(),
                LocalDateTime.now()
            ),
            24, TimeUnit.HOURS);
        
        log.info("订单创建完成: {}", message.getOrderNo());
    }
}
