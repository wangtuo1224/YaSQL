<template>
  <a-card style="margin: 5px">
    <a-tabs type="card" :activeKey="activeKey" @change="callback">
      <a-tab-pane key="1" tab="流程模版">
        <a-spin :spinning="pushing">
          <a-form :form="form" v-if="currentTplData.group">
            <WorkflowTpl :currentTplData="currentTplData" @handlePushTpl="handlePushTpl" />
            <!-- 动态参数部分  -->
            <CustomField :tplKwarg.sync="tplKwarg" @updateTplKwarg="updateTplKwarg" />
          </a-form>
        </a-spin>
      </a-tab-pane>
      <a-tab-pane key="2" tab="状态" :disabled="disableTab">
        <a-form :form="form">
          <State :currentTplData="currentTplData" :currentTplState.sync="currentTplState" />
        </a-form>
      </a-tab-pane>
      <a-tab-pane key="3" tab="状态流转" :disabled="disableTab">
        <a-form :form="form">
          <Transition :currentTplData="currentTplData" :currentTplState="currentTplState" />
        </a-form>
      </a-tab-pane>
    </a-tabs>
  </a-card>
</template>


<script>
import ticketFlowApi from "@/api/workflow.js"
import notification from 'ant-design-vue/es/notification'
import WorkflowTpl from './WorkflowTpl.vue'
import CustomField from './CustomField.vue'
import State from './State.vue'
import Transition from './Transition.vue'


export default {
  name: 'templateNew',
  components: {
    WorkflowTpl,
    CustomField,
    State,
    Transition
  },
  props: {
    pk: [Number, String]
  },
  data () {
    return {
      pushing: false,
      disableTab: true,
      activeKey: '1',
      form: this.$form.createForm(this),
      currentTplData: {
        "group": null,
      },
      currentTplState: [],
      tplKwarg: [], 
    }
  },
  beforeCreate() {
    this.form = this.$form.createForm(this, { name: 'dynamic_form_item' })
  },
  created() {
    this.fetchGroupData()
  },
  methods: {
    fetchGroupData() {
      ticketFlowApi.getWorkflowGroupDetail(this.pk).then(resp => {
        this.currentTplData["group"] = resp.data
      })
    },
    callback (key){
      this.activeKey = key
    }, 
    updateTplKwarg (data){
      this.tplKwarg = data
    },
    handlePushTpl (e) {
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
        ticketFlowApi.createWorkflowTpl(data).then(resp => {
          if (resp.code === "0000") {
            this.currentTplData = { ...resp.data }
            this.disableTab = false
            this.activeKey = '2'
            notification.info({
              message: '新建工作流程',
              description: "提交成功",
            })
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
