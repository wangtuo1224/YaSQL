<template>
  <a-card>
    <a-row :gutter="48">
      <a-col :md="18" :sm="18">
        <h3>工作流程</h3>
      </a-col>
      <a-col :md="6" :sm="6">
        <div style="text-align:right">
          <a-button type="primary" style="margin: 5px" @click="handleTicket">提交</a-button>
        </div>
      </a-col>
    </a-row>
    <a-divider />
    <a-form-item 
      label="流程组"
      :labelCol="{lg: {span: 4}, sm: {span: 4}}"
      :wrapperCol="{lg: {span: 16}, sm: {span: 20} }">
      <span>{{ currentTplData.group.name }}</span>
    </a-form-item>
    <a-form-item label="名称"
      :labelCol="{lg: {span: 4}, sm: {span: 4}}"
      :wrapperCol="{lg: {span: 16}, sm: {span: 20} }">
      <a-input
        v-decorator="decorator['name']"
        placeholder="流程名称" />
    </a-form-item>
    <a-form-item label="描述"
      :labelCol="{lg: {span: 4}, sm: {span: 4}}"
      :wrapperCol="{lg: {span: 16}, sm: {span: 20}}">
      <a-input v-decorator="decorator['description']" placeholder="描述名称的功能" />
    </a-form-item>
    <a-form-item label="工单可见性"
      :labelCol="{lg: {span: 4}, sm: {span: 4}}"
      :wrapperCol="{lg: {span: 16}, sm: {span: 20}}">
      <a-switch v-decorator="decorator['all_view']" />
      <a-tooltip placement="rightBottom" title="默认所有人可见，否则只有工单相关人可见">
        <a-icon type="question-circle" style="margin-left: 5px" />
      </a-tooltip>
    </a-form-item>
    <a-form-item label="表单显示字段"
      :labelCol="{lg: {span: 4}, sm: {span: 4}}"
      :wrapperCol="{lg: {span: 16}, sm: {span: 20}}">
      <a-input v-decorator="decorator['display_form']" placeholder="提交工单时对用户可见字段" />
    </a-form-item>
  </a-card>
</template>


<script>
export default {
  props: {
    currentTplData: Object,
  },
  data () {
    const checkDisplayForm = (rule, value, callback) => {
      if(!value) {
        callback( new Error("表单中可见字段必填"))
      } 
      try {
        const f = JSON.parse(value)
        if((typeof(f) === "object") && f.constructor === Array){
          callback()
        } else {
          callback(new Error('表单显示字段格式错误，请配置成：["id","title"]'))
        }
      } catch(e) {
        callback(new Error('表单显示字段格式错误，请配置成：["id","title"]'))
      } 
    }
    return {
      decorator: {
        'name': ['name', {rules: [{ required: true,  message: '请输入流程名称' }]}],
        'description': ['description', {rules: [{ required: true, message: '流程描述' }]}],
        'all_view': ['all_view', {rules: [{ required: false }], initialValue: true, valuePropName: 'checked'}],
        'display_form': ['display_form', {rules: [{ validator: checkDisplayForm }], validateTrigger: 'blur'}]
      },
    }
  },
  methods: {
    handleTicket(e) {
      this.$emit('handlePushTpl', e)
    },
  }
}
</script>