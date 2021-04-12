<template>
  <a-table
    :columns="columns"
    :dataSource="ticketList"
    :rowKey="record => record.id"
    :loading="loading"
    :pagination="pagination"
    @change="handlePageChange"
    size="middle"
    :scroll="{ x: 1100}"
    >
    <template slot="id" slot-scope="text">
      <router-link :to="{ name: 'ticket.detail', params: {pk: text}}">
        <a size="small" style="margin: 2px">#{{ text }}</a>
      </router-link>
    </template>
    <template slot="status" slot-scope="text">
      {{ text | formatStatus }}
    </template>
    <template slot="formatTime" slot-scope="text">
      <small>{{ text | formatTime }}</small>
    </template>
    <template slot="action" slot-scope="record">
      <router-link :to="{ name: 'ticket.detail', params: {pk: record.id}}">
        <a size="small" style="margin: 2px">详情</a>
      </router-link>
    </template>
  </a-table>
</template>

<script>
import moment from 'moment'
import { TicketActState } from '@/utils/ticket.js'


export default {
  props: {
    loading: Boolean,
    ticketList: Array,
    pagination: Object
  },
  data () {
    return {
      columns: [
        {
          'title': '工单编号',
          'dataIndex': 'id',
          'scopedSlots': { customRender: 'id' }
        },
        {
          'title': '工单类型',
          'dataIndex': 'workflow',
        },
        {
          'title': '工单状态',
          'dataIndex': 'act_status',
          'scopedSlots': { customRender: 'status' }
        },
        {
          'title': '申请人',
          'dataIndex': 'creator',
        },
        {
          'title': '创建时间',
          'dataIndex': 'created_at',
          'scopedSlots': { customRender: 'formatTime' }
        },
        {
          'title': '操作',
          'scopedSlots': { customRender: 'action' }
        },
      ],
    }
  },
  filters: {
    formatTime(value) {
      if(value){
        return moment(value).format('YYYY-MM-DD HH:mm:ss')
      } else {
        return ''
      }
    },
    formatStatus(value) {
      const data = {}
      for (const status of TicketActState) {
        data[status.key.toString()] = status.value
      }
      return data[value.toString()]
    },
  },
  methods: {
    handlePageChange(pager) {
      this.$emit('pageChange', pager)
    },
  }
}
</script>
