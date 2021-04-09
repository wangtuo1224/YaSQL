<template>
  <a-card>
    <div class="table-page-search-wrapper">
      <a-form layout="inline" :form="form" @keyup.enter.native="handleSearch">
        <a-row :gutter="48">
          <a-col :md="6" :sm="24" style="padding-right: 0px;" align="right">
            <a-form-item>
              <a-input placeholder="工单组" v-decorator="decorator['name']" />
            </a-form-item>
          </a-col>
          <a-col :md="4" :sm="24" align="right">
            <span class="table-page-search-submitButtons">
              <a-button type="primary" @click="handleSearch" icon="search">查询</a-button>
              <a-button @click="resetForm" style="margin-left: 8px">重置</a-button>
            </span>
          </a-col>
        </a-row>
        <a-table
          :columns="columns"
          :dataSource="workflowGroupData"
          :rowKey="record => record.id"
          :loading="loading"
          :pagination="pagination"
          @change="handlePageChange"
          size="middle"
          :scroll="{ x: 1100}"
          >
          <template slot="action" slot-scope="record">
            <a-button size="small" @click="openModal(record)">修改</a-button>
            <router-link :to="{ name: 'workflow.template.new', params: {pk: record.id}}">
              <a-button size="small" style="margin: 2px">新建流程</a-button>
            </router-link>
          </template>
        </a-table>
      </a-form>
    </div>
    <a-modal v-model="visible" title="修改名称" ok-text="确认" cancel-text="取消" @ok="updateTpl">
      <a-form-model layout="inline" :model="curWorkflowGroup" @submit="updateTpl" @submit.native.prevent>
        <a-form-model-item>
          <a-input v-model="curWorkflowGroup.name" placeholder="name" />
        </a-form-model-item>
      </a-form-model>
    </a-modal>
  </a-card>
</template>

<script>
import ticketFlowApi from "@/api/workflow.js"
import notification from 'ant-design-vue/es/notification'


export default {
  name: 'workflowGroup',

  data () {
    return {
      loading: false,
      visible: false,
      workflowGroupData: null,
      curWorkflowGroup: {
        "id": null,
        "name": null,
      },
      pagination: {
        current: 1, 
        pageSize: 10,
        total: 0, 
        pageSizeOptions: ["10", "20", "30"], 
        showSizeChanger: true,
      },
      filters: {
        name: null,
      },
      form: this.$form.createForm(this),
      decorator: {
        'name': ['name', {rules: [{ required: false }]}],
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
        this.workflowGroupData = resp.results
        this.pagination.total = resp.count
      })
    },
    handleSearch(e) {
      e.preventDefault()
      this.form.validateFields((error, values) => {
        if(error){
          return 
        }
        this.filters["name"] = values["name"]
        this.pagination.current = 1
        this.loading = true  // 手动搜索时触发遮罩层
        this.fetchWorkflowGroupData()
        this.loading = false
      })
    },
    resetForm() {
      this.form.resetFields()
    },
    handlePageChange(pager) {
      this.pagination.current = pager.current
      this.pagination.pageSize = pager.pageSize
      this.loading = true  // 翻页时触发遮罩层
      this.fetchWorkflowGroupData()
      this.loading = false
    },
    addGroup() {

    },
    openModal(data) {
      this.visible = true
      this.curWorkflowGroup = Object.assign({}, {"id": data.id , "name": data.name})
    },
    updateTpl() {
      ticketFlowApi.updateWorkflowGroup(this.curWorkflowGroup.id, this.curWorkflowGroup).then(resp => {
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
        this.fetchWorkflowGroupData()
        this.visible = false
      })
    },
  }
}
</script>

