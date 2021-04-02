<template>
  <a-card>
    <div class="table-page-search-wrapper">
      <a-form layout="inline" :form="form" @keyup.enter.native="handleSearch">
        <a-row :gutter="48">
          <a-col :md="4" :sm="24" style="padding-right: 0px;">
            <a-form-item>
              <a-select placeholder="我的工单" v-decorator="decorator['my_action']">
                <a-select-option v-for="s in ticketAct" :key="s.key" :value="s.key">{{ s.value }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :md="4" :sm="24" style="padding-right: 0px;">
            <a-form-item>
              <a-select placeholder="工单类型" v-decorator="decorator['workflow_tpl']">
                <a-select-option v-for="s in workflowTpl" :key="s.id" :value="s.id">{{ s.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :md="3" :sm="24" style="padding-right: 0px;">
            <a-form-item>
              <a-select placeholder="工单状态" v-decorator="decorator['act_status']">
                <a-select-option v-for="s in ticketState" :key="s.key" :value="s.key">{{ s.value }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :md="5" :sm="24" style="padding-right: 0px;">
            <a-form-item>
              <a-range-picker :placeholder="['创建日期', '']" v-decorator="decorator['created_at']" />
            </a-form-item>
          </a-col>
          <a-col :md="4" :sm="24" style="padding-right: 0px;">
            <a-form-item>
              <a-input placeholder="工单内容" v-decorator="decorator['search']" />
            </a-form-item>
          </a-col>
          <a-col :md="4" :sm="24">
            <span class="table-page-search-submitButtons">
              <a-button type="primary" @click="handleSearch" icon="search">查询</a-button>
              <a-button @click="resetForm" style="margin-left: 8px">重置</a-button>
            </span>
          </a-col>
        </a-row>
        <TicketTable 
          :loading="loading"
          :ticketList="ticketList" 
          :pagination="pagination" 
          @pageChange="handleCurrentPageChange" 
          />
      </a-form>
    </div>
  </a-card>
</template>

<script>
import moment from 'moment'
import { TicketActState, TicketAct } from '@/utils/ticket.js'
import ticketFlowApi from "@/api/workflow.js"
import TicketTable from './table.vue'


export default {
  name: 'ticketFlowList',
  components: {
    TicketTable
  },

  data () {
    return {
      loading: false,
      ticketState: TicketActState,
      ticketAct: TicketAct,
      workflowTpl: null,
      ticketList: [],
      pagination: {
        current: 1, 
        pageSize: 10,
        total: 0, 
        pageSizeOptions: ["10", "20", "30"], 
        showSizeChanger: true,
      },
      filters: {
        my_action: null,
        workflow_tpl: null,
        act_status: null,
        created_at: null,
        search: null,
      },
      form: this.$form.createForm(this),
      decorator: {
        'my_action': ['my_action', {rules: [{ required: false }]}],
        'workflow_tpl': ['workflow_tpl', {rules: [{ required: false }]}],
        'act_status': ['act_status', {rules: [{ required: false }]}],
        'created_at': ['created_at', {rules: [{ required: false }]}],
        'search': ['search', {rules: [{ required: false }]}],
      },
    }
  },

  created() {
    this.fetchData()
    this.fetchWorkflowSummary()
  },

  methods: {
    fetchData() {
      const params = {
        page_size: this.pagination.pageSize,
        page: this.pagination.current,
        ...this.filters,
      }
      ticketFlowApi.getTicketList(params).then(resp => {
        this.ticketList = resp.results
        this.pagination.total = resp.count
      })
    },
    fetchWorkflowSummary() {
      const params = {
        page_size: -1,
        page: 1,
      }
      ticketFlowApi.getWorkflowSummary(params).then(resp => {
        const workflowGroup = resp.results.map(function(obj) {
          var rObj = []
          for(var i of obj.children) {
            rObj.push({
              "id": i.wf_id,
              "name": i.name,
            })
          }
          return rObj
        })
        this.workflowTpl = workflowGroup.flat()
      }).catch(error => {
        console.log(error)
      })
    },
    handleSearch(e) {
      e.preventDefault()
      this.form.validateFields((error, values) => {
        if(error){
          return 
        }

        const tmp_val = {
          'my_action': values['my_action'],
          'workflow_tpl': values['workflow_tpl'],
          'act_status': values['act_status'],
          'start_created_at': values['created_at'] ? moment(values['created_at'][0]).format('YYYY-MM-DD'): undefined,
          'end_created_at': values['created_at'] ? moment(values['created_at'][1]).format('YYYY-MM-DD'): undefined,
          'search': values['search'],
        }
        this.filters = tmp_val
        this.pagination.current = 1
        this.loading = true  // 手动搜索时触发遮罩层
        this.fetchData()
        this.loading = false
      })
    },
    resetForm() {
      this.form.resetFields()
    },
    handleCurrentPageChange(pager) {
      this.pagination.current = pager.current
      this.pagination.pageSize = pager.pageSize
      this.loading = true  // 翻页时触发遮罩层
      this.fetchData()
      this.loading = false
    },
  }
}
</script>

