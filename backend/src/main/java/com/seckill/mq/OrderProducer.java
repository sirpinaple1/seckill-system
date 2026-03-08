package com.seckill.mq;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.stereotype.Component;

/**
 * 订单消息生产者
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class OrderProducer {
    
    private static final String EXCHANGE = "seckill.exchange";
    private static final String QUEUE = "seckill.order.queue";
    private static final String ROUTING_KEY = "seckill.order";
    
    private final RabbitTemplate rabbitTemplate;
    private final ObjectMapper objectMapper;
    
    public void sendOrder(OrderMessage message) {
        try {
            rabbitTemplate.convertAndSend(EXCHANGE, ROUTING_KEY, message);
            log.info("订单消息发送成功: {}", message.getOrderNo());
        } catch (Exception e) {
            log.error("订单消息发送失败: {}", message.getOrderNo(), e);
        }
    }
}
