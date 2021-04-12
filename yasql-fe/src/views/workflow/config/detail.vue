<template>
  <a-form :form="form" v-if="currentTplData.group">
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
        <WorkflowTpl
          :currentTplData="currentTplData" 
        />
      </a-card>
      <!-- 动态参数部分  -->
      <CustomField 
        :tplKwarg="tplKwarg"
      />
    </a-spin>
  </a-form>
</template>


<script>
import ticketFlowApi from "@/api/workflow.js"
import notification from 'ant-design-vue/es/notification'
import WorkflowTpl from './WorkflowTpl.vue'
import CustomField from './CustomField.vue'


export default {
  name: 'templateDetail',
  components: {
    WorkflowTpl,
    CustomField
  },
  props: {
    pk: [Number, String]
  },
  data () {
    return {
      pushing: false,
      form: this.$form.createForm(this),
      currentTplData: {
        "group": null,
      },
      tplKwarg: [], 
    }
  },
  beforeCreate() {
    this.form = this.$form.createForm(this, { name: 'dynamic_form_item' })
  },
  created() {
    this.fetchWorkflowTplData()
  },
  methods: {
    fetchWorkflowTplData() {
      ticketFlowApi.getTicketTemplate(this.pk).then(resp => {
        this.currentTplData = resp.data
        this.tplKwarg = this.currentTplData.display_form_field
        this.$nextTick(() => {
          this.form.setFieldsValue({
            name: this.currentTplData.name,
            description: this.currentTplData.description,
            all_view: this.currentTplData.all_view,
            display_form: this.currentTplData.display_form,
          })})
      })
    },
    handleNewTicket (e) {
      e.preventDefault()
      let data = {}
      this.form.validateFields((err, values) => {
        if (err) {
          return
        }
        data = {
          "name": values["name"],
          "description": values["description"],
          "all_view": values["all_view"],
          "display_form": values["display_form"],
          "field_kwargs": [],
        }
        if(this.tplKwarg.length === 0){
          notification.error({
            message: '工作流程',
            description: '必须有一个工单字段',
          })
          return false
        }
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
                const f = JSON.parse(k["field_value"])
                // 判断f类型
                if(typeof(f) !== "object" || f.constructor !== Object){
                  notification.error({
                    message: '工作流程',
                    description: `${k['field_name']}应为json格式键值对,如:{"1":"需要","0":"不需要"}'`,
                  })
                  return false
                }
              } catch(e) {
                notification.error({
                  message: '工作流程',
                  description: `${k['field_name']}应为json格式键值对,如:{"1":"需要","0":"不需要"}'`,
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
        this.pushing = true
        ticketFlowApi.updateWorkflowTpl(this.pk, data).then(resp => {
          if (resp.code === "0000") {
            this.$router.push({ name: 'workflow.group' })
          } else {
            notification.error({
              message: '更新工作流程',
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
