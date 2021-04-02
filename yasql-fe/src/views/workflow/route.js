const route = {
  name: 'workflow',
  path: '/workflow', 
  component: () => import('./index.vue'),
  redirect: { name: 'ticket.list' },
  meta: { title: '工单系统', icon: 'calendar' },
  children: [
    {
      name: 'ticket.summary',
      path: '/workflow/summary',
      component: () => import('./ticket/summary.vue'),
      meta: { title: '工单申请', icon: 'rocket' }
    },
    {
      name: 'ticket.new',
      path: '/workflow/ticket/:pk/new',
      hidden: true,
      component: () => import('./ticket/new.vue'),
      meta: { title: '创建工单', keepAlive: true, hidden: true }
    },
    {
      name: 'ticket.list',
      path: '/workflow/ticket/list',
      component: () => import('./ticket/list.vue'),
      meta: { title: '工单审批', icon: 'rocket' }
    },
    {
      name: 'ticket.detail',
      path: '/workflow/ticket/detail/:pk',
      hidden: true,
      component: () => import('./ticket/detail.vue'),
      meta: { title: '工单详情', keepAlive: true, hidden: true }
    },
    {
      name: 'workflow.group',
      path: '/workflow/group/list',
      component: () => import('./config/list.vue'),
      meta: { title: '工单配置', icon: 'flag' },
    },
    {
      name: 'workflow.group.update',
      path: '/workflow/group/update',
      hidden: true,
      component: () => import('./config/list.vue'),
      meta: { title: '更新工单组', keepAlive: true, hidden: true }
    },
    {
      name: 'workflow.template.new',
      path: '/workflow/group/:pk/new',
      hidden: true,
      component: () => import('./config/list.vue'),
      meta: { title: '修改工单', keepAlive: true, hidden: true }
    },
  ],
}
  
export default route