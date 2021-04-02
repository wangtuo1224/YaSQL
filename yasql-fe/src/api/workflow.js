import axios from '@/utils/request'

export default {
  getWorkflowGroup(params) {
    return axios.request({
      method: 'get',
      url: '/v1/workflow/list',
      params: params,
    })
  },
  getWorkflowSummary(params) {
    return axios.request({
      method: 'get',
      url: '/v1/workflow/list',
      params: params,
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
  getTicket(pk) {
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