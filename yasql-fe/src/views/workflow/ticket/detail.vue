<template>
  <div v-if="ticketFlowInfo">
    <a-card style="margin: 5px">
      <a-row :gutter="48">
        <a-col :xs="12" :sm="12">
          <div class="heading">
            #{{ ticketFlowInfo.id }}  {{ ticketFlowInfo.workflow }}
          </div>
          <div class="text">状态：{{ ticketFlowInfo.status }}</div>
        </a-col>
        <a-col :md="12" :sm="12" align="right">
          <a-button-group style="margin-right: 4px;" v-if="!ticketFlowInfo.ticket_is_end">
            <a-popconfirm title="确认关闭工单?" placement="bottom" okText="是" cancelText="否" @confirm="closeTicketFlow">
              <a-button>关闭</a-button>
            </a-popconfirm>
          </a-button-group>
          <a-button type="primary" @click="openModal" :disabled="ticketFlowInfo.ticket_is_end">操作</a-button>
        </a-col>
      </a-row>
      <a-divider />
      <a-row>
        <a-col :md="24" :sm="24">
          <a-descriptions size="small" :column="3">
            <a-descriptions-item label="发起人">{{ ticketFlowInfo.creator }}</a-descriptions-item>
            <a-descriptions-item label="发起时间">{{ ticketFlowInfo.created_at|formatTime }}</a-descriptions-item>
            <a-descriptions-item label="更新时间">{{ ticketFlowInfo.updated_at|formatTime }}</a-descriptions-item>
          </a-descriptions>
        </a-col>
        <a-divider />
        <a-col :md="24" :sm="24">
          <a-descriptions size="small" :column="2">
            <a-descriptions-item v-for="(f, index) in ticketFlowInfo.field_kwargs" :key="index" :label="f.name">
              <a :href="f.value" v-if="f.type==='file'">点击下载</a>
              <span v-else>{{ f.value }}</span>
            </a-descriptions-item>
          </a-descriptions>
        </a-col>
      </a-row>
    </a-card>
    <a-card :bordered="false" title="工单进度" style="margin-left: 5px; margin-right: 5px">
      <a-steps :current="currentState" progressDot>
        <a-step v-for="state in allState" :key="state.id">
          <template v-slot:title>
            <span>{{ state.name }}</span>
          </template>
          <template v-slot:description>
            <div class="antd-pro-pages-profile-advanced-style-stepDescription">
              {{ state.participant }}
              <div v-if="state.participant && currentState<(allState.length-1) &&allState[currentState+1].id===state.id">
                <a>催一下</a>
              </div>
            </div>
          </template>
        </a-step>
      </a-steps>
    </a-card>
    <!-- 日志 -->
    <a-card :bordered="false" title="工单日志" style="margin-left: 5px; margin-right: 5px">
      <a-table
        :columns="operationColumns"
        :dataSource="ticketFlowLog"
        rowKey="id"
        :pagination="false" >
        <template slot="status" slot-scope="act_status">
          <a-badge :status="act_status | statusTypeFilter" :text="act_status | statusFilter"/>
        </template>
        <template slot="created_at" slot-scope="created_at">
          {{ created_at|formatTime }}
        </template>
      </a-table>
    </a-card>
    <a-card :bordered="false" title="工单评论" style="margin: 5px">
      <a-list v-if="ticketFlowSug && ticketFlowSug.length >0">
        <a-row>
          <a-list-item :key="index" v-for="(item, index) in ticketFlowSug">
            <a-col :xs="20" :sm="20">
              <a-list-item-meta>
                <div slot="title">{{ item.participant }}</div>
                <div slot="description">{{ item.suggestion }}</div>
              </a-list-item-meta>
            </a-col>
            <a-col :xs="4" :sm="4">
              <small>{{ item.created_at|formatTime }}</small>
            </a-col>
          </a-list-item>
        </a-row>
      </a-list>
      <div class="no-data" v-else>
        <a-icon type="frown-o"/>暂无数据
      </div>
    </a-card>
    <a-modal v-model="visible" :title="allState[currentState].name">
      <template slot="footer">
        <a-button :disabled="pushing" @click="handleTicketFlow('deny')">驳回</a-button>
        <a-button type="primary" :disabled="pushing" @click="handleTicketFlow('allow')">通过</a-button>
      </template>
      <a-textarea v-model="modalData" rows="5" placeholder="请输入评论" />
    </a-modal>
  </div>
</template>

<script>
import moment from 'moment'
import notification from 'ant-design-vue/es/notification'
import { TicketActState, TicketAct } from '@/utils/ticket.js'
import ticketFlowApi from "@/api/workflow.js"

export default {
  name: 'TicketFlowDetail',
  props: {
    pk: [Number, String]
  },
  data () {
    return {
      visible: false,
      pushing: false,
      currentState: 0,
      allState: [],
      ticketFlowInfo: null,
      ticketFlowLog: null,
      ticketFlowSug: null,
      modalData: null,
      operationColumns: [
        {
          title: '操作人',
          dataIndex: 'participant',
        },
        {
          title: '类型',
          dataIndex: 'state',
        },
        {
          title: '时间',
          dataIndex: 'created_at',
          scopedSlots: { customRender: 'created_at' }
        },
        {
          title: '状态',
          dataIndex: 'act_status',
          scopedSlots: { customRender: 'status' }
        },
        {
          title: '数据',
          dataIndex: 'ticket_data',
        },
      ],
    }
  },

  watch: {
    ticketFlowInfo: {
      deep: true,
      handler: function(newValue, oldValue) {
        this.allState = newValue.all_state
        for(var i=0; i<newValue.all_state.length; i++) {
          if (newValue.all_state[i].id===newValue.state){
            this.currentState = i
          }
        }
      },
    },
    ticketFlowLog: {
      deep: true,
      handler: function(newValue, oldValue) {
        this.ticketFlowSug = newValue.filter(x => x.suggestion)
      },
    },
  },

  filters: {
    formatTime(value) {
      if (value) {
        return moment(value).format('YYYY-MM-DD HH:mm:ss')
      } else {
        return ''
      }
    },
    statusFilter (value) {
      const data = {}
      for (const status of TicketActState) {
        data[status.key.toString()] = status.value
      }
      if (data.hasOwnProperty(value.toString())) {
        return data[value.toString()]
      } else {
        return ''
      }
    },
    statusTypeFilter (value) {
      if (value===2||value===4) {
        return "success"
      } else {
        return "error"
      }
    }
  },

  mounted() {
    this.getTicketFlowDetailData()
    this.getTicketFlowLog()
  },
  methods: {
    getTicketFlowDetailData() {
      ticketFlowApi.getTicketDetail(this.pk).then(resp => {
        this.ticketFlowInfo = resp.data
      })
    },
    getTicketFlowLog() {
      ticketFlowApi.getTicketLog(this.pk).then(resp => {
        this.ticketFlowLog = resp.data
      })
    },
    openModal(){
      this.visible = true
      this.modalData = null
    },
    handleTicketFlow(action) {
      const data = {
        "state": this.ticketFlowInfo.state,
        "action": action,
        "suggestion": this.modalData,
      }
      this.pushing = true
      ticketFlowApi.handleTicket(this.ticketFlowInfo.id, data).then(resp => {
        if (resp.code === "0000") {
          notification.info({
            message: '执行操作',
            description: '提交成功',
          })
        } else {
          notification.error({
            message: 'error',
            description: resp.message,
          })
        }
      }).catch(error => {
        console.log(error)
      }).finally(() => {
        this.visible = false
        this.pushing = false
        this.refresh()
      })
    },
    closeTicketFlow() {
      const data = {
        "state": this.ticketFlowInfo.state,
        "action": "close",
      }
      this.pushing = true
      ticketFlowApi.handleTicket(this.ticketFlowInfo.id, data).then(resp => {
        if (resp.code === "0000") {
          notification.info({
            message: '执行操作',
            description: '已关闭工单',
          })
        } else {
          notification.error({
            message: 'error',
            description: resp.message,
          })
        }
      }).catch(error => {
        console.log(error)
      }).finally(() => {
        this.visible = false
        this.pushing = false
        this.refresh()
      })
    },
    refresh() {
      this.getTicketFlowDetailData()
      this.getTicketFlowLog()
      this.modalData = null
    },
  },
}
</script>

<style lang="less" scoped>
  .detail-layout {
    margin-left: 44px;
  }
  .text {
    color: rgba(0, 0, 0, .45);
  }
  .heading {
    color: rgba(0, 0, 0, .85);
    font-size: 20px;
  }
  .no-data {
    color: rgba(0, 0, 0, .25);
    text-align: center;
    line-height: 64px;
    font-size: 16px;
    i {
      font-size: 24px;
      margin-right: 16px;
      position: relative;
      top: 3px;
    }
  }
  .mobile {
    .detail-layout {
      margin-left: unset;
    }
    .text {
    }
    .status-list {
      text-align: left;
    }
  }
</style>
