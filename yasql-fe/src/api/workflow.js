import axios from '@/utils/request'

export default {
  getUserRole() {
    return axios.request({
      method: 'get',
      url: '/users/role',
    })
  },
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
  getWorkflowState(tpl) {
    return axios.request({
      method: 'get',
      url: `/v1/workflow/template/${tpl}/state`,
    })
  },
  createWorkflowState(data) {
    return axios.request({
      method: 'post',
      url: `/v1/workflow/state`,
      data: data,
    })
  },
  updateWorkflowState(pk, data) {
    return axios.request({
      method: 'put',
      url: `/v1/workflow/state/${pk}`,
      data: data,
    })
  },
  deleteWorkflowState(pk) {
    return axios.request({
      method: 'delete',
      url: `/v1/workflow/state/${pk}`,
    })
  },
  getWorkflowTransition(tpl) {
    return axios.request({
      method: 'get',
      url: `/v1/workflow/template/${tpl}/transition`,
    })
  },
  createWorkflowTransition(data) {
    return axios.request({
      method: 'post',
      url: `/v1/workflow/transition`,
      data: data,
    })
  },
  updateWorkflowTransition(pk, data) {
    return axios.request({
      method: 'put',
      url: `/v1/workflow/transition/${pk}`,
      data: data,
    })
  },
  deleteWorkflowTransition(pk) {
    return axios.request({
      method: 'delete',
      url: `/v1/workflow/transition/${pk}`,
    })
  },
  createTicket(data) {
    return axios.request({
      method: 'post',
      url: '/v1/workflow/ticket/new',
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
      url: `/v1/workflow/ticket/${pk}/detail`,
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