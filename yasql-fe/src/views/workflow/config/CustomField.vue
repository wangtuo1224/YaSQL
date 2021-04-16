<template>
  <a-card :bordered="false" title="工单字段">
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
              :min="1"
              placeholder="前端表单根据此值顺序展示"
              v-decorator="[`${index}__order_id`, {rules: [{ validator: checkOrderID }], validateTrigger: 'blur', initialValue: v[`${index}__order_id`]}]" />
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
        <a-col :md="16" :sm="24" v-if='["select", "multiselect"].indexOf(filedFlag[index])>=0 || v[`${index}__field_value`]'>
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
</template>


<script>


export default {
  props: {
    tplKwarg: Array,
  },
  data () {
    return {
      filedFlag: {},
      categoryList: [{key: "string", value: "字符串"}, 
              {key: "integer", value: "整型"},
              {key: "boolean", value: "布尔值"},
              {key: "textarea", value: "文本框"},
              {key: "select", value: "单选下拉列表"},
              {key: "multiselect", value: "多选下拉列表"},
              {key: "file", value: "附件"},
              {key: "user", value: "用户"}],
      formItemLayoutWithOutLabel: {
        wrapperCol: {
          xs: { span: 24, offset: 0 },
          sm: { span: 20, offset: 4 },
        },
      },
    }
  },
  computed: {
    keysInitialValue() {
      // console.log(this.tplKwarg)
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
    checkOrderID(rule, value, callback) {
      if(!value) {
        callback(new Error("字段顺序必填"))
      }
      const kw = this.tplKwarg.filter(x => x.order_id.toString() === value)
      if(kw.length > 1){
        callback(new Error("字段顺序必须唯一"))
      } else {
        callback() 
      } 
    },
    filedChangeCategory(e, index) {
      this.filedFlag[index] = e
      const data = {
        "field_name": null,
        "field_key": null,
        "field_type": e,
        "required": false,
        "order_id": 1,
        "default_value": null,
        "placeholder": null,
        "field_value": null,    
      }
      this.$set(this.tplKwarg, index, data)
      this.$emit('update:tplKwarg', this.tplKwarg)
    },
    addField() {
      const item = {
        "field_name": null,
        "field_key": null,
        "field_type": "string",
        "required": false,
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
  }
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