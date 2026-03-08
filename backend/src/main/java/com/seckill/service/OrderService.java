package com.seckill.service;

import com.seckill.mq.OrderMessage;
import com.seckill.mq.OrderMessage;

/**
 * 订单Service接口
 */
public interface OrderService {
    
    /**
     * 创建订单
     */
    void createOrder(OrderMessage message);
}
