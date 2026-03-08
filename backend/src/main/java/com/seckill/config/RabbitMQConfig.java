package com.seckill.config;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * RabbitMQ配置
 */
@Configuration
public class RabbitMQConfig {
    
    public static final String EXCHANGE = "seckill.exchange";
    public static final String QUEUE = "seckill.order.queue";
    public static final String ROUTING_KEY = "seckill.order";
    
    // 交换机
    @Bean
    public DirectExchange seckillExchange() {
        return new DirectExchange(EXCHANGE);
    }
    
    // 队列
    @Bean
    public Queue seckillQueue() {
        return QueueBuilder.durable(QUEUE).build();
    }
    
    // 绑定
    @Bean
    public Binding binding(Queue seckillQueue, DirectExchange seckillExchange) {
        return BindingBuilder.bind(seckillQueue).to(seckillExchange).with(ROUTING_KEY);
    }
    
    // JSON序列化
    @Bean
    public Jackson2JsonMessageConverter messageConverter() {
        return new Jackson2JsonMessageConverter();
    }
    
    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory) {
        RabbitTemplate template = new RabbitTemplate(connectionFactory);
        template.setMessageConverter(messageConverter());
        return template;
    }
}
