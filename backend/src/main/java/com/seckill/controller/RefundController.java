package com.seckill.controller;

import com.seckill.common.Result;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

/**
 * 退款控制器
 */
@RestController
@RequestMapping("/api/refund")
@RequiredArgsConstructor
public class RefundController {
    
    private final StringRedisTemplate redisTemplate;
    
    /**
     * 申请退款
     */
    @PostMapping("/{orderNo}")
    public Result<String> applyRefund(@PathVariable String orderNo,
                                       @RequestHeader("userId") Long userId) {
        // 模拟退款处理
        String refundKey = "seckill:refund:" + orderNo;
        redisTemplate.opsForValue().set(refundKey, "PENDING", 24, java.util.concurrent.TimeUnit.HOURS);
        
        return Result.success("退款申请已提交");
    }
}
