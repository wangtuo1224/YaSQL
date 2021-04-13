import axios from '@/utils/request'

export default {
  getWorkflowSummary(params) {
    return axios.request({
      method: 'get',
      url: '/v1/workflow/summary',
      params: params,
    })
  },
  getWorkflowGroup(params) {
    return axios.request({
      method: 'get',
      url: '/v1/workflow/group',
      params: params,
    })
  },
  getWorkflowGroupDetail(pk) {
    return axios.request({
      method: 'get',
      url: `/v1/workflow/group/${pk}`,
    })
  },
  createWorkflowGroup(data) {
    return axios.request({
      method: 'post',
      url: '/v1/workflow/group',
      data: data,
    })
  },
  updateWorkflowGroup(pk, data) {
    return axios.request({
      method: 'put',
      url: `/v1/workflow/group/${pk}`,
      data: data,
    })
  },
  getWorkflowTpl() {
    return axios.request({
      method: 'get',
      url: '/v1/workflow/template',
    })
  },
  createWorkflowTpl(data) {
    return axios.request({
      method: 'post',
      url: '/v1/workflow/template',
      data: data,
    })
  },
  updateWorkflowTpl(pk, data) {
    return axios.request({
      method: 'put',
      url: `/v1/workflow/template/${pk}`,
      data: data,
    })
  },
  getTicketTemplate(pk) {
    return axios.request({
      method: 'get',
      url: `/v1/workflow/template/${pk}`,
    })
  },
  createTicket(data) {
    return axios.request({
      method: 'post',
      url: '/v1/workflow/ticket',
      data: data,
    })
  },
  getTicketList(params) {
    return axios.request({
      method: 'get',
      url: '/v1/workflow/ticket',
      params: params,
    })
  },
  getTicketDetail(pk) {
    return axios.request({
      method: 'get',
      url: `/v1/workflow/ticket/${pk}`,
    })
  },
  getTicketLog(pk){
    return axios.request({
      method: 'get',
      url: `/v1/workflow/ticket/${pk}/log`,
    })
  },
  handleTicket(pk, data) {
    return axios.request({
      method: 'post',
      url: `/v1/workflow/ticket/${pk}/action`,
      data: data,
    })
  },
  uploadFile(formData) {
    return axios.request({
      method: 'post',
      url: '/v1/workflow/upload',
      processData: false,
      data: formData,
    })
  },
}