<template>
  <a-card v-if="tplSummary">
    <a-list size="large"
        :loading="loading"
        :dataSource="tplSummary"
        :pagination="pagination"
        >
        <a-collapse :bordered="false">
          <template #expandIcon="props">
            <a-icon type="caret-right" :rotate="props.isActive ? 90 : 0" />
          </template>
          <a-collapse-panel :header="group.name" v-for="group in tplSummary" :key="group.wg_id">
            <a-list :grid="{ gutter: 16, column: 4 }" :data-source="group.children">
              <a-list-item slot="renderItem" slot-scope="item" class="ant-aaa">
                <router-link :to="{ name: 'ticket.new', params: { pk: item.wf_id }}">
                  <a-card>
                    <a-list-item-meta :description="item.description">
                      <a slot="title">{{ item.name }}</a>
                    </a-list-item-meta>
                  </a-card>
                </router-link>
              </a-list-item>
            </a-list>
          </a-collapse-panel>
        </a-collapse>
    </a-list>
  </a-card>
</template>

<script>
import workflowApi from "@/api/workflow.js"


export default {
  name: 'workFlowSummary',
  data () {
    return {
      loading: false,
      tplSummary: null,
      pagination: {
        current: 1, 
        pageSize: 15,
        total: 0, 
        onChange: page => {
          this.pagination.current = page
          this.fetchWorkflowSummary()
        },
      },
    }
  },

  created() {
    this.fetchWorkflowSummary()
  },

  methods: {
    fetchWorkflowSummary() {
      const params = {
        page_size: this.pagination.pageSize,
        page: this.pagination.current,
      }
      workflowApi.getWorkflowSummary(params).then(resp => {
        this.tplSummary = resp.results
        this.pagination.total = resp.count
        this.loading = false
      }).catch(error => {
        console.log(error)
      }).finally(() => {
        this.loading = false
      })
    },
  },
}
</script>

<style lang="less" scope>
  .ant-aaa {
    .ant-card-body {
      background-color:#f7f7f7;
    }
    .ant-card-body:hover {
      background-color:#e7edf1 !important;
    }
  }
  .ant-collapse-borderless {
    background-color: #ffffff;
  }
</style>
