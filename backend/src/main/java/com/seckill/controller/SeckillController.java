package com.seckill.controller;

import com.seckill.common.Result;
import com.seckill.service.SeckillService;
import com.seckill.vo.SeckillOrderVO;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

/**
 * 秒杀接口控制器
 */
@RestController
@RequestMapping("/api/seckill")
@RequiredArgsConstructor
public class SeckillController {
    
    private final SeckillService seckillService;
    
    /**
     * 秒杀抢购接口
     */
    @PostMapping("/{productId}")
    public Result<String> seckill(@PathVariable Long productId,
                                   @RequestHeader("userId") Long userId) {
        if (productId == null || userId == null) {
            return Result.error("参数错误");
        }
        
        String orderNo = seckillService.seckill(productId, userId);
        
        if (orderNo != null) {
            return Result.success("秒杀成功", orderNo);
        }
        
        return Result.error("秒杀已结束");
    }
    
    /**
     * 秒杀结果查询
     */
    @GetMapping("/result/{orderNo}")
    public Result<SeckillOrderVO> getResult(@PathVariable String orderNo) {
        SeckillOrderVO order = seckillService.getOrderResult(orderNo);
        return Result.success(order);
    }
}
