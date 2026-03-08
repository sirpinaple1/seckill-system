package com.seckill.config;

import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;

/**
 * Redis分布式锁
 */
@Component
public class RedisLock {
    
    private static final String LOCK_PREFIX = "lock:";
    
    private final StringRedisTemplate redisTemplate;
    
    public RedisLock(StringRedisTemplate redisTemplate) {
        this.redisTemplate = redisTemplate;
    }
    
    /**
     * 尝试获取锁
     */
    public boolean tryLock(String key, String value, long expireSeconds) {
        String lockKey = LOCK_PREFIX + key;
        Boolean success = redisTemplate.opsForValue()
                .setIfAbsent(lockKey, value, expireSeconds, TimeUnit.SECONDS);
        return Boolean.TRUE.equals(success);
    }
    
    /**
     * 释放锁
     */
    public void unlock(String key, String value) {
        String lockKey = LOCK_PREFIX + key;
        String currentValue = redisTemplate.opsForValue().get(lockKey);
        if (value.equals(currentValue)) {
            redisTemplate.delete(lockKey);
        }
    }
}
