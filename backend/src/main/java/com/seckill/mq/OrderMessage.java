package com.seckill.mq;

import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 订单消息
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class OrderMessage implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String orderNo;
    private Long productId;
    private Long userId;
    private BigDecimal price;
    private LocalDateTime createTime;
}
