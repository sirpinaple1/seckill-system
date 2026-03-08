package com.seckill.service.impl;

import com.seckill.service.RefundService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * 退款服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class RefundServiceImpl implements RefundService {
    
    private static final String REFUND_KEY = "refund:";
    private static final String ORDER_KEY = "order:";
    
    private final StringRedisTemplate redisTemplate;
    
    @Override
    public boolean applyRefund(String orderNo, Long userId) {
        log.info("用户{}申请退款，订单号:{}", userId, orderNo);
        
        // 1. 检查订单是否存在
        String orderKey = ORDER_KEY + orderNo;
        String orderJson = redisTemplate.opsForValue().get(orderKey);
        
        if (orderJson == null) {
            log.warn("订单不存在:{}", orderNo);
            return false;
        }
        
        // 2. 检查是否已退款
        String refundKey = REFUND_KEY + orderNo;
        String refundStatus = redisTemplate.opsForValue().get(refundKey);
        
        if (refundStatus != null) {
            log.warn("订单已退款:{}", orderNo);
            return false;
        }
        
        // 3. 申请退款（模拟）
        // 实际应该调用支付平台退款接口
        redisTemplate.opsForValue().set(refundKey, "REFUNDING", 24, TimeUnit.HOURS);
        
        // 模拟退款成功后恢复库存（可选）
        // 这里简单模拟：2秒后自动退款成功
        new Thread(() -> {
            try {
                Thread.sleep(2000);
                redisTemplate.opsForValue().set(refundKey, "REFUND_SUCCESS", 24, TimeUnit.HOURS);
                log.info("订单{}退款成功", orderNo);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }).start();
        
        log.info("用户{}退款申请成功，订单号:{}", userId, orderNo);
        return true;
    }
    
    @Override
    public String getRefundStatus(String orderNo) {
        String refundKey = REFUND_KEY + orderNo;
        String status = redisTemplate.opsForValue().get(refundKey);
        
        if (status == null) {
            return "NO_REFUND";
        }
        
        return status;
    }
}
