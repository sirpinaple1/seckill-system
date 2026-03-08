package com.seckill.service.impl;

import cn.hutool.core.util.IdUtil;
import com.seckill.config.RedisLock;
import com.seckill.mq.OrderProducer;
import com.seckill.mq.OrderMessage;
import com.seckill.service.SeckillService;
import com.seckill.vo.SeckillOrderVO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.concurrent.TimeUnit;

/**
 * 秒杀服务实现
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SeckillServiceImpl implements SeckillService {
    
    private static final String STOCK_KEY = "seckill:stock:";
    private static final String ORDER_KEY = "seckill:order:";
    private static final String USER_KEY = "seckill:user:";
    
    private final StringRedisTemplate redisTemplate;
    private final RedisLock redisLock;
    private final OrderProducer orderProducer;
    
    @Override
    public String seckill(Long productId, Long userId) {
        String lockKey = "lock:seckill:" + productId;
        
        boolean lock = redisLock.tryLock(lockKey, userId.toString(), 10);
        if (!lock) {
            log.warn("用户{}重复秒杀商品{}", userId, productId);
            return null;
        }
        
        try {
            String stockKey = STOCK_KEY + productId;
            Long stock = redisTemplate.opsForValue().decrement(stockKey);
            
            if (stock == null || stock < 0) {
                redisTemplate.opsForValue().increment(stockKey);
                log.info("商品{}库存不足", productId);
                return null;
            }
            
            String userKey = USER_KEY + productId;
            Boolean isMember = redisTemplate.opsForSet().isMember(userKey, userId.toString());
            if (Boolean.TRUE.equals(isMember)) {
                log.warn("用户{}已秒杀过商品{}", userId, productId);
                return null;
            }
            
            String orderNo = IdUtil.getSnowflakeNextIdStr();
            
            OrderMessage message = new OrderMessage();
            message.setOrderNo(orderNo);
            message.setProductId(productId);
            message.setUserId(userId);
            message.setPrice(new BigDecimal("99.00"));
            message.setCreateTime(LocalDateTime.now());
            
            orderProducer.sendOrder(message);
            
            redisTemplate.opsForSet().add(userKey, userId.toString());
            redisTemplate.expire(userKey, 24, TimeUnit.HOURS);
            
            log.info("用户{}秒杀商品{}成功，订单号:{}", userId, productId, orderNo);
            return orderNo;
            
        } finally {
            redisLock.unlock(lockKey, userId.toString());
        }
    }
    
    @Override
    public SeckillOrderVO getOrderResult(String orderNo) {
        String orderKey = ORDER_KEY + orderNo;
        String orderJson = redisTemplate.opsForValue().get(orderKey);
        
        if (orderJson != null) {
            return SeckillOrderVO.builder()
                    .orderNo(orderNo)
                    .status("PAID")
                    .build();
        }
        
        return SeckillOrderVO.builder()
                .orderNo(orderNo)
                .status("PROCESSING")
                .build();
    }
}
