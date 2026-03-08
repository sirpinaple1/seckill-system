package com.seckill.mq;

import com.seckill.service.OrderService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

/**
 * 订单消息消费者
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class OrderConsumer {
    
    private final OrderService orderService;
    
    @RabbitListener(queues = "seckill.order.queue")
    public void handleOrder(OrderMessage message) {
        log.info("收到订单消息: {}", message.getOrderNo());
        
        try {
            orderService.createOrder(message);
            log.info("订单创建成功: {}", message.getOrderNo());
        } catch (Exception e) {
            log.error("订单创建失败: {}", message.getOrderNo(), e);
        }
    }
}
