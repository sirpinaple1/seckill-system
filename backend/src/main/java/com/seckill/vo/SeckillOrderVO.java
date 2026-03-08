package com.seckill.vo;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 秒杀订单VO
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SeckillOrderVO implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String orderNo;
    private Long productId;
    private Long userId;
    private BigDecimal price;
    private String status;
    private LocalDateTime createTime;
    private LocalDateTime payTime;
}
