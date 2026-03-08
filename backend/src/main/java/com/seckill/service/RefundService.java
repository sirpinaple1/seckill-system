package com.seckill.service;

/**
 * 退款Service接口
 */
public interface RefundService {
    
    /**
     * 申请退款
     * @return 是否成功
     */
    boolean applyRefund(String orderNo, Long userId);
    
    /**
     * 获取退款状态
     */
    String getRefundStatus(String orderNo);
}
