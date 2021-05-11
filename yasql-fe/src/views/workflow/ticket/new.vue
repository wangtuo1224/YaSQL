<template>
  <a-form :form="form" v-if="tpl">
    <a-spin :spinning="pushing">
      <a-card style="margin: 5px">
        <a-row :gutter="48">
          <a-col :md="18" :sm="18">
            <h4>{{ tpl.name }}</h4>
            <small>{{ tpl.description }}</small>
          </a-col>
          <a-col :md="6" :sm="6">
            <div style="text-align:right">
              <a-button type="primary" style="margin: 5px" @click="handleNewTicket">提交</a-button>
            </div>
          </a-col>
        </a-row>
        <a-divider />
        <div style="text-align:center">
          <a-form-item v-for="(item, index) in tpl.display_form_field" :key="index"
            :label="item.field_name"
            :labelCol="{lg: {span: 4}, sm: {span: 4}}"
            align="left"
            :wrapperCol="{lg: {span: 16 }, sm: {span: 16} }">
              <a-input v-if="item.field_type==='string'"
                v-decorator="[item.field_key, {rules: [{ required: item.required }], initialValue: item.default_value}]"
                :placeholder="item.placeholder" />
              <a-input-number v-if="item.field_type==='integer'" 
                v-decorator="[item.field_key, {rules: [{ required: item.required }], initialValue: item.default_value}]" 
                :placeholder="item.placeholder" />
              <a-switch v-if="item.field_type==='boolean'"
                v-decorator="[item.field_key, {rules: [{ required: item.required }], initialValue: ['true', 'True'].indexOf(item.default_value)>=0, valuePropName: 'checked'}]" />
              <a-textarea v-if="item.field_type==='textarea'"
                v-decorator="[item.field_key, {rules: [{ required: item.required }], initialValue: item.default_value}]"  
                :autoSize="{ minRows: 5, maxRows: 10 }"
                :placeholder="item.placeholder" />
              <a-select v-if="item.field_type==='select'"
                v-decorator="[item.field_key, {rules: [{ required: item.required }], initialValue: item.default_value}]" 
                :placeholder="item.placeholder">
                <a-select-option v-for="(value, key, index) in JSON.parse(item.field_value)" :key="index" :value="value">
                  {{ key }}
                </a-select-option>
              </a-select>
              <a-select v-if="item.field_type==='multiselect'" mode="multiple"
                v-decorator="[item.field_key, {rules: [{ required: item.required }]}]"  
                :placeholder="item.placeholder">
                <a-select-option v-for="(value, key, index) in JSON.parse(item.field_value)" :key="index" :value="value">
                  {{ key }}
                </a-select-option>
              </a-select>
              <a-upload v-if="item.field_type==='file'"
                :fileList="fileList"
                :customRequest="handleUpload"
                :remove="handleRemove">
                <a-button :disabled="fileList.length > 0 || uploading" type="primary"> 
                  <a-icon type="upload" /> {{ uploading ? '已上传' : '上传文件' }} 
                </a-button>
              </a-upload>
              <!-- 用户类型待处理 -->
          </a-form-item>
        </div>
      </a-card>
    </a-spin>
  </a-form>
</template>

<script>
import ticketFlowApi from "@/api/workflow.js"


export default {
  name: 'ticketNew',
  props: {
    pk: [Number, String]
  },
  data () {
    return {
      tpl: null,
      pushing: false,
      uploading: false,
      fileList: [],
      fileObj: {
        "key": null,
        "value": null
      },
      form: this.$form.createForm(this),
    }
  },

  mounted() {
    this.getTicketTemplateData()
  },

  methods: {
    getTicketTemplateData() {
      ticketFlowApi.getTicketTemplate(this.pk).then(resp => {
        this.tpl = resp.data
        const f = this.tpl.display_form_field.filter(x => x.field_type ==='file')
        if(f.length >0) {
          this.fileObj["key"] = f[0]["field_key"]
        }
      })
    },
    handleUpload(data) {
      const formData = new FormData()
      this.uploading = true
      formData.append('file', data.file)
      ticketFlowApi.uploadFile(formData).then(resp => {
        if (resp.code === "0000") {
          this.fileList.push(data.file)
          this.fileObj["value"] = resp.data.file_name
        } else {
          this.$message.error("上传附件错误")
        }
      }).catch(error => {
        this.$message.error("上传附件失败")
      })
    },
    handleRemove(file) {
      const index = this.fileList.indexOf(file)
      const newFileList = this.fileList.slice()
      newFileList.splice(index, 1)
      this.fileList = newFileList
      this.uploading = false
    },
    handleNewTicket(e) {
      e.preventDefault()
      this.form.validateFields((error, values) => {
        if (error) {
          return
        }
        // 增加附件
        if(this.fileList.length > 0) {
          values[this.fileObj["key"]] = this.fileObj["value"]
        }
        const data = {
          "field_kwargs": values,
          "workflow": this.pk,
        }
        this.pushing = true
        ticketFlowApi.createTicket(data).then(resp => {
          if(resp.code === "0000") {
            this.ticketInfo = resp.data
            this.$router.push({
              path: "/workflow/ticket/success", 
              query: {
                tid: this.ticketInfo.id,
                tplid: this.tpl.id,
              }
            })
          } else {
            this.$message.error(resp.message)
          }
        }).finally(() => {
          this.pushing = false
        })
      })
    },
  }
}
</script>

<style scoped>
  .ant-form-item {
    margin-bottom: 5px;
  }
</style>
