package com.seckill.service;

import com.seckill.vo.SeckillOrderVO;

/**
 * 秒杀Service接口
 */
public interface SeckillService {
    
    /**
     * 执行秒杀
     * @param productId 商品ID
     * @param userId 用户ID
     * @return 订单号，秒杀失败返回null
     */
    String seckill(Long productId, Long userId);
    
    /**
     * 获取订单结果
     */
    SeckillOrderVO getOrderResult(String orderNo);
}
