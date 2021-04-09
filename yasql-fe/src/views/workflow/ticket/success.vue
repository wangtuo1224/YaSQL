<template>
  <a-card :bordered="false">
    <a-result status="success" title="提交成功" sub-title="">
      <template #extra>
        <router-link :to="{ name: 'ticket.detail', params: { pk: tid }}">
          <a-button type="primary">工单详情</a-button>
        </router-link>
        <router-link :to="{ name: 'ticket.new', params: { pk: tplid }}">
          <a-button style="margin-left: 8px">再次创建</a-button>
        </router-link>
      </template>
    </a-result>
  </a-card>
</template>

<script>

export default {
  name: 'Success',
  data () {
    return {
      tid: this.$route.query.tid,
      tplid: this.$route.query.tplid,
    }
  },
}
</script>