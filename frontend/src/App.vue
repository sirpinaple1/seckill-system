<template>
  <div id="app">
    <el-container>
      <!-- 头部 -->
      <el-header class="header">
        <div class="header-content">
          <h1>⚡ 秒杀系统</h1>
          <div class="user-info">
            <el-dropdown @command="handleCommand">
              <span class="user-dropdown">
                用户: {{ userId }} <i class="el-icon-arrow-down"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                <el-dropdown-item command="refunds">退款记录</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      
      <el-main>
        <!-- 实时客流统计 -->
        <el-row :gutter="20" class="stats-row">
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon blue"><i class="el-icon-user"></i></div>
              <div class="stat-info">
                <div class="stat-value">{{ realtime.onlineUsers }}</div>
                <div class="stat-label">在线人数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon green"><i class="el-icon-view"></i></div>
              <div class="stat-info">
                <div class="stat-value">{{ realtime.totalVisits }}</div>
                <div class="stat-label">总访问量</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon orange"><i class="el-icon-shopping-cart-2"></i></div>
              <div class="stat-info">
                <div class="stat-value">{{ realtime.totalOrders }}</div>
                <div class="stat-label">总订单数</div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="6">
            <el-card class="stat-card">
              <div class="stat-icon purple"><i class="el-icon-success"></i></div>
              <div class="stat-info">
                <div class="stat-value">{{ realtime.successRate }}%</div>
                <div class="stat-label">成功率</div>
              </div>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 客流柱状图 -->
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card class="chart-card">
              <div slot="header">
                <span>📊 24小时客流趋势</span>
                <el-button-group style="float: right;">
                  <el-button size="small" :type="chartType==='hourly'?'primary':''" @click="chartType='hourly'">小时</el-button>
                  <el-button size="small" :type="chartType==='daily'?'primary':''" @click="chartType='daily'">日</el-button>
                </el-button-group>
              </div>
              <div ref="chart" style="height: 300px;"></div>
            </el-card>
          </el-col>
          
          <!-- 我的订单 -->
          <el-col :span="8">
            <el-card class="orders-card">
              <div slot="header">
                <span>📦 我的订单</span>
              </div>
              <el-table :data="myOrders" style="width: 100%">
                <el-table-column prop="orderNo" label="订单号" width="120"></el-table-column>
                <el-table-column prop="status" label="状态">
                  <template slot-scope="scope">
                    <el-tag :type="scope.row.status==='PAID'?'success':'warning'" size="small">
                      {{ scope.row.status==='PAID'?'已支付':'处理中' }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80">
                  <template slot-scope="scope">
                    <el-button v-if="scope.row.status==='PAID'" 
                              type="text" 
                              size="small"
                              @click="applyRefund(scope.row.orderNo)">
                      退款
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 商品列表 -->
        <el-divider></el-divider>
        <h2>🔥 秒杀商品</h2>
        <el-row :gutter="20">
          <el-col :span="8" v-for="product in products" :key="product.id">
            <el-card class="product-card">
              <img :src="product.image" class="product-image">
              <h3>{{ product.name }}</h3>
              <p class="price">
                <span class="original">¥{{ product.originalPrice }}</span>
                <span class="seckill">秒杀价 ¥{{ product.seckillPrice }}</span>
              </p>
              <p class="stock">库存: {{ product.stock }}</p>
              <el-button 
                type="danger" 
                size="large" 
                :loading="loading"
                @click="handleSeckill(product.id)"
                class="seckill-btn"
              >
                立即秒杀
              </el-button>
            </el-card>
          </el-col>
        </el-row>
        
        <!-- 退款对话框 -->
        <el-dialog v-model="refundDialogVisible" title="退款申请" width="400px">
          <p>订单号: {{ currentRefundOrder }}</p>
          <p>确定要申请退款吗？</p>
          <span slot="footer">
            <el-button @click="refundDialogVisible = false">取消</el-button>
            <el-button type="primary" @click="confirmRefund">确认退款</el-button>
          </span>
        </el-dialog>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'

const API_URL = 'http://localhost:8080/api'

export default {
  name: 'App',
  data() {
    return {
      userId: Math.floor(Math.random() * 100000) + 1000,
      products: [],
      loading: false,
      realtime: {
        onlineUsers: 0,
        totalVisits: 0,
        totalOrders: 0,
        successRate: '0'
      },
      chartType: 'hourly',
      chartData: [],
      myOrders: [],
      refundDialogVisible: false,
      currentRefundOrder: ''
    }
  },
  mounted() {
    this.loadProducts()
    this.loadRealtimeData()
    this.loadChartData()
    this.loadOrders()
    // 定时刷新（每2秒）
    setInterval(() => {
      this.loadProducts()
      this.loadRealtimeData()
      this.loadChartData()
    }, 2000)
  },
  methods: {
    async loadProducts() {
      try {
        const response = await axios.get(`${API_URL}/product/list`)
        if (response.data.code === 200) {
          this.products = response.data.data
        }
      } catch (e) {
        console.error(e)
      }
    },
    
    async loadRealtimeData() {
      try {
        const response = await axios.get(`${API_URL}/traffic/realtime`)
        this.realtime = response.data.data
      } catch (e) {
        console.error(e)
      }
    },
    
    async loadChartData() {
      try {
        const url = this.chartType === 'hourly' 
          ? `${API_URL}/traffic/hourly` 
          : `${API_URL}/traffic/daily`
        const response = await axios.get(url)
        this.chartData = response.data.data
        this.initChart()
      } catch (e) {
        console.error(e)
      }
    },
    
    initChart() {
      if (!this.$refs.chart) return
      
      const chart = echarts.init(this.$refs.chart)
      const xData = this.chartData.map(d => d.time || d.date)
      const visits = this.chartData.map(d => d.visits)
      const orders = this.chartData.map(d => d.orders)
      
      chart.setOption({
        tooltip: { trigger: 'axis' },
        legend: { data: ['访问量', '订单数'] },
        xAxis: { type: 'category', data: xData },
        yAxis: { type: 'value' },
        series: [
          { name: '访问量', type: 'bar', data: visits, itemStyle: { color: '#409EFF' } },
          { name: '订单数', type: 'bar', data: orders, itemStyle: { color: '#67C23A' } }
        ]
      })
    },
    
    async loadOrders() {
      // 模拟订单数据
      this.myOrders = [
        { orderNo: '202603071001', status: 'PAID' },
        { orderNo: '202603071002', status: 'PROCESSING' }
      ]
    },
    
    handleCommand(command) {
      if (command === 'orders') {
        this.$message.info('查看订单')
      } else if (command === 'refunds') {
        this.$message.info('查看退款')
      }
    },
    
    applyRefund(orderNo) {
      this.currentRefundOrder = orderNo
      this.refundDialogVisible = true
    },
    
    async confirmRefund() {
      try {
        await axios.post(`${API_URL}/refund/${this.currentRefundOrder}`, {}, {
          headers: { 'userId': this.userId }
        })
        this.$message.success('退款申请已提交')
        this.refundDialogVisible = false
      } catch (e) {
        this.$message.error('退款失败')
      }
    },
    
    async handleSeckill(productId) {
      this.loading = true
      try {
        const response = await axios.post(`${API_URL}/seckill/${productId}`, {}, {
          headers: { 'userId': this.userId }
        })
        
        if (response.data.code === 200) {
          this.$message.success('秒杀成功！订单号: ' + response.data.data)
          this.myOrders.unshift({ orderNo: response.data.data, status: 'PROCESSING' })
          // 刷新库存
          this.loadProducts()
        }
      } catch (error) {
        this.$message.error(error.response?.data?.message || '秒杀失败')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style lang="scss">
#app {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.header {
  background: linear-gradient(90deg, #ff4757, #ff6b81);
  color: white;
  display: flex;
  align-items: center;
  
  .header-content {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    h1 { font-size: 24px; margin: 0; }
  }
}

.user-dropdown { color: white; cursor: pointer; }

.stats-row { margin-bottom: 20px; }

.stat-card {
  display: flex; align-items: center;
  .stat-icon {
    width: 60px; height: 60px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 24px; margin-right: 15px;
    &.blue { background: #e3f2fd; color: #2196f3; }
    &.green { background: #e8f5e9; color: #4caf50; }
    &.orange { background: #fff3e0; color: #ff9800; }
    &.purple { background: #f3e5f5; color: #9c27b0; }
  }
  .stat-info {
    .stat-value { font-size: 24px; font-weight: bold; }
    .stat-label { color: #999; font-size: 12px; }
  }
}

.chart-card, .orders-card { margin-bottom: 20px; }

.product-card {
  margin-bottom: 20px; text-align: center;
  .product-image { width: 100%; height: 150px; object-fit: cover; }
  .price {
    .original { text-decoration: line-through; color: #999; margin-right: 10px; }
    .seckill { color: #ff4757; font-size: 24px; font-weight: bold; }
  }
  .seckill-btn { width: 100%; font-size: 18px; font-weight: bold; }
}
</style>
