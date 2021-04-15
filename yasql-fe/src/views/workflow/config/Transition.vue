<template>
  <a-card>
    <a-row :gutter="48">
      <a-col :md="18" :sm="18">
        <h3>状态流转</h3>
      </a-col>
    </a-row>
    <a-divider />
    <a-table
      :columns="columns"
      :dataSource="currentTplTransition"
      rowKey="id"
      :pagination="false"
    >
      <template slot="operation" slot-scope="text, record">
        <template>
          <span>
            <a @click="updateTransition(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm title="是否要删除此行？" @confirm="removeTransition(record)">
              <a>删除</a>
            </a-popconfirm>
          </span>
        </template>
      </template>
      <template slot="transitionType" slot-scope="text">
        {{ text|displayTransitionType }}
      </template>
      <template slot="attributeType" slot-scope="text">
        {{ text|displayAttributeType }}
      </template>
    </a-table>
    <a-button style="width: 100%; margin-top: 16px; margin-bottom: 8px" type="dashed" icon="plus" @click="newTransition">新增流转</a-button>
    <a-modal v-model="visible" title="配置状态流转" width="800px" ok-text="确认" cancel-text="取消" @ok="commitTransition" v-if="curRecord">
      <a-form-model :model="curRecord" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-model-item label="流转名称">
          <a-input v-model="curRecord.action" placeholder="状态流转操作名称" />
        </a-form-model-item>
        <a-form-model-item label="流转类型">
          <a-select v-model="curRecord.transition_type" placeholder="流转类型">
            <a-select-option v-for="item in transitionType" :key="item.key" :value="item.key">
              {{ item.value }}
            </a-select-option>
          </a-select>
        </a-form-model-item>
        <a-form-model-item label="源状态">
          <a-select v-model="curRecord.source_state" placeholder="源状态">
            <a-select-option v-for="item in currentTplState" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
          <a-tooltip placement="rightBottom" title="初始状态:新建工单时,获取对应的字段以及状态流转，结束状态：此状态下的工单不再处理">
            <a-icon type="question-circle" />
          </a-tooltip>
        </a-form-model-item>
        <a-form-model-item label="目标状态">
          <a-select v-model="curRecord.destination_state" placeholder="目标状态">
            <a-select-option v-for="item in currentTplState" :key="item.id" :value="item.id">
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-model-item>
        <a-form-model-item label="属性类型">
          <a-select v-model="curRecord.attribute_type" placeholder="属性类型">
            <a-select-option v-for="item in attributeType" :key="item.key" :value="item.key">
              {{ item.value }}
            </a-select-option>
          </a-select>
        </a-form-model-item>
        <a-form-model-item label="条件表达式">
          <a-textarea v-model="curRecord.condition_expression" placeholder="根据表达式中的条件来确定流转的下个状态" />
        </a-form-model-item>
        <a-form-model-item label="是否校验参数">
          <a-switch v-model="curRecord.field_require_check" />
          <a-tooltip placement="rightBottom" title="提交工单时需要校验数据。如'退回'操作，表单不需要提交数据">
            <a-icon type="question-circle" style="margin-left: 10px" />
          </a-tooltip>
        </a-form-model-item>
      </a-form-model>
    </a-modal>
  </a-card>
</template>


<script>
import { TransitionType, AttributeType } from '@/utils/ticket.js'
import notification from 'ant-design-vue/es/notification'
import ticketFlowApi from "@/api/workflow.js"


export default {
  props: {
    currentTplData: Object,
    currentTplState: Array,
  },
  data () {
    return {
      isNewTransition: true,
      visible: false,
      curRecord: null,
      currentTplTransition: [],
      transitionType: TransitionType,
      attributeType: AttributeType,
      columns: [
        {
          title: '流转名称',
          dataIndex: 'action',
        },
        {
          title: '流转类型',
          dataIndex: 'transition_type',
          scopedSlots: { customRender: 'transitionType' }
        },
        {
          title: '源状态',
          dataIndex: 'source_state_name',
        },
        {
          title: '目标状态',
          dataIndex: 'destination_state_name',
        },
        {
          title: '属性类型',
          dataIndex: 'attribute_type',
          scopedSlots: { customRender: 'attributeType' }
        },
        {
          title: '操作',
          scopedSlots: { customRender: 'operation' }
        }
      ],
    }
  },
  filters: {
    displayTransitionType(value) {
      const s = TransitionType.filter(x => x.key === value)
      if(s.length > 0){
        return s[0].value
      } else {
        return ''
      }
    },
    displayAttributeType(value) {
      const s = AttributeType.filter(x => x.key === value)
      if(s.length > 0){
        return s[0].value
      } else {
        return ''
      }
    },
  },
  created() {
    this.initData()
  },
  methods: {
    initData() {
      this.fetchStateData()
      this.fetchTransitionData()
    },
    fetchTransitionData () {
      ticketFlowApi.getWorkflowTransition(this.currentTplData.id).then(resp => {
        this.currentTplTransition = resp.data
      })
    },
    fetchStateData() {
      ticketFlowApi.getWorkflowState(this.currentTplData.id).then(resp => {
        this.stateData = resp.data
        this.$emit('update:currentTplState', this.stateData)
      })
    },
    newTransition () {
      this.visible = true
      this.isNewTransition = true
      this.curRecord = {}
    },
    updateTransition (record) {
      this.visible = true
      this.isNewTransition = false
      this.curRecord = record
    },
    removeTransition (record) {
      ticketFlowApi.deleteWorkflowTransition(record.id).then(resp => {
        if (resp.code === "0000") {
          notification.info({
            message: '创建状态',
            description: "提交成功",
          })
          this.initData()
        } else {
          notification.error({
            message: '创建状态',
            description: resp.message,
          })
        }
      }) 
    },
    commitTransition() {
      if(this.isNewTransition) {
        let data = { ...this.curRecord }
        data["workflow"] = this.currentTplData.id
        ticketFlowApi.createWorkflowTransition(data).then(resp => {
          if (resp.code === "0000") {
            notification.info({
              message: '创建状态',
              description: "提交成功",
            })
            this.initData()
            this.visible = false
          } else {
            notification.error({
              message: '创建状态',
              description: resp.message,
            })
          }
        })       
      } else {
        ticketFlowApi.updateWorkflowTransition(this.curRecord.id, this.curRecord).then(resp => {
          if (resp.code === "0000") {
            notification.info({
              message: '更新状态',
              description: "提交成功",
            })
            this.initData()
            this.visible = false
          } else {
            notification.error({
              message: '更新状态',
              description: resp.message,
            })
          }
        })
      }
    },
  }
}
</script>