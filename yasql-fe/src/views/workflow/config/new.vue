<template>
  <a-form :form="form" v-if="currentGroup">
    <a-spin :spinning="pushing">
      <a-card style="margin: 5px">
        <a-row :gutter="48">
          <a-col :md="18" :sm="18">
            <h3>创建工作流程</h3>
          </a-col>
          <a-col :md="6" :sm="6">
            <div style="text-align:right">
              <a-button type="primary" style="margin: 5px" @click="handleNewTicket">提交</a-button>
            </div>
          </a-col>
        </a-row>
        <a-divider />
        <a-form-item 
          label="流程组"
          :labelCol="{lg: {span: 4}, sm: {span: 4}}"
          :wrapperCol="{lg: {span: 16}, sm: {span: 20} }">
          <span>{{ currentGroup.name }}</span>
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
          <a-tooltip placement="rightBottom" title="默认是所有人可见，勾选后只有工单相关人可见">
            <a-icon type="question-circle" style="margin-left: 5px" />
          </a-tooltip>
        </a-form-item>
        <a-form-item label="表单显示字段"
          :labelCol="{lg: {span: 4}, sm: {span: 4}}"
          :wrapperCol="{lg: {span: 16}, sm: {span: 20}}">
          <a-input v-decorator="decorator['display_form']" placeholder="提交工单时对用户可见字段" />
        </a-form-item>
      </a-card>
      <!-- 动态参数部分  -->
      <a-card :bordered="false" title="工单字段" style="margin: 5px">
        <a-card v-for="(v, index) in keysInitialValue" :key="index">
          <a-row :gutter="10">
            <a-col :md="8" :sm="24">
              <a-form-item
                label="字段名"
                :labelCol="{lg: {span: 6}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 18}, sm: {span: 24}}">
                <a-input
                  placeholder="字段显示的名称（中文名）"
                  v-decorator="[`${index}__field_name`, {rules: [{ required: true }], initialValue: v[`${index}__field_name`]}]" />
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24">
              <a-form-item
                label="字段key"
                :labelCol="{lg: {span: 6}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 18}, sm: {span: 24}}" >
                <a-input
                  placeholder="字段唯一标识"
                  v-decorator="[`${index}__field_key`, {rules: [{ required: true }], initialValue: v[`${index}__field_key`]}]" />
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24">
              <a-form-item
                label="字段类型"
                :labelCol="{lg: {span: 6}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 18}, sm: {span: 24}}">
                <a-select
                  placeholder="字段类型"
                  @change="filedChangeCategory($event, index)"
                  v-decorator="[`${index}__field_type`, {rules: [{ required: true }], initialValue: v[`${index}__field_type`]}]">
                  <a-select-option v-for="(item, index) in categoryList" :key="index" :value='item.key'>
                    {{ item.value }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
          <a-row :gutter="10">
            <a-col :md="8" :sm="24">
              <a-form-item
                label="字段顺序"
                :labelCol="{lg: {span: 6}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 18}, sm: {span: 24}}">
                <a-input-number
                  placeholder="前端表单根据此值顺序展示"
                  v-decorator="[`${index}__order_id`, {rules: [{ required: true }], initialValue: v[`${index}__order_id`]}]" />
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24" v-if='filedFlag[index] !== "file"'>
              <a-form-item
                label="默认值"
                :labelCol="{lg: {span: 6}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 18}, sm: {span: 24}}">
                <a-input
                  placeholder="字段的默认值"
                  v-decorator="[`${index}__default_value`, {rules: [{ required: false }], initialValue: v[`${index}__default_value`]}]" />
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="24">
              <a-form-item
                label="字段占位符"
                :labelCol="{lg: {span: 6}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 18}, sm: {span: 24}}">
                <a-input
                  placeholder="表单中字段的占位符"
                  v-decorator="[`${index}__placeholder`, {rules: [{ required: false }], initialValue: v[`${index}__placeholder`]}]" />
              </a-form-item>
            </a-col>
            <a-col :md="16" :sm="24" v-if='["select", "multiselect"].indexOf(filedFlag[index])>=0'>
              <a-form-item
                label="字段数据"
                :labelCol="{lg: {span: 3}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 21}, sm: {span: 24}}">
                <a-input
                  placeholder='select/multiselect选项值，如:{"1":"需要","0":"不需要"}'
                  v-decorator="[`${index}__field_value`, {rules: [{ required: false }], initialValue: v[`${index}__field_value`]}]" />
              </a-form-item>
            </a-col>
            <a-col :md="4" :sm="24" v-if='filedFlag[index] !== "file"'>
              <a-form-item
                label="是否必填"
                :labelCol="{lg: {span: 12}, sm: {span: 24}}"
                :wrapperCol="{lg: {span: 6}, sm: {span: 24}}">
                <a-checkbox v-decorator="[`${index}__required`, {rules: [{ required: false }], initialValue: v[`${index}__required`], valuePropName: 'checked'}]">
                </a-checkbox>
              </a-form-item>
            </a-col>
            <a-col :md="4" :sm="24" style="text-align:right">
              <a-icon
                v-if="keysInitialValue.length > 0"
                class="dynamic-delete-button"
                type="minus-circle-o"
                @click="() => removeField(index)" />
            </a-col>
          </a-row>
        </a-card>
        <a-form-item v-bind="formItemLayoutWithOutLabel">
          <a-button type="dashed" style="width: 60%" @click="addField">
            <a-icon type="plus" /> 增加字段
          </a-button>
        </a-form-item>
        <a-divider />
      </a-card>
    </a-spin>
  </a-form>
</template>


<script>
import ticketFlowApi from "@/api/workflow.js"
import notification from 'ant-design-vue/es/notification'


export default {
  name: 'templateNew',
  props: {
    pk: [Number, String]
  },
  data () {
    return {
      pushing: false,
      form: this.$form.createForm(this),
      currentGroup: null,
      tplKwarg: [],
      filedFlag: {},
      categoryList: [{key: "string", value: "字符串"}, 
                    {key: "integer", value: "整型"},
                    {key: "boolean", value: "布尔值"},
                    {key: "textarea", value: "文本框"},
                    {key: "select", value: "单选下拉列表"},
                    {key: "multiselect", value: "多选下拉列表"},
                    {key: "file", value: "附件"},
                    {key: "user", value: "用户"}],
      decorator: {
        'name': ['name', {rules: [{ required: true,  message: '请输入流程名称' }]}],
        'description': ['description', {rules: [{ required: true, message: '流程描述' }]}],
        'all_view': ['all_view', {rules: [{ required: false }], initialValue: false, valuePropName: 'checked'}],
        'display_form': ['display_form', {rules: [{ required: true, message: '表单中可见字段' }]}]
      },

      formItemLayoutWithOutLabel: {
        wrapperCol: {
          xs: { span: 24, offset: 0 },
          sm: { span: 20, offset: 4 },
        },
      },
    }
  },
  beforeCreate() {
    this.form = this.$form.createForm(this, { name: 'dynamic_form_item' })
  },
  created() {
    this.fetchGroupData()
  },
  computed: {
    keysInitialValue() {
      let initialValue = []
      for(var i=0; i<this.tplKwarg.length; i++) {
        let x = {}
        for(var y in this.tplKwarg[i]){
          if(this.tplKwarg[i][y] !== null){
            x[i+'__'+y] = this.tplKwarg[i][y]
          }
        }
        initialValue[i] = x
      }
      return initialValue
    }
  },
  methods: {
    fetchGroupData() {
      ticketFlowApi.getWorkflowGroupDetail(this.pk).then(resp => {
        this.currentGroup = resp.data
      })
    },
    addField() {
      const item = {
        "field_name": null,
        "field_key": null,
        "field_type": "string",
        "required": true,
        "order_id": 1,
        "default_value": null,
        "placeholder": null,
        "field_value": null,
      }
      this.tplKwarg.push(item)
    },
    removeField(index) {
      this.tplKwarg.splice(index, 1)
    },
    filedChangeCategory(e, index) {
      this.filedFlag[index] = e
    },
    handleNewTicket (e) {
      e.preventDefault()
      let data = {}
      this.form.validateFields((err, values) => {
        if (err) {
          return
        }
        data = {
          "group": this.pk,
          "name": values["name"],
          "description": values["description"],
          "all_view": values["all_view"],
          "display_form": values["display_form"],
          "field_kwargs": [],
        }
        if(this.tplKwarg.length > 0){
          for(var i=0;i<this.tplKwarg.length;i++){
            let k = {}
            for(var v in values){
              if(v.startsWith(i+'__')){
                const t = v.split('__')
                k[t[1]] = values[v]
              }
            }
            if(["select", "multiselect"].indexOf(k["field_type"])>=0) {
              if(k["field_value"]){
                try {
                  JSON.parse(k["field_value"])
                } catch(e) {
                  notification.error({
                    message: '工作流程',
                    description: `${k['field_name']}应为json格式`,
                  })
                  return false
                } 
              } else {
                notification.error({
                  message: '工作流程',
                  description: `${k['field_name']}为${k['field_type']}类型，字段数据必填`,
                })
                return false
              } 
            }
            data.field_kwargs[i] = k
          }
        }
        this.pushing = true
        ticketFlowApi.createWorkflowTpl(data).then(resp => {
          if (resp.code === "0000") {
            this.$router.push({ name: 'workflow.group' })
          } else {
            notification.error({
              message: '新建工作流程',
              description: resp.message,
            })
          }
        })      
        this.pushing = false
      })
    },
  },
}
</script>

<style lang="less" scoped>
  .ant-form-item {
    margin-bottom: 0px;
  }
  .dynamic-delete-button {
    cursor: pointer;
    position: relative;
    top: 4px;
    font-size: 24px;
    color: #1890ff;
    transition: all 0.3s;
  }
  .dynamic-delete-button:hover {
    color: #777;
  }
  .dynamic-delete-button[disabled] {
    cursor: not-allowed;
    opacity: 0.5;
  }
</style>