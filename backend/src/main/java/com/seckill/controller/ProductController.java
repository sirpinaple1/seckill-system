package com.seckill.controller;

import com.seckill.common.Result;
import com.seckill.service.SeckillService;
import com.seckill.vo.SeckillOrderVO;
import lombok.RequiredArgsConstructor;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 商品接口控制器
 */
@RestController
@RequestMapping("/api/product")
@RequiredArgsConstructor
public class ProductController {
    
    private final StringRedisTemplate redisTemplate;
    
    private static final Map<Long, Map<String, Object>> PRODUCTS = new HashMap<>();
    
    static {
        PRODUCTS.put(1L, Map.of("id", 1, "name", "iPhone 15 Pro", "originalPrice", 8999, "seckillPrice", 6999, "image", "https://picsum.photos/200"));
        PRODUCTS.put(2L, Map.of("id", 2, "name", "MacBook Pro", "originalPrice", 15999, "seckillPrice", 12999, "image", "https://picsum.photos/201"));
        PRODUCTS.put(3L, Map.of("id", 3, "name", "AirPods Pro", "originalPrice", 1999, "seckillPrice", 999, "image", "https://picsum.photos/202"));
        PRODUCTS.put(4L, Map.of("id", 4, "name", "iPad Pro", "originalPrice", 6999, "seckillPrice", 4999, "image", "https://picsum.photos/203"));
        PRODUCTS.put(5L, Map.of("id", 5, "name", "Apple Watch", "originalPrice", 3999, "seckillPrice", 2999, "image", "https://picsum.photos/204"));
    }
    
    /**
     * 获取商品列表（包含实时库存）
     */
    @GetMapping("/list")
    public Result<List<Map<String, Object>>> getProductList() {
        List<Map<String, Object>> result = new ArrayList<>();
        
        for (Map.Entry<Long, Map<String, Object>> entry : PRODUCTS.entrySet()) {
            Map<String, Object> product = new HashMap<>(entry.getValue());
            
            // 从 Redis 获取实时库存
            String stockKey = "seckill:stock:" + entry.getKey();
            String stock = redisTemplate.opsForValue().get(stockKey);
            product.put("stock", stock != null ? Integer.parseInt(stock) : 0);
            
            result.add(product);
        }
        
        return Result.success(result);
    }
}
