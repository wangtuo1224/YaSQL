<template>
  <a-card>
    <div class="table-page-search-wrapper">
      <a-form layout="inline" :form="form" @keyup.enter.native="handleSearch">
        <a-row :gutter="48" align="right">
          <a-col :md="6" :sm="24" style="padding-right: 0px;">
            <a-form-item>
              <a-input placeholder="工单组" v-decorator="decorator['search']" />
            </a-form-item>
          </a-col>
          <a-col :md="4" :sm="24">
            <span class="table-page-search-submitButtons">
              <a-button type="primary" @click="handleSearch" icon="search">查询</a-button>
              <a-button @click="resetForm" style="margin-left: 8px">重置</a-button>
            </span>
          </a-col>
        </a-row>
        <div class="operate">
          <a-button type="dashed" style="width: 100%" icon="plus" @click="add">添加工单组</a-button>
        </div>
        <a-table
          :columns="columns"
          :dataSource="workflowGroup"
          :rowKey="record => record.id"
          :loading="loading"
          :pagination="pagination"
          @change="handlePageChange"
          size="middle"
          :scroll="{ x: 1100}"
          >
          <template slot="formatTime" slot-scope="text">
            <small>{{ text | formatTime }}</small>
          </template>
          <template slot="action" slot-scope="record">
            <router-link :to="{ name: 'ticket.detail', params: {pk: record.id}}">
              <a size="small" style="margin: 2px">详情</a>
            </router-link>
          </template>
        </a-table>
      </a-form>
    </div>
  </a-card>
</template>

<script>
import ticketFlowApi from "@/api/workflow.js"


export default {
  name: 'workflowGroup',

  data () {
    return {
      loading: false,
      workflowGroup: null,
      pagination: {
        current: 1, 
        pageSize: 10,
        total: 0, 
        pageSizeOptions: ["10", "20", "30"], 
        showSizeChanger: true,
      },
      filters: {
        search: null,
      },
      form: this.$form.createForm(this),
      decorator: {
        'search': ['search', {rules: [{ required: false }]}],
      },
      columns: [
        {
          'title': '工单组ID',
          'dataIndex': 'id',
        },
        {
          'title': '工单组名',
          'dataIndex': 'name',
        },
        {
          'title': '操作',
          'scopedSlots': { customRender: 'action' }
        },
      ],
    }
  },

  created() {
    this.fetchWorkflowGroupData()
  },

  methods: {
    fetchWorkflowGroupData() {
      const params = {
        page_size: this.pagination.pageSize,
        page: this.pagination.current,
        ...this.filters,
      }
      ticketFlowApi.getWorkflowGroup(params).then(resp => {
        this.workflowGroup = resp.results
        this.pagination.total = resp.count
      })
    },
    handleSearch(e) {
      e.preventDefault()
      this.form.validateFields((error, values) => {
        if(error){
          return 
        }
        this.filters["search"] = values["search"]
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

