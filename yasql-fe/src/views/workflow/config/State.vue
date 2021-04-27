<template>
  <a-card>
    <a-row :gutter="48">
      <a-col :md="18" :sm="18">
        <h3>流程状态</h3>
      </a-col>
    </a-row>
    <a-divider />
    <a-table
      :columns="columns"
      :dataSource="stateData"
      rowKey="id"
      :pagination="false"
    >
      <template slot="operation" slot-scope="text, record">
        <template>
          <span>
            <a @click="updateState(record)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm title="是否要删除此行？" @confirm="removeState(record)">
              <a>删除</a>
            </a-popconfirm>
          </span>
        </template>
      </template>
      <template slot="state_type" slot-scope="text">
        {{ text|displayStateType }}
      </template>
      <template slot="participant_type" slot-scope="text">
        {{ text|displayParticipantType }}
      </template>
      <template slot="participant" slot-scope="text">
        {{ text.join(', ') }}
      </template>
      <template slot="is_hidden" slot-scope="text">
        {{ text|formatBool }}
      </template>
    </a-table>
    <a-button style="width: 100%; margin-top: 16px; margin-bottom: 8px" type="dashed" icon="plus" @click="newState">新增状态</a-button>
    <a-modal v-model="visible" v-if="curRecord"
      title="配置状态" width="800px" 
      ok-text="确认" cancel-text="取消" 
      @ok="commitState" @cancel="cancelModal">
      <a-form-model ref="ruleForm" :model="curRecord" :rules="rules" :label-col="{ span: 6 }" :wrapper-col="{ span: 16 }">
        <a-form-model-item label="名称" required prop="name">
          <a-input v-model="curRecord.name" placeholder="状态名称" />
        </a-form-model-item>
        <a-form-model-item label="顺序" required prop="order_id">
          <a-input-number v-model="curRecord.order_id" :min="1" placeholder="状态顺序" />
          <a-tooltip placement="rightBottom" title="工单根据此顺序进行流转">
            <a-icon type="question-circle" style="margin-left: 10px" />
          </a-tooltip>
        </a-form-model-item>
        <a-form-model-item label="类型" required prop="state_type">
          <a-select v-model="curRecord.state_type" @change="handleChangeStateType" placeholder="状态类型">
            <a-select-option v-for="item in stateType" :key="item.key" :value="item.key">
              {{ item.value }}
            </a-select-option>
          </a-select>
          <a-tooltip placement="rightBottom" title="初始状态：新建工单时,获取对应的字段以及状态流转，普通状态：中间流转状态，结束状态：此状态下的工单不再处理">
            <a-icon type="question-circle" />
          </a-tooltip>
        </a-form-model-item>
        <a-form-model-item label="操作人类型">
          <a-select v-model="curRecord.participant_type" 
            :disabled="curRecord.state_type===1" 
            @change="handleChangeParticipantType" placeholder="操作人类型">
            <a-select-option v-for="item in participantType" :key="item.key" :value="item.key">
              {{ item.value }}
            </a-select-option>
          </a-select>
        </a-form-model-item>
        <a-form-model-item label="操作人">
          <div v-if="curRecord.participant_type===1">
            <a-select v-model="curRecord.participant" mode="tags" placeholder="请输入相关操作人">
            </a-select>
          </div>
          <div v-else-if="curRecord.participant_type===2">
            <a-select v-model="curRecord.participant" mode="tags" placeholder="请输入相关角色">
              <a-select-option v-for="item in RoleList" :key="item.rid" :value="item.role_name">
                {{ item.role_name }}
              </a-select-option>
            </a-select>
          </div>
          <div v-else-if="curRecord.participant_type===4">
            <a-select v-model="curRecord.participant" mode="tags" placeholder="请输入工单字段">
              <a-select-option v-for="item in tplKwarg" :key="item.field_key" :value="item.field_key">
                {{ item.field_name }}
              </a-select-option>
            </a-select>
          </div>
          <div v-else>
            <a-select v-model="curRecord.participant" disabled mode="tags" placeholder="请输入相关操作人">
            </a-select>
          </div>
        </a-form-model-item>
        <a-form-model-item label="流转方式">
          <a-select v-model="curRecord.distribute_type" 
            :disabled="curRecord.state_type===1 || [2, 3, 5].indexOf(curRecord.participant_type) >= 0"
            placeholder="审核：其中一人处理，还是所有人都要处理">
            <a-select-option v-for="item in distributeType" :key="item.key" :value="item.key">
              {{ item.value }}
            </a-select-option>
          </a-select>
        </a-form-model-item>
        <a-form-model-item label="隐藏此状态">
          <a-switch v-model="curRecord.is_hidden" />
          <a-tooltip placement="rightBottom" title="前端页面不展示此阶段状态">
            <a-icon type="question-circle" style="margin-left: 10px" />
          </a-tooltip>
        </a-form-model-item>
      </a-form-model>
    </a-modal>
  </a-card>
</template>


<script>
import { StateType, DistributeType, ParticipantType } from '@/utils/ticket.js'
import notification from 'ant-design-vue/es/notification'
import ticketFlowApi from "@/api/workflow.js"


export default {
  props: {
    currentTplData: Object,
    currentTplState: Array,
  },
  data () {
    return {
      isNewState: true,
      visible: false,
      curRecord: null,
      stateData: [],
      RoleList: [],
      tplKwarg: [],
      stateType: StateType,
      distributeType: DistributeType,
      participantType: ParticipantType,
      columns: [
        {
          title: '状态名称',
          dataIndex: 'name',
        },
        {
          title: '状态顺序',
          dataIndex: 'order_id',
        },
        {
          title: '状态类型',
          dataIndex: 'state_type',
          scopedSlots: { customRender: 'state_type' }
        },
        {
          title: '操作人类型',
          dataIndex: 'participant_type',
          scopedSlots: { customRender: 'participant_type' }
        },
        {
          title: '操作人',
          dataIndex: 'participant',
          scopedSlots: { customRender: 'participant' }
        },
        {
          title: '是否隐藏',
          dataIndex: 'is_hidden',
          scopedSlots: { customRender: 'is_hidden' }
        },
        {
          title: '操作',
          scopedSlots: { customRender: 'operation' }
        }
      ],
      rules: {
        name: [
          { required: true, message: '必须填写', trigger: 'change' },
          { min: 2, message: '至少2个字符', trigger: 'blur' },
        ],
        order_id: [{ required: true, message: '必须填写', trigger: 'blur' }],
        state_type: [{ required: true, message: '必须选择', trigger: 'change' }],
      },
    }
  },
  filters: {
    displayStateType(value) {
      const s = StateType.filter(x => x.key === value)
      if(s.length > 0){
        return s[0].value
      } else {
        return ''
      }
    },
    displayParticipantType(value) {
      const s = ParticipantType.filter(x => x.key === value)
      if(s.length > 0){
        return s[0].value
      } else {
        return ''
      }
    },
    formatBool(value) {
      if(value) {
        return "是"
      } else {
        return "否"
      }
    }
  },
  created() {
    this.fetchStateData()
    this.fetchUserRole()
    this.fetchtplKwarg()
  },
  methods: {
    fetchStateData() {
      ticketFlowApi.getWorkflowState(this.currentTplData.id).then(resp => {
        this.stateData = resp.data
        this.$emit('update:currentTplState', this.stateData)
      })
    },
    fetchUserRole() {
      ticketFlowApi.getUserRole().then(resp => {
        this.RoleList = resp.data
      })
    },
    fetchtplKwarg(){
      ticketFlowApi.getTicketTemplate(this.currentTplData.id).then(resp => {
        const data = resp.data
        this.tplKwarg = data.display_form_field
      })
    },
    handleChangeStateType(value) {
      if(value === 1){
        delete this.curRecord.participant_type
        delete this.curRecord.participant
        delete this.curRecord.distribute_type
      }
    },
    handleChangeParticipantType(value) {
      delete this.curRecord.participant
      if([2, 3, 5].indexOf(value) >= 0){
        delete this.curRecord.distribute_type
      }
    },
    newState () {
      this.visible = true
      this.isNewState = true
      this.curRecord = {}
    },
    updateState (record) {
      this.visible = true
      this.isNewState = false
      this.curRecord = record
    },
    removeState (record) {
      ticketFlowApi.deleteWorkflowState(record.id).then(resp => {
        if (resp.code === "0000") {
          notification.info({
            message: '创建状态',
            description: "提交成功",
          })
          this.fetchStateData()
        } else {
          notification.error({
            message: '创建状态',
            description: resp.message,
          })
        }
      }) 
    },
    commitState() {
      this.$refs.ruleForm.validate(valid => {
        if (!valid) {
          return false
        }
        if(this.isNewState) {
          let data = { ...this.curRecord }
          data["workflow"] = this.currentTplData.id
          ticketFlowApi.createWorkflowState(data).then(resp => {
            if (resp.code === "0000") {
              notification.info({
                message: '创建状态',
                description: "提交成功",
              })
              this.fetchStateData()
              this.visible = false
            } else {
              notification.error({
                message: '创建状态',
                description: resp.message,
              })
            }
          })       
        } else {
          ticketFlowApi.updateWorkflowState(this.curRecord.id, this.curRecord).then(resp => {
            if (resp.code === "0000") {
              notification.info({
                message: '更新状态',
                description: "提交成功",
              })
              this.fetchStateData()
              this.visible = false
            } else {
              notification.error({
                message: '更新状态',
                description: resp.message,
              })
            }
          })
        }
      })
    },
    cancelModal() {
      this.$refs.ruleForm.resetFields()
      this.visible = false
      this.fetchStateData()
    },
  },
}
</script>

